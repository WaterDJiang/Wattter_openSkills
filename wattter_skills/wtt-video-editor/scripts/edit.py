#!/usr/bin/env python3
"""Inspect existing footage and render an explicit FFmpeg edit plan."""

import argparse
from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
import shlex
import subprocess
from tempfile import TemporaryDirectory


FFMPEG = ("ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin")
SAMPLE_RATE = 48000
FPS_OPTIONS = (24, 25, 30, 48, 50, 60)
OVERLAPS = {
    "audio": "transition=custom:expr='if(gte(P,0.5),A,B)'",
    "dissolve": "transition=fade",
    "dip": "transition=fadeblack",
    # A diagonal, feathered front travels from the left edge to the right.
    "soft_wipe_right": (
        "transition=custom:"
        "expr='A+(B-A)*clip(((1-P)*1.24-X/W-0.12*(1-Y/H))/0.12,0,1)'"
    ),
}


def run(*args):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        raise ValueError(f"{shlex.join(map(str, args))}\n{result.stderr.strip()}")
    return result.stdout


def field(info, name, default=None):
    value = info.get(name)
    return default if value in (None, "N/A") else float(value)


def probe(path):
    if not path.is_file():
        raise ValueError(f"找不到素材 {path}")
    info = json.loads(run(
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path
    ))
    video = next((s for s in info["streams"] if s["codec_type"] == "video"
                  and not s.get("disposition", {}).get("attached_pic")), None)
    if video is None:
        raise ValueError(f"素材缺少视频流 {path}")
    audio = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    origin = field(info["format"], "start_time", 0.0)
    video_start = field(video, "start_time", origin)
    file_offset = video_start - origin
    duration = field(video, "duration")
    if duration is None:
        duration = field(info["format"], "duration", 0.0) - file_offset
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError(f"无法确定视频时长 {path}")
    audio_delay = field(audio, "start_time", origin) - video_start if audio else 0.0
    return video, audio, duration, file_offset, audio_delay


def fit(width, height):
    return (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease:"
        f"force_divisible_by=2:reset_sar=1:flags=lanczos,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1"
    )


def inspect(path, sheets):
    video, audio, duration, offset, delay = probe(path)
    report = {"path": str(path), "video_seconds": duration, "video_offset": offset,
              "audio_delay": delay, "video": video, "audio": audio}
    if sheets is not None:
        sheets.mkdir(parents=True, exist_ok=True)
        window = min(duration, 2.0)
        report["sheets"] = {}
        for name, start in (("head", 0.0), ("tail", duration - window)):
            destination = sheets / f"{name}.png"
            filters = (
                f"setpts=PTS-STARTPTS,fps={12 / window:.9f}:start_time=0,"
                f"trim=end_frame=12,{fit(256, 144)},tile=4x3:padding=2:margin=2"
            )
            run(*FFMPEG, "-n", "-ss", f"{max(0, start + offset):.9f}", "-i", path,
                "-map", f"0:{video['index']}", "-an", "-vf", filters, "-frames:v", "1",
                "-threads:v", "1", destination)
            if not destination.is_file():
                raise ValueError(f"未提取到窗口画面 {path} / {name}")
            report["sheets"][name] = {"path": str(destination), "window_start": start,
                                      "interval": window / 12}
    return report


def number(value, label):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError(f"{label} 需要非负秒数")
    return value


def check_keys(config, allowed, label):
    if not isinstance(config, dict) or config.keys() - set(allowed.split()):
        raise ValueError(f"{label} 可用字段为 {allowed}")


@dataclass
class Clip:
    path: Path
    video_index: int
    audio_index: int | None
    audio_delay: float
    start: int
    end: int
    fade_in: int
    fade_out: int
    mode: str
    overlap: int
    zoom: float

    @property
    def frames(self):
        return self.end - self.start


