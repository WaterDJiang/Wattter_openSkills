#!/usr/bin/env python3
"""Local footage -> immutable frame sequences; never fetch or approve assets implicitly."""
import argparse
import json
import math
import subprocess
import sys
from pathlib import Path
import asset_review as ar

SCHEMA = 'code-animation-footage/v1'


def integer(value, name, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f'{name} 须为 >= {minimum} 的整数')
    return value


def numeric(value, name, minimum=0):
    if type(value) not in (int, float) or not math.isfinite(value) or value < minimum:
        raise ValueError(f'{name} 须为 >= {minimum} 的有限数值')
    return value


def staging(root, name):
    """Accept only normal asset paths or real paths in the candidate tree."""
    if not isinstance(name, str) or not name or Path(name).is_absolute() or '..' in Path(name).parts or '\\' in name:
        raise ValueError('路径须为项目内相对路径')
    if not name.startswith('.asset-review/candidates/'):
        return ar.local(root, name)
    path = root / name
    if not path.resolve().is_relative_to(root / '.asset-review/candidates'):
        raise ValueError('候选路径越界')
    for parent in (path, *path.parents):
        if parent == root: break
        if parent.is_symlink(): raise ValueError('候选路径不能是软链')
    return path


def recipe(data):
    if data.get('schema') != SCHEMA: raise ValueError('footage schema 不符')
    fps = integer(data.get('fps'), 'fps', 1)
    clips = data.get('clips')
    if not isinstance(clips, list) or not clips: raise ValueError('clips 不能为空')
    seen = set()
    for clip in clips:
        ar.valid_id(clip.get('id'))
        if clip['id'] in seen: raise ValueError('clip id 重复')
        seen.add(clip['id'])
        integer(clip.get('startFrame'), 'startFrame')
        integer(clip.get('durationFrames'), 'durationFrames', 1)
        numeric(clip.get('inSeconds'), 'inSeconds')
        numeric(clip.get('speed', 1), 'speed', .01)
        integer(clip.get('width'), 'width', 2)
        if not isinstance(clip.get('syncBasis'), str) or not clip['syncBasis'].strip():
            raise ValueError('syncBasis 必填；未同步须明确写明')
        if clip.get('audio') != 'mute':
            raise ValueError('预抽帧仅接受 audio=mute；原声另提取登记并接入 audioTracks')
    return fps, clips


