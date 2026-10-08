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
    for track in c.get('audioTracks', []):
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
                'captionTiming': 'character-weighted-approximation', 'audioTracks': c.get('audioTracks', []),
                'assetReview': asset_review.guard_if_locked(root)}
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
    # Sources are validated before trim; trim removes only silence beyond the frame timeline.
    filters.append(''.join(labels) + f'amix=inputs={len(labels)}:duration=first:normalize=0,atrim=duration={duration},loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000[out]')
    filter_path = out / 'mix-filter.txt'
    filter_path.write_text(';\n'.join(filters))
    run(args + ['-filter_complex_script', filter_path, '-map', '[out]', '-t', duration, out / 'mix-master.wav'])
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
    p.add_argument('command', choices=['init', 'timeline', 'tts', 'mix', 'check', 'finish', 'validate'])
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


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(1)
