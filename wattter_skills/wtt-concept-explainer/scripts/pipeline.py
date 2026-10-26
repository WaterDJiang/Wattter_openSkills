#!/usr/bin/env python3
"""Code-animation v1: scaffold, compile a frame timeline, create speech, mix, verify."""
import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

# Allow direct script use and module-based unit checks.
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import asset_review

SCHEMA = 'code-animation/v1'


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def write(p, value):
    Path(p).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run(args, **kw):
    return subprocess.run([str(a) for a in args], check=True, **kw)


def probe(p):
    return json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(p)]))


def media_seconds(p):
    m = probe(p)
    if not any(s['codec_type'] == 'audio' for s in m['streams']):
        raise ValueError(f'音频文件没有音轨：{p}')
    return float(m['format']['duration'])


def number(n, label, minimum=0):
    if isinstance(n, bool) or not isinstance(n, (int, float)) or not math.isfinite(n) or n < minimum:
        raise ValueError(f'{label} 必须是 >= {minimum} 的有限数值')
    return n


def local(root, name):
    if not isinstance(name, str) or not name:
        raise ValueError('资源路径必须为非空字符串')
    p = (root / name).resolve()
    if not p.is_relative_to(root.resolve()):
        raise ValueError(f'资源必须位于项目内：{name}')
    return p


def config(root):
    c = read(root / 'film.json')
    if c.get('schema') != SCHEMA:
        raise ValueError(f'schema 应为 {SCHEMA}')
    for key in ('width', 'height', 'fps'):
        n = number(c.get(key), key, 1)
        if int(n) != n or (key != 'fps' and n % 2):
            raise ValueError(f'{key} 必须是正整数；视频尺寸须为偶数')
    if not isinstance(c.get('scenes'), list) or not c['scenes']:
        raise ValueError('scenes 不能为空')
    ids = set()
    for s in c['scenes']:
        sid = s.get('id', '')
        if not re.fullmatch(r'[a-z][a-z0-9-]*', sid) or sid in ids:
            raise ValueError(f'镜头 id 必须唯一且为 kebab-case：{sid}')
        ids.add(sid)
        number(s.get('visualSeconds'), f'{sid}.visualSeconds', .01)
        for key in ('leadSeconds', 'tailSeconds'):
            number(s.get(key, .3 if key == 'leadSeconds' else .6), f'{sid}.{key}')
        if not isinstance(s.get('narration', ''), str):
            raise ValueError(f'{sid}.narration 必须为字符串')
    return c


def speech_key(text, voice, rate):
    return hashlib.sha256(json.dumps([text, 'macos', voice, rate], ensure_ascii=False).encode()).hexdigest()


def caption_parts(text):
    # Character-weighted approximation, not forced alignment.
    pieces = []
    for sentence in re.split(r'(?<=[，。！？；,.!?;])', text):
        sentence = sentence.strip()
        while sentence:
            pieces.append(sentence[:22])
            sentence = sentence[22:]
    return pieces


