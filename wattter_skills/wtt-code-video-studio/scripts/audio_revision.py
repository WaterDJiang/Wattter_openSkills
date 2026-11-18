#!/usr/bin/env python3
"""已获批通用成片的纯音轨修订：锁素材、复制画面流、比较全部帧；不生成四帧批准。"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import asset_review
import pipeline


def run(args):
    command = [str(x) for x in args]
    try:
        return subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f'命令失败（{error.returncode}）：{command}\n{error.stderr}') from error


def picture(file):
    streams = pipeline.probe(file)['streams']
    video = [s for s in streams if s['codec_type'] == 'video']
    if len(video) != 1:
        raise ValueError('须恰有一条视频流')
    video = video[0]
    metadata = {k: video[k] for k in ('codec_name', 'width', 'height', 'avg_frame_rate', 'nb_frames')}
    metadata['duration'] = float(video['duration'])
    packet_hash = run(['ffmpeg', '-v', 'error', '-i', file, '-map', '0:v:0',
                       '-c:v', 'copy', '-f', 'hash', '-']).stdout.strip()
    decoded = run(['ffmpeg', '-v', 'error', '-xerror', '-i', file, '-map', '0:v:0',
                   '-f', 'framemd5', '-']).stdout
    rows = [line.strip() for line in decoded.splitlines() if line.strip() and not line.startswith('#')]
    if not rows or len(rows) != int(video['nb_frames']):
        raise ValueError('完整解码帧数与视频声明不一致')
    return {'metadata': metadata, 'packetHash': packet_hash, 'decodedFrames': rows}


def same_picture(expected, actual):
    if expected != actual:
        raise ValueError('画面流、全部解码帧或视频时序不同；停止纯音轨修订，按新版四帧流程制作')


def original_receipt(root):
    # Reuse current source/asset/mix/preview/render guards without rewriting old reports.
    timeline = pipeline.check_render(root)
    expected = {'assetReview': timeline['assetReview'],
                'finalSha256': pipeline.digest(root / 'final.mp4'),
                'renderReportSha256': pipeline.digest(root / 'render-report.json'),
                'mixReportSha256': pipeline.digest(root / 'audio/mix-report.json')}
    if pipeline.read(root / 'finalization.json') != expected:
        raise ValueError('原成片未绑定获批画面和素材；不能沿用四帧批准')
    return timeline, expected


def compose(original, root, picture_name, audio_name, output_name, report_name, message):
    original, root = Path(original).resolve(), Path(root).resolve()
    if root == original:
        raise ValueError('纯音轨修订须使用独立目录，保留原工程和成片')
    if not message.strip():
        raise ValueError('记录用户明确换音对象与目标的真实原话；不自动代用户授权')
    staged_picture, audio, output, report = [pipeline.local(root, name) for name in
                                            (picture_name, audio_name, output_name, report_name)]
    for dest in (output, report):
        if dest.exists() or dest.is_symlink():
            raise ValueError(f'修订输出已存在，换新版本名称，禁止覆盖：{dest}')
        if not dest.parent.is_dir():
            raise ValueError(f'先创建输出父目录：{dest.parent}')
    if output == report:
        raise ValueError('视频与报告路径不能相同')
    receipt = {'schema': 'code-video-audio-revision/v1', 'passed': False,
               'scope': 'audio-only-postproduction', 'userMessage': message,
               'subjectiveListening': 'pending-user', 'userAcceptance': 'pending'}
    try:
        timeline, old_receipt = original_receipt(original)
        asset_review.registered(root, [picture_name, audio_name])
        lock = asset_review.require(root)
        baseline = timeline['assetReview']
        inherited = root / '.asset-review/versions' / baseline['version'] / 'manifest.json'
        if not inherited.is_file() or pipeline.digest(inherited) != baseline['manifestSha256']:
            raise ValueError('修订目录必须继承原素材锁历史；禁止重建清单或重新seal绕过diff审阅')
        for version in sorted((root / '.asset-review/versions').glob('v[0-9]*')):
            if version.name > baseline['version']:
                authorization = pipeline.read(version / 'authorization.json')
                diff = pipeline.read(version / 'diff.json')
                if (authorization.get('kind') not in ('confirmed', 'explicit-request')
                        or not authorization.get('statement', '').strip() or not diff.get('changes')):
                    raise ValueError('新素材版本缺少实际diff与用户授权')
        sources = {str(file): pipeline.digest(file) for file in (staged_picture, audio)}
        original_picture = picture(original / 'silent.mp4')
        metadata = original_picture['metadata']
        if (metadata['codec_name'], metadata['width'], metadata['height'], int(metadata['nb_frames'])) != (
                'h264', timeline['width'], timeline['height'], timeline['totalFrames']):
            raise ValueError('原画面参数与获批时间轴不一致')
        from fractions import Fraction
        if Fraction(metadata['avg_frame_rate']) != timeline['fps']:
            raise ValueError('原画面帧率与获批时间轴不一致')
        same_picture(original_picture, picture(staged_picture))
        expected_seconds = timeline['totalFrames'] / timeline['fps']
        streams = pipeline.probe(audio)['streams']
        if len(streams) != 1 or streams[0]['codec_type'] != 'audio':
            raise ValueError('新母带须恰有一条音频流')
        if not streams[0]['codec_name'].startswith('pcm_') or streams[0].get('sample_rate') != '48000':
            raise ValueError('新母带须为48kHz PCM音频')
        if abs(float(streams[0]['duration']) - expected_seconds) > 1 / 48000:
            raise ValueError('新母带须按原时序混成等长音频；不能裁词、加速或改变字幕/画面时长')
        samples = round(expected_seconds * 48000)
        command = ['ffmpeg', '-hide_banner', '-v', 'error', '-n', '-i', staged_picture,
                   '-i', audio, '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy',
                   '-af', 'loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000,asetpts=N/SR/TB,'
                   f'apad=whole_len={samples},atrim=end_sample={samples},asetpts=N/SR/TB',
                   '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', output]
        receipt['command'] = [str(x) for x in command]
        run(command)
        same_picture(original_picture, picture(output))
        info = pipeline.probe(output)
        videos = [s for s in info['streams'] if s['codec_type'] == 'video']
        audios = [s for s in info['streams'] if s['codec_type'] == 'audio']
        if len(videos) != 1 or len(audios) != 1 or len(info['streams']) != 2:
            raise ValueError('输出须仅有一条视频与一条新音轨')
        if videos[0]['codec_name'] != 'h264' or audios[0]['codec_name'] != 'aac':
            raise ValueError('仅支持原H.264画面与新AAC音轨')
        if any(abs(float(s['duration']) - expected_seconds) > max(1 / timeline['fps'], .05)
               for s in info['streams']):
            raise ValueError('最终音画时长不闭合')
        decoded = run(['ffmpeg', '-v', 'error', '-xerror', '-i', output, '-f', 'null', '-'])
        if decoded.stderr.strip():
            raise ValueError(f'解码错误：{decoded.stderr}')
        volume = run(['ffmpeg', '-hide_banner', '-i', output, '-vn', '-af',
                      'volumedetect', '-f', 'null', '-']).stderr
        peak = re.search(r'max_volume: ([-\d.]+) dB', volume)
        if peak is None or float(peak[1]) >= 0:
            raise ValueError('音轨静音、峰值无法核验或达到0dBFS')
        if sources != {str(file): pipeline.digest(file) for file in (staged_picture, audio)}:
            raise ValueError('修订输入执行期间变化')
        if original_receipt(original)[1] != old_receipt or asset_review.require(root) != lock:
            raise ValueError('原批准或素材锁执行期间变化')
        receipt.update(passed=True, originalFinalSha256=old_receipt['finalSha256'],
                       sourceSha256=sources, assetReview=lock,
                       finalSha256=pipeline.digest(output),
                       videoStreamSha256=original_picture['packetHash'],
                       allDecodedFramesIdentical=True, totalFrames=timeline['totalFrames'],
                       durationSeconds=expected_seconds, samplePeakDbfs=float(peak[1]),
                       audioSource=audio_name, originalAudioMixed=False,
                       originalPreviewApproval=pipeline.read(original / 'render-report.json')['previewReview'])
    except Exception as error:
        receipt['error'] = f'{type(error).__name__}: {error}'
        raise
    finally:
        with report.open('x', encoding='utf-8') as file:
            json.dump(receipt, file, ensure_ascii=False, indent=2)
            file.write('\n')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original', type=Path, required=True)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--picture', required=True, help='修订目录内已登记的原画面文件')
    parser.add_argument('--audio', required=True, help='修订目录内已登记的等长新母带')
    parser.add_argument('--out', default='final-personal-voice.mp4')
    parser.add_argument('--report', default='audio-revision-check.json')
    parser.add_argument('--message', required=True)
    args = parser.parse_args()
    print(json.dumps(compose(args.original, args.project, args.picture, args.audio,
                             args.out, args.report, args.message), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(f'ERROR: {type(error).__name__}: {error}', file=sys.stderr)
        sys.exit(1)