def read_clips(config, parent, fps):
    clips = []
    for idx, entry in enumerate(config, 1):
        label = f"第 {idx} 段"
        check_keys(entry, "path in out audio_fade_in audio_fade_out transition zoom note", label)
        if not isinstance(entry.get("path"), str) or not entry["path"]:
            raise ValueError(f"{label} 缺少素材路径")
        path = (parent / entry["path"]).resolve()
        video, audio, duration, _, delay = probe(path)
        start = round(number(entry.get("in", 0), f"{label} in") * fps)
        end = round(number(entry.get("out", duration), f"{label} out") * fps)
        if not 0 <= start < end <= round(duration * fps):
            raise ValueError(f"{label} 的剪接区间超出有效范围或不足一帧（{duration:.3f} 秒）")
        fade_in = round(number(entry.get("audio_fade_in", 0), label) * SAMPLE_RATE)
        fade_out = round(number(entry.get("audio_fade_out", 0), label) * SAMPLE_RATE)
        if fade_in + fade_out > (end - start) * SAMPLE_RATE // fps:
            raise ValueError(f"{label} 的音频淡化长于保留区间")
        transition = entry.get("transition", {})
        check_keys(transition, "type duration", f"{label} transition")
        mode = transition.get("type", "cut")
        if mode not in ("cut", *OVERLAPS):
            raise ValueError(f"{label} 可用转场为 cut、{ '、'.join(OVERLAPS)}")
        seconds = number(transition.get("duration", 0), label)
        overlap = round(seconds * fps)
        if mode == "cut" and seconds != 0:
            raise ValueError(f"{label} 直切的重叠时长须为零")
        if mode != "cut" and (not clips or not 0 < overlap < min(
            clips[-1].frames - clips[-1].overlap, end - start
        )):
            raise ValueError(f"{label} 的重叠区间必须完整落在相邻两个片段内")
        zoom = number(entry.get("zoom", 1), f"{label} zoom")
        if zoom < 1:
            raise ValueError(f"{label} zoom 为居中放大倍率，须大于或等于 1")
        clips.append(Clip(path, video["index"], audio["index"] if audio else None,
                          delay, start, end, fade_in, fade_out, mode, overlap, zoom))
    return clips


def clip_filters(index, clip, width, height, fps):
    samples_per_frame = SAMPLE_RATE // fps
    first_sample = clip.start * samples_per_frame
    end_sample = clip.end * samples_per_frame
    framing = ""
    if clip.zoom > 1:
        framing = f"crop=trunc(iw/{clip.zoom}/2)*2:trunc(ih/{clip.zoom}/2)*2,"
    video = (
        f"[{index}:{clip.video_index}]setpts=PTS-STARTPTS,"
        f"fps={fps}:start_time=0:eof_action=pass,"
        f"trim=start_frame={clip.start}:end_frame={clip.end},"
        f"{framing}{fit(width, height)},format=yuv420p,settb=1/{fps},setpts=N[v{index}]"
    )
    if clip.audio_index is None:
        audio = f"anullsrc=r={SAMPLE_RATE}:cl=stereo"
    else:
        audio = (
            f"[{index}:{clip.audio_index}]asetpts=PTS-STARTPTS+({clip.audio_delay:.9f}/TB),"
            f"aresample={SAMPLE_RATE}:async=1:first_pts=0,"
            f"aformat=sample_rates={SAMPLE_RATE}:channel_layouts=stereo,"
            f"apad=whole_len={end_sample}"
        )
    audio += f",atrim=start_sample={first_sample}:end_sample={end_sample},asetpts=N/SR/TB"
    if clip.fade_in:
        audio += f",afade=t=in:ss=0:ns={clip.fade_in}"
    if clip.fade_out:
        audio += f",afade=t=out:ss={end_sample - first_sample - clip.fade_out}:ns={clip.fade_out}"
    return video, f"{audio}[a{index}]"