def compile_rhythm(value, fps, total_frames, scenes):
    """Quantize absolute beat times once; never retime narration or infer beats from audio."""
    if not isinstance(value, dict): raise ValueError('rhythm 必须为对象')
    allowed = {'bpm', 'offsetSeconds', 'beatTimesSeconds', 'beatsPerBar', 'basis', 'audioFile', 'events'}
    if set(value) - allowed: raise ValueError('rhythm 含未知字段')
    if ('bpm' in value) == ('beatTimesSeconds' in value):
        raise ValueError('rhythm 只选 bpm 或 beatTimesSeconds 一种节拍来源')
    basis = value.get('basis', '')
    if not isinstance(basis, str) or not basis.strip(): raise ValueError('rhythm.basis 须说明节拍来源与核对依据')
    per_bar = value.get('beatsPerBar', 4)
    if type(per_bar) is not int or per_bar < 1: raise ValueError('beatsPerBar 须为正整数')
    def quantize(t): return math.floor(t * fps + Fraction(1, 2))
    if 'bpm' in value:
        bpm = number(value['bpm'], 'rhythm.bpm', .01)
        if bpm > fps * 60: raise ValueError('拍点间隔小于一帧，无法表示')
        offset = Fraction(str(number(value.get('offsetSeconds', 0), 'rhythm.offsetSeconds')))
        step = Fraction(60) / Fraction(str(bpm))
        times = []
        i = 0
        while quantize(offset + step * i) < total_frames:
            times.append(offset + step * i); i += 1
    else:
        if 'offsetSeconds' in value: raise ValueError('beatTimesSeconds 已是全片绝对时间，不再叠加 offsetSeconds')
        raw = value['beatTimesSeconds']
        if not isinstance(raw, list) or not raw: raise ValueError('beatTimesSeconds 不能为空')
        times = [Fraction(str(number(t, 'beatTimesSeconds'))) for t in raw]
        if any(a >= b for a, b in zip(times, times[1:])): raise ValueError('拍点必须严格递增')
    if not times: raise ValueError('片内没有有效拍点')
    frames = [quantize(t) for t in times]
    if any(f >= total_frames for f in frames): raise ValueError('拍点超出片尾半开区间')
    if len(set(frames)) != len(frames): raise ValueError('多个拍点量化到同一帧，请调整节拍网格或帧率')
    beats = [{'beat': i, 'frame': f, 'seconds': f / fps, 'bar': i // per_bar,
              'beatInBar': i % per_bar} for i, f in enumerate(frames)]
    events, ids = [], set()
    raw_events = value.get('events', [])
    if not isinstance(raw_events, list): raise ValueError('rhythm.events 须为数组')
    for event in raw_events:
        if not isinstance(event, dict) or set(event) - {'id', 'beat', 'action', 'sceneId'}:
            raise ValueError('rhythm.events 字段仅 id/beat/action/sceneId')
        eid, beat, action = event.get('id'), event.get('beat'), event.get('action')
        if not isinstance(eid, str) or not re.fullmatch(r'[a-z][a-z0-9-]*', eid) or eid in ids:
            raise ValueError('节奏事件 id 必须唯一且为 kebab-case')
        ids.add(eid)
        if type(beat) is not int or not 0 <= beat < len(beats): raise ValueError('事件 beat 越界，拍号从 0 开始')
        if not isinstance(action, str) or not action.strip(): raise ValueError('节奏事件 action 不能为空')
        frame = frames[beat]
        scene = next(s for s in scenes if s['startFrame'] <= frame < s['endFrame'])
        if 'sceneId' in event and event['sceneId'] != scene['id']:
            raise ValueError(f'节奏事件 {eid} 不在声明的 sceneId 内；旁白或镜头时长可能已变化')
        events.append(dict(event, frame=frame, seconds=frame / fps, sceneId=scene['id']))
    return {'basis': basis, 'audioFile': value.get('audioFile'), 'beatsPerBar': per_bar,
            'beats': beats, 'events': events}


