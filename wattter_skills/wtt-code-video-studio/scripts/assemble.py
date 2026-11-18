#!/usr/bin/env python3
"""从分镜工作稿创建新的视频工程。原镜头代码按稳定 ID 调用。"""
import argparse
import re
import shutil
import sys
import tempfile
from pathlib import Path

import pipeline


def assemble(plan, destination, selected=None):
    plan = plan.resolve()
    data = pipeline.read(plan)
    if not isinstance(data, dict) or set(data) - {'film', 'order', 'worldShots'} or not {'film', 'order'} <= set(data):
        raise ValueError('组装单需要 film 和 order')
    order = data['order']
    if not isinstance(order, list) or not order or not all(
            isinstance(s, str) and re.fullmatch(r'[a-z][a-z0-9-]*', s) for s in order):
        raise ValueError('order 需要非空的 kebab-case 镜头 ID 列表')
    if len(set(order)) != len(order):
        raise ValueError('order 镜头 ID 重复')
    ids = order if selected is None else selected
    if not ids or len(set(ids)) != len(ids) or not set(ids) <= set(order):
        raise ValueError('选中的镜头重复、为空或未在 order 声明')
    film = data['film']
    if not isinstance(film, dict) or {'scenes', 'assetReview'} & film.keys():
        raise ValueError('film 填写全片配置，镜头由 order 组装，素材锁由目标工程生成')
    if ids != order and (film.get('audioTracks') or 'rhythm' in film or
                         'footageManifest' in film or film.get('loop')):
        raise ValueError('局部或重排涉及全片音轨、拍点、素材时码或循环；先为目标顺序另存组装单并对齐时序')
    if destination.exists() or destination.is_symlink():
        raise ValueError('目标必须是新目录；已有工程请在原素材锁下局部修订')
    world_shots = data.get('worldShots', [])
    if (not isinstance(world_shots, list) or not all(isinstance(s, str) and s in order for s in world_shots)
            or len(world_shots) != len(set(world_shots))):
        raise ValueError('worldShots 须列出共用状态的镜头 ID，不能重复')
    world_file = None
    if set(ids).intersection(world_shots):
        world_file = pipeline.local(plan.parent, 'shared/world.js')
        if not world_file.is_file():
            raise ValueError('同源镜头缺少 shared/world.js')
    scenes = []
    modules = {}
    for sid in ids:
        scene = pipeline.read(pipeline.local(plan.parent, f'shots/{sid}.json'))
        if not isinstance(scene, dict) or scene.get('id') != sid:
            raise ValueError(f'{sid} 配置内 id 须与文件名一致')
        if 'transitionIn' in scene:
            bridge = scene['transitionIn']
            if (not isinstance(bridge, dict) or set(bridge) != {'from', 'frames'}
                    or type(bridge['frames']) is not int or bridge['frames'] < 2):
                raise ValueError(f'{sid} 过渡需要 from 和至少两帧的 frames')
            if not scenes and selected and order.index(sid) > 0 and bridge['from'] == order[order.index(sid)-1]:
                # A standalone shot opens directly in its own style.
                scene.pop('transitionIn')
            elif not scenes or bridge['from'] != scenes[-1]['id']:
                raise ValueError(f'{sid} 的过渡前镜不匹配；请为新顺序重新设计接点')
            if sid not in world_shots or bridge['from'] not in world_shots:
                raise ValueError(f'{sid} 过渡两端必须同时登记 worldShots')
        modules[sid] = pipeline.local(plan.parent, f'shots/{sid}.js')
        if not modules[sid].is_file():
            raise ValueError(f'缺少 {sid} 的画法文件：{modules[sid]}')
        scenes.append(scene)

    # Assemble and validate off to the side. Failed input never publishes a partial project.
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as tmp:
        project = Path(tmp) / 'film'
        pipeline.init(project)
        pipeline.write(project / 'film.json', dict(film, scenes=scenes))
        pipeline.config(project)
        (project / 'code').mkdir()
        if world_file is not None:
            (project / 'code/shared').mkdir()
            shutil.copyfile(world_file, project / 'code/shared/world.js')
        for sid, module in modules.items():
            shutil.copyfile(module, project / 'code' / f'{sid}.js')
        shutil.copyfile(Path(__file__).resolve().parents[1] / 'assets' / 'shot-dispatch.js',
                        project / 'scenes.js')
        project.rename(destination)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--shots', nargs='+', help='只组装这些 ID，按参数顺序排列')
    args = parser.parse_args()
    try:
        assemble(args.plan, args.destination, args.shots)
        print(f'已组装镜头工程：{args.destination.resolve()}')
    except (OSError, ValueError, KeyError) as exc:
        sys.exit(f'ERROR: {exc}')