def assemble(clips, width, height, fps):
    filters = []
    timeline = []
    cursor = 0
    video, audio = "", ""
    for index, clip in enumerate(clips):
        filters.extend(clip_filters(index, clip, width, height, fps))
        offset = cursor - clip.overlap
        timeline.append({"path": str(clip.path), "source_in_frame": clip.start,
                         "source_out_frame": clip.end, "timeline_in_frame": offset,
                         "timeline_out_frame": offset + clip.frames,
                         "transition": clip.mode, "overlap_frames": clip.overlap})
        incoming_video, incoming_audio = f"[v{index}]", f"[a{index}]"
        if index == 0:
            video, audio = incoming_video, incoming_audio
        else:
            if clip.mode == "cut":
                picture_join = "concat=n=2:v=1:a=0"
                sound_join = "concat=n=2:v=0:a=1"
            else:
                picture_join = (
                    f"xfade={OVERLAPS[clip.mode]}:duration={clip.overlap / fps:.9f}:"
                    f"offset={offset / fps:.9f}"
                )
                sound_join = f"acrossfade=ns={clip.overlap * SAMPLE_RATE // fps}"
            joined_video, joined_audio = f"[vjoin{index}]", f"[ajoin{index}]"
            filters.extend((
                f"{video}{incoming_video}{picture_join},format=yuv420p,"
                f"settb=1/{fps},setpts=N{joined_video}",
                f"{audio}{incoming_audio}{sound_join},asetpts=N/SR/TB{joined_audio}",
            ))
            video, audio = joined_video, joined_audio
        cursor = offset + clip.frames
    return ";".join(filters), video, audio, cursor, timeline


def render(plan, output):
    config = json.loads(plan.read_text(encoding="utf-8"))
    check_keys(config, "width height fps clips", "剪接单")
    width, height, fps = (config.get(key) for key in ("width", "height", "fps"))
    if any(type(size) is not int or size < 2 or size % 2 for size in (width, height)):
        raise ValueError("width 和 height 须为正偶数")
    if type(fps) is not int or fps not in FPS_OPTIONS:
        raise ValueError(f"fps 须为 {FPS_OPTIONS} 中的整数")
    entries = config.get("clips")
    if not isinstance(entries, list) or not entries:
        raise ValueError("clips 须为非空素材数组")
    if output.suffix.lower() != ".mp4" or output.exists() or output.is_symlink():
        raise ValueError(f"请指定一个尚不存在的 MP4 输出路径 {output}")
    clips = read_clips(entries, plan.parent, fps)
    graph, video_label, audio_label, frames, timeline = assemble(clips, width, height, fps)
    output.parent.mkdir(parents=True, exist_ok=True)
    inputs = [arg for clip in clips for arg in ("-i", clip.path)]
    with TemporaryDirectory(prefix=".ffedit-", dir=output.parent) as directory:
        candidate = Path(directory) / "render.mp4"
        run(*FFMPEG, "-xerror", *inputs, "-filter_complex", graph,
            "-map", video_label, "-map", audio_label, "-c:v", "libx264",
            "-crf", "17", "-preset", "fast", "-pix_fmt", "yuv420p",
            "-fps_mode", "passthrough", "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", candidate)
        video, audio, duration, _, _ = probe(candidate)
        if (int(video.get("nb_frames", 0)) != frames
                or abs(duration - frames / fps) > 0.001):
            raise ValueError(f"视频帧数或时长异常，计划 {frames} 帧，实际 "
                             f"{video.get('nb_frames')} 帧、{duration:.6f} 秒")
        audio_duration = field(audio or {}, "duration", 0.0)
        if abs(audio_duration - frames / fps) > 0.024:
            raise ValueError(f"音视频时长不符，视频 {duration:.6f} 秒，音频 {audio_duration:.6f} 秒")
        run(*FFMPEG, "-xerror", "-i", candidate, "-map", "0:v:0", "-map", "0:a:0",
            "-f", "null", "-")
        os.link(candidate, output)
    return {"output": str(output), "fps": fps, "frames": frames,
            "seconds": frames / fps, "timeline": timeline}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    review = sub.add_parser("inspect", help="读取媒体轨道和首尾帧拼图")
    review.add_argument("input", type=Path)
    review.add_argument("--sheets", type=Path)
    export = sub.add_parser("render", help="按 JSON 剪接单生成并核验 MP4")
    export.add_argument("plan", type=Path)
    export.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "inspect":
            report = inspect(args.input.resolve(), args.sheets)
        else:
            report = render(args.plan.resolve(), args.output.absolute())
    except (ValueError, OSError) as error:
        parser.exit(1, f"{error}\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