def compile_timeline(root, lock=False):
    c = config(root)
    fps, cursor, shots, captions, assets = c['fps'], 0, [], [], {}
    rate = number(c.get('speechCharsPerSecond', 3.8), 'speechCharsPerSecond', .1)
    for s in c['scenes']:
        sid, text = s['id'], s.get('narration', '').strip()
        lead = math.ceil(s.get('leadSeconds', .3) * fps)
        tail = math.ceil(s.get('tailSeconds', .6) * fps)
        voice, voice_frames = None, 0
        if text:
            voice = s.get('voice', f'audio/{sid}.wav')
            path = local(root, voice)
            if lock:
                if not path.is_file():
                    raise ValueError(f'{sid} 缺少旁白 {voice}；先生成或提供音频，禁止静默导出无声版')
                cache = path.with_suffix(path.suffix + '.json')
                if cache.exists():
                    record = read(cache)
                    if record.get('text') != text or record.get('audioSha256') != digest(path):
                        raise ValueError(f'{sid} 旁白缓存与台词/音频不符；重新生成或重新登记外部音频')
                elif not s.get('externalVoiceVerified', False):
                    raise ValueError(f'{sid} 外部音频需核对台词后设置 externalVoiceVerified=true')
                duration = media_seconds(path)
                assets[voice] = digest(path)
            else:
                duration = len(re.sub(r'\s', '', text)) / rate
            voice_frames = math.ceil(duration * fps)
        frames = max(math.ceil(s['visualSeconds'] * fps), lead + voice_frames + tail)
        item = dict(s, startFrame=cursor, durationFrames=frames, endFrame=cursor + frames,
                    voiceStartFrame=cursor + lead, voiceFrames=voice_frames, voice=voice)
        shots.append(item)
        parts = caption_parts(text)
        total = sum(map(len, parts))
        offset = 0
        for part in parts:
            start = cursor + lead + round(voice_frames * offset / total)
            offset += len(part)
            end = cursor + lead + round(voice_frames * offset / total)
            if end > start:
                captions.append({'text': part, 'startFrame': start, 'endFrame': end})
        cursor += frames
    duration = cursor / fps
    if c.get('maxSeconds') is not None and duration > number(c['maxSeconds'], 'maxSeconds', .01) + 1 / fps:
        raise ValueError(f'内容需要 {duration:.3f}s，超过 maxSeconds={c["maxSeconds"]}；修改剧本或时长约束，不能裁切语音')
    rhythm = compile_rhythm(c['rhythm'], fps, cursor, shots) if 'rhythm' in c else None
    tracks = [dict(track) for track in c.get('audioTracks', [])]
    if rhythm and rhythm['audioFile'] is not None and rhythm['audioFile'] not in [t['file'] for t in tracks]:
        raise ValueError('rhythm.audioFile 必须引用本片 audioTracks 中的音频，沿素材锁校验')
    for track in tracks:
        if 'startBeat' in track:
            beat = track.pop('startBeat')
            if 'startSeconds' in track: raise ValueError('startBeat 与 startSeconds 不能同时指定')
            if not rhythm or type(beat) is not int or not 0 <= beat < len(rhythm['beats']):
                raise ValueError('startBeat 需要有效节拍网格及片内整数拍号')
            track['startSeconds'] = rhythm['beats'][beat]['frame'] / fps
        path = local(root, track['file'])
        start = number(track.get('startSeconds', 0), 'audioTracks.startSeconds')
        number(track.get('gain', .2), 'audioTracks.gain')
        if lock:
            if not path.is_file():
                raise ValueError(f'缺少音频素材：{path}')
            if start + media_seconds(path) > duration + 1 / fps:
                raise ValueError(f'音频素材越过片尾：{path.name}；先在源素材中编辑长度')
            assets[track['file']] = digest(path)
    timeline = {'schema': SCHEMA, 'locked': lock, 'filmSha256': digest(root / 'film.json'),
                'assetSha256': assets, 'title': c.get('title', ''), 'width': c['width'], 'height': c['height'],
                'fps': fps, 'totalFrames': cursor, 'durationSeconds': duration,
                'seed': c.get('seed', 42), 'scenes': shots, 'captions': captions,
                'captionTiming': 'character-weighted-approximation', 'audioTracks': tracks,
                'assetReview': asset_review.guard_if_locked(root)}
    if rhythm is not None: timeline['rhythm'] = rhythm
    if 'loop' in c:
        if type(c['loop']) is not bool: raise ValueError('loop 须为布尔值；它只请求首尾接缝审查')
        timeline['loop'] = c['loop']
    return timeline


def locked(root):
    receipt = asset_review.require(root)
    t = read(root / 'timeline.json')
    if t.get('assetReview') != receipt:
        raise ValueError('时间轴未绑定当前素材版本；先重新锁时')
    if not t.get('locked'):
        raise ValueError('时间轴尚未锁定：执行 pipeline.py timeline 项目 --lock')
    if t != compile_timeline(root, lock=True):
        raise ValueError('时间轴已过期：film.json 或音频变化，重新锁定并渲染')
    return t


