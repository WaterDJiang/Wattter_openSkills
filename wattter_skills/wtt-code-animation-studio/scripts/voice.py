#!/usr/bin/env python3
"""检索模型、本地音色配置与离线配音；下载是独立显式命令。"""
import argparse
import hashlib
import json
import math
import os
import platform
import re
import subprocess
import sys
import time
from pathlib import Path

CATALOG = Path(__file__).resolve().parents[1] / 'config/model-catalog.json'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        while chunk := f.read(8 * 1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def catalog(model_id=None):
    models = read(CATALOG)['models']
    if model_id is None:
        return models
    for model in models:
        if model['id'] == model_id:
            return model
    raise ValueError(f'未知模型：{model_id}；先运行 catalog')


def resolve(base, value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('配置路径必须是非空本地路径')
    if '://' in value:
        raise ValueError('配置仅接受本地路径，不接受 URL')
    return (base / Path(value).expanduser()).resolve()


def within(root, value):
    path = resolve(root, value)
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f'文件必须位于指定目录内：{value}')
    return path


def load_config(path, voice_id=None):
    path = Path(path).resolve()
    c = read(path)
    if c.get('schema') != 'code-animation-voice/v1':
        raise ValueError('声音配置 schema 应为 code-animation-voice/v1')
    voice_id = voice_id or c.get('defaultVoice')
    if voice_id not in c.get('voices', {}):
        raise ValueError(f'未配置音色：{voice_id}')
    voice = c['voices'][voice_id]
    model = catalog(voice['model'])
    if model['engine'] != 'qwen3-tts-mlx':
        raise ValueError('该模型不是已接入的 Qwen3-TTS MLX 克隆模型')
    location = c.get('models', {}).get(model['id'])
    if not location:
        raise ValueError(f'没有配置模型路径：{model["id"]}')
    if voice.get('referenceTextVerified') is not True:
        raise ValueError('先核对参考录音与文字，再设置 referenceTextVerified=true')
    allowed_voice = {'label', 'model', 'referenceAudio', 'referenceTextFile', 'referenceTextVerified', 'language'}
    if set(voice) - allowed_voice:
        raise ValueError(f'不支持的音色字段：{sorted(set(voice)-allowed_voice)}')
    settings = {'seed': 42, 'temperature': .7, 'maxTokens': 1200} | c.get('generation', {})
    if set(settings) != {'seed', 'temperature', 'maxTokens'}:
        raise ValueError('generation 只支持 seed、temperature、maxTokens；不支持 speed/instruct')
    if type(settings['seed']) is not int or not 0 <= settings['seed'] < 2**32:
        raise ValueError('seed 必须为 0 至 2^32-1 的整数')
    if type(settings['maxTokens']) is not int or not 16 <= settings['maxTokens'] <= 4096:
        raise ValueError('maxTokens 必须为 16 至 4096 的整数')
    temp = settings['temperature']
    if type(temp) not in (float, int) or not math.isfinite(temp) or not 0 < temp <= 2:
        raise ValueError('temperature 必须在 (0, 2] 内')
    language = voice.get('language', 'chinese')
    if language not in ('auto', 'chinese', 'english', 'japanese', 'korean', 'german',
                        'french', 'russian', 'portuguese', 'spanish', 'italian'):
        raise ValueError('不支持的 language；使用模型支持的完整英文语言名')
    return {'voiceId': voice_id, 'model': model, 'settings': settings, 'language': language,
            'modelPath': resolve(path.parent, location['path']),
            'manifestPath': resolve(path.parent, location['manifest']),
            'referenceAudio': resolve(path.parent, voice['referenceAudio']),
            'referenceTextFile': resolve(path.parent, voice['referenceTextFile'])}


def discover_config(project=None, explicit=None):
    """Resolve one config by priority; never skip an invalid higher-priority choice."""
    selected = explicit if explicit is not None else os.environ.get('CODE_ANIMATION_VOICE_CONFIG')
    if selected is not None:
        if not str(selected).strip():
            raise ValueError('指定的声音配置路径为空')
        path = Path(selected).expanduser().resolve()
        if not path.is_file():
            raise ValueError(f'指定的声音配置不存在或不是文件：{path}')
        return path
    for path in (Path(project or Path.cwd()).resolve() / '.voice-local/voice.local.json',
                 Path.home() / '.config/wtt-code-animation-studio/voice.local.json'):
        if path.exists() or path.is_symlink():
            if not path.is_file():
                raise ValueError(f'声音配置不可读取：{path}')
            return path.resolve()
    return None


def required_config(project=None, explicit=None):
    path = discover_config(project, explicit)
    if path is None:
        raise ValueError('未发现声音配置；先配置项目/用户默认音色，或传入 --config')
    return path


def verify_model(directory, manifest_path, entry, *, hash_files=True):
    manifest = read(manifest_path)
    if manifest.get('repo') != entry['repo'] or manifest.get('revision') != entry['revision']:
        raise ValueError('模型清单与目录中固定的 repo/revision 不一致')
    files = manifest.get('files', [])
    if not files or len({f['file'] for f in files}) != len(files):
        raise ValueError('模型清单为空或有重复文件')
    names = {f['file'] for f in files}
    for required in ('config.json', 'tokenizer_config.json', 'speech_tokenizer/config.json'):
        if required not in names:
            raise ValueError(f'模型清单缺少必要文件：{required}')
    if not any(n.endswith('.safetensors') and not n.startswith('speech_tokenizer/') for n in names):
        raise ValueError('模型清单缺少主权重')
    if not any(n.startswith('speech_tokenizer/') and n.endswith('.safetensors') for n in names):
        raise ValueError('模型清单缺少参考音频编解码权重')
    for item in files:
        file = within(directory, item['file'])
        if not file.is_file() or file.stat().st_size != item['bytes'] or (hash_files and sha(file) != item['sha256']):
            raise ValueError(f'模型文件缺失或哈希不匹配：{item["file"]}')
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob('*')
              if p.is_file() and '.cache' not in p.relative_to(directory).parts
              and p.resolve() != Path(manifest_path).resolve()}
    if actual != names:
        raise ValueError('模型目录含清单之外的文件；使用干净的固定版本目录')
    return len(files)


