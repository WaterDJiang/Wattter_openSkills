"""Rebuild the local demo-derived Foley bank in a new directory."""
import argparse
from html import escape
import hashlib
import json
import shutil
from pathlib import Path
import wave

import numpy as np

import brick
import wood

REV = '00a7f9ec99c8686265a8ca4ed9a3fdaaf27ea6f4'
SOURCE = f'https://github.com/lemomo-ai/lemo-opuscar/blob/{REV}'
# Stable id, name, scene, recipe, arguments, demo event, peak dBFS.
PRESETS = [
    ('snap', '卡扣咔嗒', '零件扣合、开关按到底', brick.click, (), 'click', -8),
    ('table-clack', '小物落桌', '硬物接触木桌、模型搭建', brick.clack, (), 'clack', -8),
    ('toy-step', '玩偶单步', '微缩人物踏步、逐格动画', brick.step, (), 'step', -14),
    ('low-thump', '低频闷响', '重物落定、强调落版', brick.thump, (), 'thump', -8),
    ('swish', '短掠风', '快速擦过、画面横移', brick.whoosh, (.35,), 'whoosh', -12),
    ('bubble-pop', '气泡弹出', '标签出现、喜剧点题', brick.pop, (), 'title', -12),
    ('chime', '清亮提示铃', '完成提示、一次信息揭示', brick.ding, (), 'ding', -14),
    ('paper-lay', '铺纸', '纸面展开、档案就位', wood.paper_lay, (), 'paper_lay', -10),
    ('wood-bite', '刻刀入木', '刀尖接触、工艺手部特写', wood.knife_bite, (), 'knife_bite', -9),
    ('metal-tap', '金属轻碰', '器具相碰、金属件接触', wood.clank, (), 'tongs_clank', -10),
    ('metal-drop', '金属落地连响', '小金属件落地、弹跳再停住', wood.compass_drop, (), 'compass_drop', -9),
    ('far-wind', '远处阵风', '空镜、空间切换、对白间隙', wood.wind, (3.0,), 'far_wind', -16),
]


def write_audition_page(destination, entries):
    cards = []
    for entry in entries:
        cards.append(f'<article><h2>{escape(entry["name"])}</h2>'
                     f'<p>{escape(entry["use"])} · {entry["seconds"]:.2f} 秒</p>'
                     f'<audio controls preload="none" aria-label="{escape(entry["name"])}" '
                     f'src="{escape(entry["file"])}"></audio></article>')
    head = """<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>拟音试听</title>
<style>*{box-sizing:border-box}body{font:16px/1.5 system-ui,sans-serif;max-width:1040px;margin:auto;padding:28px;background:#faf8f2;color:#222823}
main{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(235px,100%),1fr));gap:14px}article{padding:18px;background:white;border:1px solid #dad9cf;border-radius:12px}
h1{font-size:30px}h2{font-size:18px;margin:0}p{font-size:14px;color:#535a52}audio{width:100%;height:36px}footer{margin-top:22px}</style>
<h1>拟音试听</h1><main>"""
    foot = '</main><footer><a href="catalog.json">音效 ID 与来源</a> · <a href="LICENSE.txt">合成代码 MIT</a> · <a href="https://creativecommons.org/publicdomain/zero/1.0/">粉笔实录 CC0</a></footer></html>'
    (destination/'index.html').write_text(head + '\n'.join(cards) + foot)


def build(destination):
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError('输出目录须为空，避免覆盖已锁定的素材')
    clips = destination / 'clips'
    clips.mkdir()
    entries = []
    for sound_id, name, use, recipe, args, event, peak_db in PRESETS:
        module = recipe.__module__
        demo = 'brick-toy' if module == 'brick' else 'woodcut'
        code = 'core/audio/sfx.py' if module == 'brick' else 'styles/woodcut/demo/mix.py'
        seed = int.from_bytes(hashlib.sha256(sound_id.encode()).digest()[:4], 'big')
        brick._rng = np.random.default_rng(seed)
        wood.rng = np.random.default_rng(seed)
        samples = recipe(*args)
        # Smooth the clip boundaries, leaving percussive attacks intact.
        fade_in = 960 if sound_id == 'far-wind' else 8
        fade_out = min(4800 if sound_id == 'far-wind' else 240, len(samples) // 4)
        samples[:fade_in] *= np.linspace(0, 1, fade_in)
        samples[-fade_out:] *= np.linspace(1, 0, fade_out)
        samples *= (32767 * 10 ** (peak_db / 20)) / np.max(np.abs(samples))
        path = clips / f'sfx-{sound_id}.wav'
        with wave.open(str(path), 'wb') as wav:
            wav.setparams((1, 2, brick.SR, 0, 'NONE', 'not compressed'))
            wav.writeframes(np.rint(samples).astype('<i2').tobytes())
        entries.append(dict(id=sound_id, name=name, use=use, file=f'clips/{path.name}',
                            seconds=len(samples)/brick.SR, peakDbFS=peak_db, seed=seed,
                            kind='procedural', license='MIT (generator)', recipe=recipe.__name__, args=list(args), sourceUrl=f'{SOURCE}/{code}',
                            demo=demo, event=event, demoCredits=f'{SOURCE}/styles/{demo}/demo/CREDITS',
                            sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    recording = Path(__file__).with_name('clips') / 'chalkboard-writing.ogg'
    recording_sha = '35f65c08e27fbccaa894a134c2f0cd83f3c6159e9186649ffb3a4539d93962d3'
    if hashlib.sha256(recording.read_bytes()).hexdigest() != recording_sha:
        raise ValueError('粉笔实录与已核实的原件不符')
    shutil.copyfile(recording, clips / recording.name)
    entries.append(dict(id='chalk-writing', name='粉笔板书实录', use='课堂板书、手写讲解，按笔画截取',
                        kind='recording', file='clips/'+recording.name, seconds=41.685333, author='Tomproberts',
                        license='CC0-1.0', licenseUrl='https://creativecommons.org/publicdomain/zero/1.0/',
                        sourceUrl='https://commons.wikimedia.org/wiki/File:Chalkboard-writing.ogg',
                        originalUrl='https://upload.wikimedia.org/wikipedia/commons/3/36/Chalkboard-writing.ogg',
                        demo='chalkboard', demoCredits=f'{SOURCE}/styles/chalkboard/demo/CREDITS',
                        sha256=recording_sha))
    shutil.copyfile(Path(__file__).with_name("LICENSE.txt"), destination / "LICENSE.txt")
    write_audition_page(destination, entries)
    catalog = dict(generatorAuthor='Lemomo (LemoLab)', revision=REV, codeLicense='MIT',
                   licenseFile='LICENSE.txt', sampleRate=brick.SR, sounds=entries)
    (destination/'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2)+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    build(parser.parse_args().destination)
