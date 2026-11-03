#!/usr/bin/env python3
"""把自有V2手绘示例放入新工程，复用现有pipeline初始化；不下载、不合成、不封锁素材。"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
import pipeline

FILES = ('forest.js', 'courier.js', 'scene.js', 'index.html', 'play.html', 'package.json',
         'tools/render_handpainted.cjs', 'tools/motion_preview.cjs', 'tools/keyframes.cjs', 'tools/check_pose.cjs', 'tools/compose.py')


def create(project):
    project = Path(project).expanduser().resolve()
    source = Path(__file__).resolve().parent.parent / 'assets/handpainted-cinema'
    if project.exists():
        raise ValueError('手绘示例必须使用尚不存在的新目录；不覆盖已有工程或素材')
    required = (*FILES, 'film.example.json', 'provenance.json', 'README.md')
    for name in required:
        if not (source / name).is_file():
            raise ValueError(f'手绘资源不完整：{name}；停止创建，不留下伪成功工程')
    pipeline.init(project)
    for name in FILES:
        shutil.copy2(source / name, project / name)
    shutil.copy2(source / 'film.example.json', project / 'film.json')
    shutil.copy2(source / 'provenance.json', project / 'art-provenance.json')
    shutil.copy2(source / 'README.md', project / 'HANDPAINTED.md')
    entries = {name: hashlib.sha256((project / name).read_bytes()).hexdigest() for name in (*FILES, 'film.json', 'art-provenance.json')}
    (project / 'handpainted-scaffold.json').write_text(json.dumps({
        'example': 'handpainted-cinema/v2', 'files': entries,
        'scope': '自有12秒工程示例；正式剧本/角色/时长另按内容重编，尚未合成声音/锁素材/渲染',
    }, ensure_ascii=False, indent=2) + '\n')
    print(f'已创建V2手绘示例：{project}；画面入口scene.js，先做静帧和动作审阅，再正式渲染。')
    return project


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('project', type=Path, help='尚不存在的新工程目录')
    args = p.parse_args()
    try:
        create(args.project)
    except (ValueError, OSError) as error:
        p.exit(1, f'ERROR: {error}\n')


if __name__ == '__main__':
    main()