def doctor(project=None, explicit=None):
    """Read-only onboarding: existence/size checks, no model loading or hash certification."""
    result = {'status': 'needs-setup', 'config': None, 'defaultVoice': None,
              'modelFilesPresent': False, 'customVoiceFilesPresent': False,
              'referenceTextVerified': False, 'fullValidation': 'not-run', 'issues': [],
              'nextStep': '按 README / VOICE.md 配置模型、参考录音与逐字文本，再运行 voice.py check；不自动下载或写配置。'}
    issues = result['issues']
    try:
        path = discover_config(project, explicit)
        if path is None:
            result['status'] = 'missing-config'
            issues.append('尚未发现 voice.local.json；公开 voice.example.json 只是模板，不代表已安装模型或个人音色。')
            return result
        result['config'] = str(path)
        data = read(path)
        if not isinstance(data, dict) or data.get('schema') != 'code-animation-voice/v1':
            raise ValueError('声音配置 schema 应为 code-animation-voice/v1')
        voices, models = data.get('voices', {}), data.get('models', {})
        if not isinstance(voices, dict) or not isinstance(models, dict):
            raise ValueError('voices 和 models 必须是配置对象')
        vid = data.get('defaultVoice'); result['defaultVoice'] = vid
        voice = voices.get(vid) if isinstance(vid, str) else None
        if not isinstance(voice, dict):
            raise ValueError('没有有效的 defaultVoice 个人音色；填写 voices 并指定默认音色')
        try:
            entry = catalog(voice.get('model'))
            if not isinstance(entry, dict): raise ValueError('个人音色未指定模型 ID')
            location = models.get(entry['id'])
            if not isinstance(location, dict): raise ValueError('个人音色对应的模型路径未配置')
            directory = resolve(path.parent, location.get('path'))
            manifest = resolve(path.parent, location.get('manifest'))
            verify_model(directory, manifest, entry, hash_files=False)
            result['modelFilesPresent'] = True
        except (ValueError, OSError, KeyError, TypeError, AttributeError) as error:
            issues.append(f'模型需要完善：{error}')
        audio_ok = text_ok = False
        try:
            audio = resolve(path.parent, voice.get('referenceAudio'))
            if not audio.is_file() or audio.stat().st_size == 0:
                raise ValueError('参考录音不存在或为空；填写 referenceAudio')
            audio_ok = True
        except (ValueError, OSError, TypeError) as error:
            issues.append(f'个人音色需要完善：{error}')
        try:
            text_file = resolve(path.parent, voice.get('referenceTextFile'))
            if not text_file.read_text(encoding='utf-8').strip():
                raise ValueError('参考逐字文本为空；填写 referenceTextFile')
            text_ok = True
        except (ValueError, OSError, TypeError) as error:
            issues.append(f'个人音色文字需要完善：{error}')
        result['customVoiceFilesPresent'] = audio_ok and text_ok
        result['referenceTextVerified'] = voice.get('referenceTextVerified') is True
        # Reuse the production schema/settings checks, including the human transcript check.
        try:
            load_config(path)
        except (ValueError, OSError, KeyError, TypeError, AttributeError) as error:
            issues.append(f'配置需要完善：{error}')
        if not issues:
            result['status'] = 'configured-unverified'
            result['nextStep'] = '已发现模型与默认个人音色，直接沿用；正式合成仍执行模型 SHA256、录音格式与平台检查。'
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as error:
        issues.append(f'声音配置需要完善：{error}')
    return result