def prepare(root, recipe_path, out_name, target=None):
    root = Path(root).resolve()
    ar.guard_if_locked(root)
    data = ar.read(staging(root, recipe_path))
    fps, clips = recipe(data)
    out = staging(root, out_name)
    ar.protect_output(root, out)
    target = target or out_name
    ar.local(root, target)
    ar.valid_id(Path(target).name)
    if out.exists(): raise ValueError('输出已存在，禁止覆盖；使用新版本目录')
    is_candidate = out_name.startswith('.asset-review/candidates/')
    if not is_candidate and target != out_name:
        raise ValueError('非候选输出的 target 必须等于 out')
    if any((root/target).glob('*')) and is_candidate:
        raise ValueError('派生素材使用新的 target 版本目录，不覆盖当前序列')
    # Validate all sources before creating output. Metadata is copied, never guessed.
    inputs = []
    for clip in clips:
        source = ar.local(root, clip.get('sourcePath'))
        actual = staging(root, clip.get('inputPath', clip['sourcePath']))
        if actual != source and not clip.get('inputPath', '').startswith('.asset-review/candidates/'):
            raise ValueError('inputPath 替换只能指向候选目录')
        meta = clip.get('provenance', {})
        ar.validate_selection({'assets': [dict(meta, id=clip['id'], sha256='pending')], 'links': []})
        info = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(actual)]))
        videos = [s for s in info['streams'] if s['codec_type'] == 'video']
        if not videos: raise ValueError(f'没有视频流：{actual}')
        duration = float(videos[0].get('duration', info['format'].get('duration', 0)))
        end = clip['inSeconds'] + clip['durationFrames'] / fps * clip.get('speed', 1)
        if end > duration + 1e-6: raise ValueError(f'{clip["id"]} 源片段越界：需要 {end}s，来源 {duration}s')
        inputs.append((clip, actual, ar.sha(actual)))
    out.mkdir(parents=True, exist_ok=False)
    manifest = {'schema':SCHEMA, 'fps':fps, 'toolVersion':1,
                'ffmpegVersion':subprocess.check_output(['ffmpeg','-version'],text=True).splitlines()[0], 'clips':[]}
    fragment = {'schema':ar.SCHEMA, 'assets':[], 'links':[]}
    def entry(aid, relative, meta):
        item = dict(meta, id=aid, path=f'{target}/{relative}')
        if is_candidate: item['candidatePath'] = f'{out_name}/{relative}'
        fragment['assets'].append(item)
    try:
        for clip, actual, source_sha in inputs:
            folder = out / clip['id']; folder.mkdir()
            speed = clip.get('speed', 1)
            vf = f'setpts=(PTS-STARTPTS)/{speed},fps={fps}:round=up,scale={clip["width"]}:-2'
            # Trim in source time BEFORE retiming; -ss after filters would select output time.
            command = ['ffmpeg','-nostdin','-n','-v','error','-i',str(actual),'-an','-vf',
                       f'trim=start={clip["inSeconds"]}:end={clip["inSeconds"]+clip["durationFrames"]/fps*speed},'+vf,
                       '-frames:v',str(clip['durationFrames']),'-start_number','0',str(folder/'%06d.png')]
            subprocess.run(command, check=True)
            files = sorted(folder.glob('*.png'))
            if len(files) != clip['durationFrames']: raise ValueError(f'{clip["id"]} 缺帧：{len(files)}/{clip["durationFrames"]}')
            if ar.sha(actual) != source_sha: raise ValueError('预处理期间源文件变化')
            item = {k:v for k,v in clip.items() if k not in ('inputPath','provenance')}
            item.update(speed=speed, sourceSha256=source_sha, frames=[])
            for index, file in enumerate(files):
                rel = file.relative_to(out).as_posix()
                item['frames'].append({'path':f'{target}/{rel}', 'sha256':ar.sha(file)})
                entry(f'{Path(target).name}-{clip["id"]}-f{index}', rel, clip['provenance'])
            manifest['clips'].append(item)
        ar.write_new(out/'manifest.json', manifest)
        entry(f'{Path(target).name}-manifest','manifest.json',
              {'sourceUrl':None,'license':'本项目生成的处理记录；源素材许可见各项',
               'useBasis':'绑定来源哈希、处理参数和全部派生帧','landingUrl':None})
        ar.write_new(out/'assets.fragment.json', fragment)
    except Exception as error:
        (out/'FAILED.txt').write_text(str(error)+'\n',encoding='utf-8')
        raise
    return {'manifest':f'{target}/manifest.json', 'fragment':f'{out_name}/assets.fragment.json',
            'status':'candidate' if is_candidate else 'prepared-unsealed'}


def check(root, film=None, total_frames=None):
    root = Path(root).resolve()
    film = film or ar.read(root/'film.json')
    name = film.get('footageManifest')
    if name is None: return None
    ar.require(root)
    _, selection = ar.history(root)
    approved = {a['path']:a['sha256'] for a in selection['assets']}
    def verify(path, expected=None):
        file = ar.local(root, path)
        if path not in approved: raise ValueError(f'视频素材未登记：{path}')
        if expected is not None and approved[path] != expected:
            raise ValueError(f'视频源或派生哈希过期：{path}；重新准备并审阅')
        return file
    manifest = ar.read(verify(name))
    fps, clips = recipe(manifest)
    if fps != film['fps']: raise ValueError('预抽帧 fps 与 film 不符；重新准备')
    for clip in clips:
        verify(clip['sourcePath'], clip.get('sourceSha256'))
        if not clip.get('sourceSha256'): raise ValueError('缺少视频源哈希')
        frames = clip.get('frames', [])
        if len(frames) != clip['durationFrames']: raise ValueError('序列缺帧')
        if len({f['path'] for f in frames}) != len(frames): raise ValueError('序列帧路径重复')
        if total_frames is not None and clip['startFrame']+clip['durationFrames'] > total_frames:
            raise ValueError(f'{clip["id"]} 超出成片时间轴')
        for frame in frames:
            if not frame.get('sha256'): raise ValueError('缺少派生帧哈希')
            verify(frame['path'], frame['sha256'])
    return name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare','check'])
    parser.add_argument('project',type=Path)
    parser.add_argument('--recipe'); parser.add_argument('--out'); parser.add_argument('--target')
    args = parser.parse_args()
    if args.command == 'prepare':
        if not args.recipe or not args.out: parser.error('prepare 需要 --recipe 和 --out')
        print(json.dumps(prepare(args.project,args.recipe,args.out,args.target),ensure_ascii=False))
    else:
        film=ar.read(args.project/'film.json')
        timeline=ar.read(args.project/'timeline.json') if (args.project/'timeline.json').is_file() else {}
        print(json.dumps({'manifest':check(args.project,film,timeline.get('totalFrames'))},ensure_ascii=False))


if __name__ == '__main__':
    try: main()
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        print(f'ERROR: {error}',file=sys.stderr);sys.exit(1)