def tts(root, voice, rate):
    asset_review.guard_if_locked(root)
    c = config(root)
    for s in c['scenes']:
        text = s.get('narration', '').strip()
        if not text:
            continue
        path = local(root, s.get('voice', f'audio/{s["id"]}.wav'))
        if s.get('externalVoiceVerified'):
            if not path.is_file():
                raise ValueError(f'外部语音缺失：{path}')
            print(f'保留已核对的外部语音：{path.name}')
            continue
        key = speech_key(text, voice, rate)
        record = path.with_suffix(path.suffix + '.json')
        if path.exists() and record.exists() and read(record).get('key') == key and read(record).get('audioSha256') == digest(path):
            print(f'复用：{path.name}')
            continue
        asset_review.protect_output(root, path)
        if sys.platform != 'darwin' or not shutil.which('say'):
            raise ValueError('本机不支持 macOS say；使用可用 TTS 或用户音频，并按契约登记外部语音')
        path.parent.mkdir(parents=True, exist_ok=True)
        src = path.with_suffix('.tts.aiff')
        temp = path.with_name(path.stem + '.new' + path.suffix)
        run(['say', '-v', voice, '-r', rate, '-o', src, text])
        run(['ffmpeg', '-y', '-v', 'error', '-i', src, '-ar', '48000', '-ac', '1', temp])
        temp.replace(path)
        write(record, {'key': key, 'text': text, 'voice': voice, 'rate': rate, 'audioSha256': digest(path)})
        src.unlink()
        print(f'生成：{path.name}')


def default_tts(root, system_voice=None, rate=None, voice_config=None, voice_id=None):
    asset_review.guard_if_locked(root)
    if system_voice is not None:
        if voice_config is not None or voice_id is not None:
            raise ValueError('--voice 为系统音色，不能与 --voice-config/--voice-id 同时使用')
        return tts(root, system_voice, rate if rate is not None else 205)
    import voice as voice_tools
    chosen = voice_tools.discover_config(root, voice_config)
    if chosen is None:
        if voice_id is not None:
            raise ValueError('指定了克隆音色，但未发现声音配置')
        return tts(root, 'Tingting', rate if rate is not None else 205)
    if rate is not None:
        raise ValueError('--rate 仅适用于 macOS 系统配音；已配置克隆音色不支持此参数')
    selected = voice_tools.load_config(chosen, voice_id)
    print(f'使用已配置音色：{selected["voiceId"]}（{chosen}）', flush=True)
    interpreter = chosen.parent / '.venv/bin/python'
    if not interpreter.is_file():
        interpreter = Path(sys.executable)
    run([interpreter, Path(__file__).with_name('voice.py'), 'synthesize',
         '--config', chosen, '--voice', selected['voiceId'], '--project', root])


def mix(root):
    t = locked(root)
    duration = t['durationSeconds']
    samples = round(t['totalFrames'] * 48000 / t['fps'])
    out = root / 'audio'
    out.mkdir(exist_ok=True)
    args = ['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo']
    tracks = [(s['voice'], s['voiceStartFrame'] / t['fps'], 1.0) for s in t['scenes'] if s['voice']]
    tracks += [(s['file'], s.get('startSeconds', 0), s.get('gain', .2)) for s in t['audioTracks']]
    asset_review.registered(root, [str(file) for file, _, _ in tracks])
    filters, labels = [], ['[0:a]']
    for i, (file, start, gain) in enumerate(tracks, 1):
        args += ['-i', local(root, file)]
        filters.append(f'[{i}:a]aresample=48000,aformat=channel_layouts=stereo,volume={gain},adelay={round(start * 48000)}S:all=1[a{i}]')
        labels.append(f'[a{i}]')
    # Sources are validated before trim. loudnorm/resampling may shorten fractional-frame tails;
    # restore exact timeline length after processing without relaxing delivery validation.
    filters.append(''.join(labels) + f'amix=inputs={len(labels)}:duration=first:normalize=0,atrim=duration={duration},loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000,asetpts=N/SR/TB,apad=whole_len={samples},atrim=end_sample={samples},asetpts=N/SR/TB[out]')
    filter_path = out / 'mix-filter.txt'
    filter_path.write_text(';\n'.join(filters))
    run(args + ['-filter_complex_script', filter_path, '-map', '[out]', out / 'mix-master.wav'])
    receipt = asset_review.require(root)
    write(out / 'mix-report.json', {'assetReview': receipt, 'timelineSha256': digest(root / 'timeline.json'),
          'mixSha256': digest(out / 'mix-master.wav'), 'durationSeconds': duration, 'tracks': len(tracks)})