def check(c):
    if platform.system() != 'Darwin' or platform.machine() != 'arm64':
        raise ValueError('本克隆引擎仅支持 macOS Apple Silicon；其他平台使用外部配音入口')
    count = verify_model(c['modelPath'], c['manifestPath'], c['model'])
    text = c['referenceTextFile'].read_text(encoding='utf-8').strip()
    if not text:
        raise ValueError('参考文字不能为空')
    audio = c['referenceAudio']
    info = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams',
                      '-show_format', '-of', 'json', str(audio)]))
    streams = [s for s in info['streams'] if s['codec_type'] == 'audio']
    if len(streams) != 1 or streams[0]['channels'] != 1 or not streams[0]['codec_name'].startswith('pcm_'):
        raise ValueError('参考音频须为单声道 PCM WAV；先按 README 转换，不能只改扩展名')
    duration = float(info['format']['duration'])
    if not 3 <= duration <= 30:
        raise ValueError('参考片段须为连续 3–30 秒；本工作流先选 10–20 秒完整句子')
    return {'voiceId': c['voiceId'], 'modelId': c['model']['id'], 'verifiedFiles': count,
            'referenceSeconds': duration, 'referenceText': text,
            'referenceAudioSha256': sha(audio), 'referenceTextSha256': sha(c['referenceTextFile'])}


def download(model_id, root):
    # This command has no voice/config/audio inputs. It only fetches public model files.
    from huggingface_hub import HfApi, snapshot_download
    entry = catalog(model_id)
    dest = Path(root).expanduser().resolve() / model_id
    info = HfApi().model_info(entry['repo'], revision=entry['revision'], files_metadata=True)
    if info.sha != entry['revision']:
        raise ValueError('远程版本与固定 revision 不一致')
    def cached(item):
        file = within(dest, item.rfilename)
        if not file.is_file() or file.stat().st_size != item.size:
            return False
        if item.lfs:
            return sha(file) == item.lfs.sha256
        return hashlib.sha1(f'blob {item.size}\0'.encode() + file.read_bytes()).hexdigest() == item.blob_id
    if not info.siblings:
        raise ValueError('远程模型没有文件清单')
    reused = all(cached(item) for item in info.siblings)
    if not reused:
        snapshot_download(repo_id=entry['repo'], revision=entry['revision'], local_dir=dest, max_workers=3)
    files = []
    for item in info.siblings:
        file = within(dest, item.rfilename)
        size = file.stat().st_size
        digest = sha(file)
        if size != item.size:
            raise ValueError(f'下载文件大小不匹配：{item.rfilename}')
        if item.lfs:
            if digest != item.lfs.sha256:
                raise ValueError(f'下载 SHA256 不匹配：{item.rfilename}')
        elif hashlib.sha1(f'blob {size}\0'.encode() + file.read_bytes()).hexdigest() != item.blob_id:
            raise ValueError(f'下载 Git blob 哈希不匹配：{item.rfilename}')
        files.append({'file': item.rfilename, 'bytes': size, 'sha256': digest})
    write(dest / 'model-manifest.json', {'repo': entry['repo'], 'revision': entry['revision'],
          'verified': True, 'files': files, 'totalBytes': sum(f['bytes'] for f in files)})
    return {'directory': str(dest), 'verifiedFiles': len(files), 'reusedVerifiedFiles': reused}


