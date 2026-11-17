#!/usr/bin/env python3
"""Versioned four-frame preview approval. No command infers or creates user consent."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SCHEMA = 'code-video-preview/v1'
STORE = '.preview-review'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def local(root, name):
    if not isinstance(name, str) or not name or Path(name).is_absolute():
        raise ValueError('预览路径须为项目内相对路径')
    result = (root / name).resolve()
    if not result.is_relative_to(root.resolve()):
        raise ValueError('预览路径不得越出项目')
    return result


def integer(value, name, minimum=1):
    if type(value) is not int or value < minimum:
        raise ValueError(f'{name}须为不小于{minimum}的整数')
    return value


def check_sources(root, binding):
    if binding.get('kind') not in ('pipeline', 'map'):
        raise ValueError('四帧预览kind须为pipeline或map')
    for key in ('fps', 'totalFrames', 'width', 'height'):
        integer(binding.get(key), key, 4 if key == 'totalFrames' else 1)
    sources = binding.get('sourceSha256')
    if not isinstance(sources, dict) or not sources:
        raise ValueError('四帧预览必须绑定实际绘图源文件')
    for name, expected in sources.items():
        file = local(root, name)
        if not isinstance(expected, str) or not re.fullmatch('[0-9a-f]{64}', expected) or not file.is_file() or digest(file) != expected:
            raise ValueError(f'四帧批准已失效：源文件变化或缺失 {name}；重新预览并取得用户确认')
    if binding['kind'] == 'pipeline':
        if not {'film.json', 'timeline.json', 'assets.json'} <= set(sources):
            raise ValueError('通用四帧须绑定film/timeline/assets')
        def code_path(name):
            p = Path(name)
            return p.suffix in ('.js', '.css', '.html') and (len(p.parts) == 1 or p.parts[0] == 'code')
        current_code = {p.relative_to(root).as_posix() for p in root.iterdir() if p.is_file() and code_path(p.name)}
        if (root / 'code').is_dir():
            current_code |= {p.relative_to(root).as_posix() for p in (root / 'code').rglob('*') if p.is_file() and p.suffix in ('.js', '.css', '.html')}
        if current_code != {name for name in sources if code_path(name)}:
            raise ValueError('四帧批准已失效：绘图代码文件集合新增或删除；重新预览并取得用户确认')
        for name in ('pipeline.py', 'render.cjs', 'preview_review.py', 'asset_review.py', 'speech.py'):
            if (root / 'tools' / name).is_file() and f'tools/{name}' not in sources:
                raise ValueError(f'四帧预览须冻结执行工具：tools/{name}')
        import asset_review
        if binding.get('assetReview') != asset_review.require(root):
            raise ValueError('四帧预览素材版本已失效')
        timeline = read(root / 'timeline.json')
        if not timeline.get('locked') or any(timeline.get(k) != binding[k] for k in ('fps', 'totalFrames', 'width', 'height')):
            raise ValueError('四帧预览与当前锁定时间轴不符')
    elif 'config.json' not in sources:
        raise ValueError('地图四帧须绑定实际config.json')


def current(root):
    pointer = root / STORE / 'current.json'
    if not pointer.is_file():
        raise ValueError('尚无四帧拼图：先生成预览，展示给用户并取得明确确认，禁止完整渲染')
    p = read(pointer)
    version = p.get('version', '')
    if not re.fullmatch(r'v\d{4,}', version):
        raise ValueError('四帧预览版本指针无效')
    manifest_file = root / STORE / 'versions' / version / 'manifest.json'
    if not manifest_file.is_file() or digest(manifest_file) != p.get('manifestSha256'):
        raise ValueError('四帧预览清单已被替换；重新生成，不能更新哈希冒用旧批准')
    m = read(manifest_file)
    if m.get('schema') != SCHEMA or m.get('version') != version:
        raise ValueError('四帧预览清单格式无效')
    return m, manifest_file


def validate_preview(root, expected_kind=None):
    m, file = current(root)
    binding = m['binding']
    if expected_kind is not None and binding['kind'] != expected_kind:
        raise ValueError('四帧预览来自其他导出路线')
    check_sources(root, binding)
    if hashlib.sha256(encoded(binding)).hexdigest() != m.get('bindingSha256'):
        raise ValueError('四帧绑定内容发生变化')
    frames = m.get('frames', [])
    if len(frames) != 4 or len({x['frame'] for x in frames}) != 4:
        raise ValueError('四帧预览必须恰有四个不同帧号')
    for item in frames:
        for key in ('file', 'originalFile'):
            f = local(root, item[key])
            if not f.is_file() or digest(f) != item['sha256']:
                raise ValueError(f'四帧样帧已变化：{item[key]}；重新预览并取得用户确认')
    sheet = local(root, m['contactSheet'])
    if not sheet.is_file() or digest(sheet) != m['contactSheetSha256']:
        raise ValueError('四帧拼图已变化；禁止冒用旧批准')
    return m, file


def check(root, expected_kind=None, frames_request=None):
    m, file = validate_preview(root, expected_kind)
    decisions = sorted(file.parent.glob('decision-*.json'), key=lambda f: int(f.stem.split('-')[1]))
    if not decisions:
        raise ValueError(f'四帧拼图{m["version"]}尚未获用户确认：{m["contactSheet"]}；禁止完整渲染')
    decision = read(decisions[-1])
    if decision.get('decision') != 'approved' or decision.get('authority') != 'user' or decision.get('manifestSha256') != digest(file) or not decision.get('userMessage', '').strip():
        raise ValueError('四帧批准缺失、已撤回或绑定旧清单；禁止完整渲染')
    if frames_request is not None:
        frames = frames_request.get('frames')
        if not isinstance(frames, list) or len(frames) != 4 or any(not isinstance(x, dict) for x in frames):
            raise ValueError('完整渲染前须重新绘制已批准的四帧')
        for actual, expected in zip(frames, m['frames']):
            image = local(root, actual.get('file'))
            if actual.get('frame') != expected['frame'] or not image.is_file() or digest(image) != expected['sha256']:
                raise ValueError('本次重绘四帧与已批准样帧不同；停止完整渲染，重新预览并取得用户确认')
    return {'version': m['version'], 'manifestSha256': digest(file), 'bindingSha256': m['bindingSha256'],
            'contactSheet': m['contactSheet'], 'contactSheetSha256': m['contactSheetSha256'],
            'decisionSha256': digest(decisions[-1]), 'frameIndices': [x['frame'] for x in m['frames']]}


def image_size(file):
    result = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'json', str(file)], check=True, capture_output=True, text=True)
    stream = json.loads(result.stdout)['streams'][0]
    return stream['width'], stream['height']


# A tiny fixed bitmap alphabet keeps frame/time labels portable even when FFmpeg
# was built without drawtext or no font package is installed. It is original code.
FONT = {
    '0': ['01110','10001','10011','10101','11001','10001','01110'],
    '1': ['00100','01100','00100','00100','00100','00100','01110'],
    '2': ['01110','10001','00001','00010','00100','01000','11111'],
    '3': ['11110','00001','00001','01110','00001','00001','11110'],
    '4': ['00010','00110','01010','10010','11111','00010','00010'],
    '5': ['11111','10000','10000','11110','00001','00001','11110'],
    '6': ['01110','10000','10000','11110','10001','10001','01110'],
    '7': ['11111','00001','00010','00100','01000','01000','01000'],
    '8': ['01110','10001','10001','01110','10001','10001','01110'],
    '9': ['01110','10001','10001','01111','00001','00001','01110'],
    'F': ['11111','10000','10000','11110','10000','10000','10000'],
    'R': ['11110','10001','10001','11110','10100','10010','10001'],
    'A': ['01110','10001','10001','11111','10001','10001','10001'],
    'M': ['10001','11011','10101','10101','10001','10001','10001'],
    'E': ['11111','10000','10000','11110','10000','10000','11111'],
    'S': ['01111','10000','10000','01110','00001','00001','11110'],
    '/': ['00001','00010','00010','00100','01000','01000','10000'],
    '.': ['00000','00000','00000','00000','00000','00110','00110'],
    ' ': ['00000'] * 7,
}


def write_label(file, text):
    width, height, scale = 640, 40, 3
    pixels = bytearray(bytes((244, 242, 236)) * width * height)
    if len(text) * 6 * scale > width - 24:
        raise ValueError('帧号/时码过长，无法生成可读拼图')
    for index, char in enumerate(text):
        for y, row in enumerate(FONT[char]):
            for x, dot in enumerate(row):
                if dot == '1':
                    for dy in range(scale):
                        for dx in range(scale):
                            at = ((10 + y*scale + dy)*width + 12 + index*6*scale + x*scale + dx)*3
                            pixels[at:at+3] = bytes((23, 41, 67))
    file.write_bytes(f'P6\n{width} {height}\n255\n'.encode() + pixels)


def prepare(root, request):
    binding = {k: request[k] for k in ('kind', 'fps', 'totalFrames', 'width', 'height', 'sourceSha256')}
    if 'assetReview' in request:
        binding['assetReview'] = request['assetReview']
    check_sources(root, binding)
    frames = request.get('frames')
    if not isinstance(frames, list) or len(frames) != 4:
        raise ValueError('必须选择恰好四张真实样帧')
    normalized = []
    for item in frames:
        if not isinstance(item, dict):
            raise ValueError('每张样帧须记录frame和file')
        frame = integer(item.get('frame'), 'frame', 0)
        if frame >= binding['totalFrames']:
            raise ValueError('样帧越出片长')
        source = local(root, item.get('file'))
        if not source.is_file() or image_size(source) != (binding['width'], binding['height']):
            raise ValueError('样帧缺失或尺寸不符：' + str(source))
        normalized.append({'frame': frame, 'seconds': frame / binding['fps'], 'originalFile': item['file'], 'sha256': digest(source)})
    if len({x['frame'] for x in normalized}) != 4:
        raise ValueError('样帧须为四个不同帧号')
    # Same request reuses the same immutable review bundle and any genuine existing decision.
    try:
        old, _ = validate_preview(root)
        keys = ('frame', 'seconds', 'sha256')
        if old['binding'] == binding and [{k: x[k] for k in keys} for x in old['frames']] == [{k: x[k] for k in keys} for x in normalized]:
            return {'version': old['version'], 'manifestFile': str((Path(STORE) / 'versions' / old['version'] / 'manifest.json')),
                    'contactSheet': old['contactSheet'], 'bindingSha256': old['bindingSha256'], 'reused': True}
    except (ValueError, OSError, KeyError, json.JSONDecodeError):
        pass
    versions = root / STORE / 'versions'
    ids = [int(f.name[1:]) for f in versions.glob('v*') if f.is_dir() and re.fullmatch(r'v\d{4,}', f.name)]
    version = f'v{max(ids, default=0)+1:04d}'
    folder = versions / version
    folder.mkdir(parents=True)
    rows = []
    for i, item in enumerate(normalized):
        dest = folder / f'frame-{i+1:02d}-{item["frame"]:06d}.png'
        shutil.copy2(local(root, item['originalFile']), dest)
        rows.append(dict(item, file=str(dest.relative_to(root))))
    sheet = folder / 'contact-sheet.png'
    filters = []
    for i, item in enumerate(rows):
        label = f'FRAME {item["frame"]:06d} / {item["seconds"]:.2f} S'
        write_label(folder / f'label-{i+1:02d}.ppm', label)
        filters.append(f'[{i}:v]scale=640:-2[im{i}];[{i+4}:v][im{i}]vstack=inputs=2[v{i}]')
    filters.append('[v0][v1][v2][v3]xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0[out]')
    args = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-filter_complex_threads', '1']
    for item in rows:
        args += ['-i', str(local(root, item['file']))]
    for i in range(4):
        args += ['-i', str(folder / f'label-{i+1:02d}.ppm')]
    result = subprocess.run(args + ['-filter_complex', ';'.join(filters), '-map', '[out]', '-frames:v', '1', str(sheet)], capture_output=True, text=True)
    if result.returncode:
        (folder / 'prepare-failure.log').write_text(result.stderr)
        raise ValueError('四帧拼图生成失败：' + result.stderr.strip())
    check_sources(root, binding)
    manifest = {'schema': SCHEMA, 'version': version, 'binding': binding,
                'bindingSha256': hashlib.sha256(encoded(binding)).hexdigest(), 'frames': rows,
                'contactSheet': str(sheet.relative_to(root)), 'contactSheetSha256': digest(sheet), 'userApproval': 'pending'}
    file = folder / 'manifest.json'
    write(file, manifest)
    write(root / STORE / 'current.json', {'version': version, 'manifestSha256': digest(file)})
    return {'version': version, 'manifestFile': str(file.relative_to(root)), 'contactSheet': manifest['contactSheet'],
            'bindingSha256': manifest['bindingSha256'], 'reused': False}


def decide(root, version, message, approved=True):
    if not isinstance(message, str) or not message.strip() or message.strip().lower() in ('继续', '好', '好的', 'a', 'b', 'c', 'd', 'e', 'continue', 'yes'):
        raise ValueError('须记录用户针对这版四帧的明确原话；普通继续/风格选择不能代替四帧确认')
    m, file = validate_preview(root)
    if version != m['version']:
        raise ValueError('只能记录当前展示版本的决定；用户尚未看到的新版本不能自动批准')
    decisions = sorted(file.parent.glob('decision-*.json'))
    entry = {'decision': 'approved' if approved else 'rejected', 'authority': 'user', 'userMessage': message,
             'version': version, 'manifestSha256': digest(file), 'contactSheetSha256': m['contactSheetSha256']}
    dest = file.parent / f'decision-{len(decisions)+1:04d}.json'
    write(dest, entry)
    return check(root) if approved else {'version': version, 'decision': 'rejected', 'record': str(dest.relative_to(root))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'check', 'approve', 'reject'])
    parser.add_argument('root', type=Path)
    parser.add_argument('--request', type=Path)
    parser.add_argument('--kind', choices=['pipeline', 'map'])
    parser.add_argument('--version')
    parser.add_argument('--message')
    args = parser.parse_args()
    root = args.root.resolve()
    if args.command == 'prepare':
        if args.request is None:
            parser.error('prepare需要--request FILE')
        result = prepare(root, read(args.request))
    elif args.command == 'check':
        result = check(root, args.kind, read(args.request) if args.request else None)
    else:
        if args.version is None or args.message is None:
            parser.error('approve/reject需要--version和--message用户原话')
        result = decide(root, args.version, args.message, args.command == 'approve')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        sys.exit(1)