def check_mix(root):
    report = read(root / 'audio/mix-report.json')
    if report.get('assetReview') != asset_review.require(root):
        raise ValueError('混音素材版本已过期')
    if report['timelineSha256'] != digest(root / 'timeline.json') or report['mixSha256'] != digest(root / 'audio/mix-master.wav'):
        raise ValueError('混音已过期，重新执行 mix')


def check_render(root):
    t = locked(root)
    check_mix(root)
    r = read(root / 'render-report.json')
    if r.get('assetReview') != t['assetReview']:
        raise ValueError('渲染素材版本已过期；不能验收旧版本')
    if r.get('mode') != 'render' or r['timelineSha256'] != digest(root / 'timeline.json') or r['videoSha256'] != digest(root / 'silent.mp4'):
        raise ValueError('画面已过期，重新执行 render')
    for name, expected in r.get('sourceSha256', {}).items():
        if digest(local(root, name)) != expected:
            raise ValueError(f'渲染源文件已变化：{name}；重新执行 render')
    return t


def finish(root):
    t = check_render(root)
    run(['ffmpeg', '-y', '-v', 'error', '-i', root / 'silent.mp4', '-i', root / 'audio/mix-master.wav',
         '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
         '-movflags', '+faststart', root / 'final.mp4'])
    asset_review.require(root)
    write(root / 'finalization.json', {'assetReview': t['assetReview'],
          'finalSha256': digest(root / 'final.mp4'), 'renderReportSha256': digest(root / 'render-report.json'),
          'mixReportSha256': digest(root / 'audio/mix-report.json')})
    validate(root)


def validate(root):
    t = check_render(root)
    finalization = read(root / 'finalization.json')
    expected_receipt = {'assetReview': t['assetReview'], 'finalSha256': digest(root / 'final.mp4'),
        'renderReportSha256': digest(root / 'render-report.json'), 'mixReportSha256': digest(root / 'audio/mix-report.json')}
    if finalization != expected_receipt:
        raise ValueError('成片未绑定当前素材、画面和混音；重新 finish，不能重写哈希报告跳过')
    file = root / 'final.mp4'
    m = probe(file)
    video = next(s for s in m['streams'] if s['codec_type'] == 'video')
    audio = next(s for s in m['streams'] if s['codec_type'] == 'audio')
    expected = (t['width'], t['height'], str(t['totalFrames']), 'h264')
    actual = (video['width'], video['height'], video.get('nb_frames'), video['codec_name'])
    if actual != expected or video['avg_frame_rate'] != f'{t["fps"]}/1' or audio['codec_name'] != 'aac':
        raise ValueError(f'成片媒体参数不符：{actual} / {expected}')
    for stream in (video, audio):
        if abs(float(stream['duration']) - t['durationSeconds']) > max(1 / t['fps'], .05):
            raise ValueError('音画时长不闭合')
    decoded = run(['ffmpeg', '-v', 'error', '-i', file, '-f', 'null', '-'], capture_output=True, text=True)
    if decoded.stderr.strip():
        raise ValueError(f'解码错误：{decoded.stderr}')
    peaks = run(['ffmpeg', '-hide_banner', '-i', file, '-vn', '-af', 'volumedetect', '-f', 'null', '-'], capture_output=True, text=True)
    match = re.search(r'max_volume: ([-\d.]+) dB', peaks.stderr)
    peak = float(match[1]) if match else None
    if peak is not None and peak >= 0:
        raise ValueError('音频达到 0 dBFS；降低母带峰值后重混')
    asset_review.require(root)
    write(root / 'media-info.json', m)
    write(root / 'delivery-check.json', {'passed': True, 'assetReview': t['assetReview'], 'durationSeconds': t['durationSeconds'],
          'totalFrames': t['totalFrames'], 'decodeErrors': [], 'samplePeakDbfs': peak,
          'finalSha256': digest(file), 'timelineSha256': digest(root / 'timeline.json'),
          'visualReview': 'pending-human-or-agent-image-inspection', 'userAcceptance': 'pending'})
    print(f'技术检查通过：{file} · {t["totalFrames"]} 帧 / {t["durationSeconds"]:.3f}s')