def jobs_for(args):
    if args.project:
        import pipeline
        root = args.project.resolve()
        import asset_review
        asset_review.guard_if_locked(root)
        film = pipeline.config(root)
        jobs = [(s.get('narration', '').strip(), pipeline.local(root, s.get('voice', f'audio/{s["id"]}.wav')))
                for s in film['scenes'] if s.get('narration', '').strip()]
    else:
        if not args.text_file or not args.out:
            raise ValueError('试音需要 --text-file 和 --out，或使用 --project 按镜头生成')
        jobs = [(args.text_file.read_text(encoding='utf-8').strip(), args.out.resolve())]
    if not jobs or any(not text for text, _ in jobs):
        raise ValueError('待合成文字不能为空')
    if args.project:
        for _, path in jobs:
            asset_review.protect_output(root, path)
    paths = [path for _, path in jobs]
    if len(set(paths)) != len(paths):
        raise ValueError('多个镜头不能使用同一个输出音频路径')
    for _, path in jobs:
        if path.suffix.lower() != '.wav':
            raise ValueError('合成输出必须为 .wav')
        if path.exists() or path.with_suffix('.wav.json').exists():
            raise ValueError(f'输出已存在，改用新版本目录或新文件名：{path}')
    return jobs


def synthesize(c, jobs):
    attempts = []
    def guard(event, args):
        if event == 'socket.connect':
            attempts.append(str(args[1]))
            raise RuntimeError('离线配音禁止网络连接')
    for key in ('HF_HUB_OFFLINE', 'TRANSFORMERS_OFFLINE', 'HF_HUB_DISABLE_TELEMETRY', 'DO_NOT_TRACK'):
        os.environ[key] = '1'
    sys.addaudithook(guard)
    verified = check(c)
    import mlx.core as mx
    import numpy as np
    import soundfile as sf
    import importlib.metadata
    from mlx_audio.tts.utils import load_model
    if not mx.metal.is_available():
        raise ValueError('Metal GPU 不可用；检查运行权限与本机环境')
    start = time.monotonic()
    model = load_model(c['modelPath'], lazy=False, strict=True)
    load_seconds = time.monotonic() - start
    reports = []
    for index, (text, out) in enumerate(jobs):
        mx.random.seed((c['settings']['seed'] + index) % 2**32)
        started = time.monotonic()
        chunks, tokens = [], []
        for result in model.generate(text=text, lang_code=c['language'],
                                     ref_audio=str(c['referenceAudio']), ref_text=verified['referenceText'],
                                     temperature=c['settings']['temperature'],
                                     max_tokens=c['settings']['maxTokens'], verbose=False):
            chunks.append(np.array(result.audio, dtype=np.float32).reshape(-1))
            tokens.append(result.token_count)
            sample_rate = result.sample_rate
        if not chunks or any(t >= c['settings']['maxTokens'] for t in tokens):
            raise ValueError('没有完整语音或已达到 token 上限；缩短单镜台词/调整上限后在新输出目录重跑')
        audio = np.concatenate(chunks)
        if not len(audio) or not np.isfinite(audio).all() or np.max(np.abs(audio)) < 1e-5:
            raise ValueError('输出为空、非有限值或静音，不交付')
        peak = float(np.max(np.abs(audio)))
        # Static peak normalization preserves timing and pitch; final film loudness is handled by mix.
        gain = 10 ** (-3 / 20) / peak
        out.parent.mkdir(parents=True, exist_ok=True)
        sf.write(out, audio * gain, sample_rate, subtype='PCM_16')
        report = {'engine': c['model']['engine'], 'text': text, 'audioSha256': sha(out),
                  'voiceId': c['voiceId'], 'modelId': c['model']['id'], 'modelRevision': c['model']['revision'],
                  'modelManifestSha256': sha(c['manifestPath']),
                  'referenceAudioSha256': verified['referenceAudioSha256'],
                  'referenceTextSha256': verified['referenceTextSha256'], 'language': c['language'],
                  'generation': c['settings'] | {'seed': (c['settings']['seed'] + index) % 2**32},
                  'sampleRate': sample_rate, 'durationSeconds': len(audio)/sample_rate,
                  'loadSeconds': load_seconds, 'generationSeconds': time.monotonic()-started,
                  'peakMemoryGB': mx.get_peak_memory()/1e9, 'peakNormalizationDbfs': -3,
                  'gainDb': 20*math.log10(gain), 'tokens': tokens,
                  'versions': {n: importlib.metadata.version(n) for n in ('mlx', 'mlx-audio', 'transformers')},
                  'networkConnectionsBlocked': True, 'networkAttempts': attempts,
                  'contentReview': 'pending-listening', 'voiceSimilarity': 'pending-user'}
        write(out.with_suffix('.wav.json'), report)
        if attempts:
            raise RuntimeError('检测到被拦截的网络尝试；不得标为离线成功')
        reports.append({'file': str(out), 'durationSeconds': report['durationSeconds']})
    return reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('catalog', help='检索维护者核对的模型目录（不联网）')
    p.add_argument('--query', default='')
    p = sub.add_parser('scan', help='只读检索指定本地目录中的 Qwen3-TTS 模型候选')
    p.add_argument('--root', type=Path, required=True)
    p = sub.add_parser('voices', help='列出配置中的音色，不显示录音文字')
    p.add_argument('--config', type=Path)
    p.add_argument('--query', default='')
    p = sub.add_parser('doctor', help='首次使用只读检测，缺项提示；不下载、不合成')
    p.add_argument('--config', type=Path)
    p.add_argument('--project', type=Path)
    p = sub.add_parser('download', help='显式下载目录中的固定公开模型')
    p.add_argument('--model', required=True)
    p.add_argument('--root', type=Path, required=True)
    for name in ('check', 'synthesize'):
        p = sub.add_parser(name)
        p.add_argument('--config', type=Path)
        p.add_argument('--voice')
        if name == 'synthesize':
            group = p.add_mutually_exclusive_group(required=True)
            group.add_argument('--text-file', type=Path)
            group.add_argument('--project', type=Path)
            p.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.command == 'catalog':
        result = [m for m in catalog() if args.query.casefold() in json.dumps(m, ensure_ascii=False).casefold()]
    elif args.command == 'scan':
        if not args.root.is_dir():
            raise ValueError('扫描目录不存在')
        result = []
        for p in sorted(args.root.rglob('config.json')):
            if '.cache' in p.parts:
                continue
            try:
                if read(p).get('model_type') == 'qwen3_tts':
                    result.append({'path': str(p.parent.resolve()), 'status': 'candidate-not-hash-verified'})
            except (ValueError, OSError):
                continue
    elif args.command == 'voices':
        result = [{'id': k, 'label': v.get('label', k), 'model': v.get('model'),
                   'referenceTextVerified': v.get('referenceTextVerified', False)}
                  for k, v in read(required_config(explicit=args.config)).get('voices', {}).items()]
        result = [v for v in result if args.query.casefold() in json.dumps(v, ensure_ascii=False).casefold()]
    elif args.command == 'doctor':
        result = doctor(args.project, args.config)
    elif args.command == 'download':
        result = download(args.model, args.root)
    else:
        c = load_config(required_config(getattr(args, 'project', None), args.config), args.voice)
        if args.command == 'check':
            result = check(c)
            result.pop('referenceText')
        else:
            result = synthesize(c, jobs_for(args))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(f'ERROR: {type(error).__name__}: {error}', file=sys.stderr)
        sys.exit(1)