# Review is separate from codec validation: these tools collect evidence, not aesthetic judgments.
REVIEW_CHECKS = ('readability', 'motion', 'focus', 'transitions', 'encoded')


def review_plan(t):
    groups = []
    for scene in t['scenes']:
        key = str(scene.get('director', {}).get('group', scene['id']))
        if not groups or groups[-1]['label'] != key:
            groups.append({'id': f'shot-{len(groups)+1:03d}', 'label': key,
                           'startFrame': scene['startFrame'], 'endFrame': scene['endFrame'], 'anchors': []})
        group = groups[-1]
        group['endFrame'] = scene['endFrame']
        offset = scene.get('director', {}).get('reviewAtSeconds')
        if offset is not None:
            frame = scene['startFrame'] + round(number(offset, 'director.reviewAtSeconds') * t['fps'])
            if frame >= scene['endFrame']:
                raise ValueError(f'{scene["id"]} reviewAtSeconds 超出该段；按锁定时间轴修正')
            group['anchors'].append(frame)
    for g in groups:
        a, b = g['startFrame'], g['endFrame']
        frames = {a, (a+b-1)//2, b-1}
        captions = [c for c in t['captions'] if a <= c['startFrame'] < b]
        if captions:
            longest = max(captions, key=lambda c: len(c['text']))
            frames.add((longest['startFrame']+longest['endFrame']-1)//2)
        g['frames'] = sorted(frames)
        if not g['anchors']:
            g['anchors'] = [max(a, (a+b)//2-t['fps'])]
        g['windows'] = [{'startFrame': f, 'endFrame': min(b, f+2*t['fps'])} for f in g.pop('anchors')]
    return groups


def review_init(root):
    target = root / 'visual-review.json'
    if target.exists():
        raise ValueError('visual-review.json 已存在；保留旧记录后再生成，不覆盖审阅结论')
    validate(root)
    t = read(root / 'timeline.json')
    groups = review_plan(t)
    final_hash = digest(root / 'final.mp4')
    folder = root / 'quality-review' / final_hash[:12]
    folder.mkdir(parents=True, exist_ok=True)
    widths = [640, 960] if t['width'] >= t['height'] else [360, 640]
    widths = sorted(set(min(w, t['width']) for w in widths))
    evidence = []
    def record(file, group, kind, **fields):
        evidence.append(dict(id=file.stem, groupId=group['id'], kind=kind,
                             file=str(file.relative_to(root)), sha256=digest(file), **fields))
    for group in groups:
        for frame in group['frames']:
            name = f'{group["id"]}-f{frame:06d}'
            original = folder / f'{name}-original.png'
            run(['ffmpeg', '-y', '-v', 'error', '-ss', frame/t['fps'], '-i', root/'final.mp4',
                 '-frames:v', '1', original])
            record(original, group, 'image', frame=frame, width=t['width'])
            for width in widths:
                file = folder / f'{name}-w{width}.png'
                run(['ffmpeg', '-y', '-v', 'error', '-i', original, '-vf', f'scale={width}:-2', '-frames:v', '1', file])
                record(file, group, 'image', frame=frame, width=width)
        for i, window in enumerate(group['windows']):
            file = folder / f'{group["id"]}-motion-{i+1:02d}.mp4'
            run(['ffmpeg', '-y', '-v', 'error', '-ss', window['startFrame']/t['fps'], '-i', root/'final.mp4',
                 '-t', (window['endFrame']-window['startFrame'])/t['fps'], '-vf', f'scale={widths[0]}:-2',
                 '-c:v', 'libx264', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-movflags', '+faststart', file])
            record(file, group, 'clip', **window)
    manifest = folder/'evidence.json'
    write(manifest, {'finalSha256': final_hash, 'timelineSha256': digest(root/'timeline.json'),
                     'previewWidths': widths, 'groups': groups, 'evidence': evidence})
    write(target, {'schema': 'concept-video-review/v1', 'finalSha256': final_hash,
                   'timelineSha256': digest(root/'timeline.json'), 'evidenceFile': str(manifest.relative_to(root)),
                   'evidenceSha256': digest(manifest), 'reviewer': {'name': '', 'method': ''},
                   'checks': {key: {'status': 'pending', 'notes': '', 'evidenceIds': []} for key in REVIEW_CHECKS},
                   'audioReview': {'status': 'not_checked', 'notes': ''}, 'userAcceptance': 'pending'})
    print(f'已生成{len(groups)}镜证据：{folder}；实际审阅后填写 {target.name}，尚未视觉通过')


def check_visual_review(root, t):
    r = read(root/'visual-review.json')
    if r.get('schema') != 'concept-video-review/v1':
        raise ValueError('视觉记录格式不符；执行 review-init 生成待审记录')
    for key, file in [('finalSha256','final.mp4'), ('timelineSha256','timeline.json')]:
        if r.get(key) != digest(root/file):
            raise ValueError('视觉记录已过期：成片或时间轴变化，重新生成证据并审阅')
    manifest_file = local(root, r.get('evidenceFile'))
    if digest(manifest_file) != r.get('evidenceSha256'):
        raise ValueError('视觉证据清单已变化；重新生成证据并审阅')
    manifest = read(manifest_file)
    if manifest.get('finalSha256') != r['finalSha256'] or manifest.get('timelineSha256') != r['timelineSha256'] or manifest.get('groups') != review_plan(t):
        raise ValueError('视觉证据与当前成片/镜头不一致')
    items = manifest.get('evidence', [])
    ids = {e['id']: e for e in items}
    if not items or len(ids) != len(items):
        raise ValueError('视觉证据缺失或ID重复')
    for e in items:
        if digest(local(root, e['file'])) != e['sha256']:
            raise ValueError(f'视觉证据已变化：{e["file"]}')
    reviewer = r.get('reviewer', {})
    if not all(isinstance(reviewer.get(k),str) and reviewer[k].strip() for k in ('name','method')):
        raise ValueError('填写实际审阅者及查看方式，不能自动记为已审阅')
    groups = {g['id'] for g in manifest['groups']}
    minimum_width = min(manifest['previewWidths'])
    for key in REVIEW_CHECKS:
        check = r.get('checks', {}).get(key, {})
        refs = check.get('evidenceIds', [])
        if check.get('status') != 'pass' or not isinstance(check.get('notes'),str) or not check['notes'].strip():
            raise ValueError(f'{key} 未通过或缺少具体观察记录')
        if not isinstance(refs,list) or not refs or any(ref not in ids for ref in refs):
            raise ValueError(f'{key} 缺少有效证据ID')
        selected = [ids[ref] for ref in refs]
        if key == 'motion': selected = [e for e in selected if e['kind'] == 'clip']
        if key == 'readability': selected = [e for e in selected if e['kind'] == 'image' and e['width'] <= minimum_width]
        if {e['groupId'] for e in selected} != groups:
            raise ValueError(f'{key} 证据未覆盖全部大镜（readability须最小尺寸图，motion须连续片段）')
        if key in ('readability', 'encoded', 'transitions'):
            required = {(g['id'], f) for g in manifest['groups'] for f in
                        ([g['startFrame'], g['endFrame']-1] if key == 'transitions' else g['frames'])}
            covered = {(e['groupId'], e.get('frame')) for e in selected if e['kind'] == 'image'}
            if not required <= covered:
                raise ValueError(f'{key} 缺少所需首中尾/字幕帧证据')
        if key == 'motion':
            required = {(g['id'], w['startFrame'], w['endFrame']) for g in manifest['groups'] for w in g['windows']}
            covered = {(e['groupId'], e.get('startFrame'), e.get('endFrame')) for e in selected}
            if not required <= covered:
                raise ValueError('motion 缺少动作窗口证据')
    audio = r.get('audioReview', {})
    if audio.get('status') not in ('not_checked','pass'):
        raise ValueError('声音试听记录无效或存在待修问题')
    if audio.get('status') == 'pass' and not str(audio.get('notes','')).strip():
        raise ValueError('声音试听通过须填写实际记录')
    return {'schema': 'concept-video-review-check/v1', 'passed': True,
            'scope': '记录完整性与文件绑定；不自动评判视觉质量或用户认可',
            'finalSha256': r['finalSha256'], 'reviewSha256': digest(root/'visual-review.json'),
            'audioReview': audio, 'userAcceptance': r.get('userAcceptance','pending')}


def review(root):
    # A failed/stale rerun must not leave an earlier successful receipt beside it.
    output = root/'visual-review-check.json'
    output.unlink(missing_ok=True)
    validate(root)
    result = check_visual_review(root, read(root/'timeline.json'))
    write(output, result)
    print('视觉检查记录完整且绑定当前成片；主观试听/用户认可状态见独立字段')


def init(root):
    if root.exists() and any(root.iterdir()):
        raise ValueError('初始化目录须为空，避免覆盖已有制作文件')
    base = Path(__file__).resolve().parent.parent
    shutil.copytree(base / 'assets/starter', root, dirs_exist_ok=True)
    target = root / 'tools'
    target.mkdir()
    for name in ('pipeline.py', 'render.cjs', 'voice.py', 'asset_review.py'):
        shutil.copy2(base / 'scripts' / name, target / name)
    (root / 'config').mkdir()
    for name in ('model-catalog.json', 'voice.example.json'):
        shutil.copy2(base / 'config' / name, root / 'config' / name)
    shutil.copy2(base / 'requirements-voice.txt', root / 'requirements-voice.txt')
    shutil.copy2(base / 'references/voice.md', root / 'VOICE.md')
    shutil.copy2(base / 'references/material-review.md', root / 'ASSETS.md')
    shutil.copy2(base / 'references/video-quality.md', root / 'QUALITY.md')
    shutil.copy2(base / '.gitignore', root / '.gitignore')
    print(f'已创建起步项目：{root}；先按用户内容改 film.json 和 scenes.js')
    import voice as voice_tools
    report = voice_tools.doctor(root)
    print('声音首次检查：' + report['nextStep'])
    for issue in report['issues']:
        print('提醒：' + issue)
    if report['issues']:
        print('可先继续剧本和画面；普通配音沿用系统/外部路线。已指定个人音色时，合成前须补齐配置。')



def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['init', 'timeline', 'tts', 'mix', 'check', 'finish', 'validate', 'review-init', 'review'])
    p.add_argument('project', type=Path)
    p.add_argument('--lock', action='store_true')
    p.add_argument('--voice', help='显式使用 macOS 系统音色，覆盖已配置的个人音色')
    p.add_argument('--rate', type=int, help='macOS say 语速，缺省 205')
    p.add_argument('--voice-config', type=Path, help='覆盖自动发现的声音配置')
    p.add_argument('--voice-id', help='覆盖配置中的 defaultVoice')
    a = p.parse_args()
    root = a.project.resolve()
    if a.command == 'init': init(root)
    elif a.command == 'timeline':
        if a.lock:
            asset_review.require(root)
            c = config(root)
            media = [s.get('voice', f'audio/{s["id"]}.wav') for s in c['scenes'] if s.get('narration', '').strip()]
            media += [t['file'] for t in c.get('audioTracks', [])]
            asset_review.registered(root, media)
        else:
            asset_review.guard_if_locked(root)
        t = compile_timeline(root, a.lock)
        write(root / 'timeline.json', t)
        print(f'{"已锁定" if a.lock else "估时预览"}：{t["totalFrames"]} 帧 / {t["durationSeconds"]:.3f}s')
    elif a.command == 'tts': default_tts(root, a.voice, a.rate, a.voice_config, a.voice_id)
    elif a.command == 'mix': mix(root)
    elif a.command == 'check': locked(root)
    elif a.command == 'finish': finish(root)
    elif a.command == 'validate': validate(root)
    elif a.command == 'review-init': review_init(root)
    elif a.command == 'review': review(root)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(1)
