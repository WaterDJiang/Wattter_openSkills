#!/usr/bin/env python3
"""Rebuild original examples in a NEW directory. Never overwrites prior films or locks."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import wave

ROOT=Path(__file__).resolve().parents[1]
def run(*args,**kw): subprocess.run(list(map(str,args)),check=True,**kw)
def write(p,data): p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def sound(file,duration,index):
    # Original soft plucks aligned to demonstration actions; no samples or private voice.
    sr=48000;events=[(.7,220+index*30),(2.0,330+index*20),(4.1,440+index*10),(duration-1,550)]
    with wave.open(str(file),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr)
        for n in range(round(duration*sr)):
            t=n/sr;v=0
            for at,hz in events:
                age=t-at
                if 0<=age<.5:v+=.13*math.sin(2*math.pi*hz*age)*math.exp(-age*11)*min(1,age/.012)
            w.writeframesraw(struct.pack('<h',round(v*32767)))

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--only',choices=['knowledge','story','product','documentary','data','creative']);ap.add_argument('--render',action='store_true');a=ap.parse_args()
    dest=a.out.resolve()
    if dest.exists():raise SystemExit('输出目录已存在；使用全新目录，不覆盖已有作品或清单')
    dest.mkdir(parents=True)
    catalog=json.loads((ROOT/'config/capabilities.json').read_text())
    for index,sample in enumerate(catalog['samples']):
        if a.only and a.only!=sample['id']:continue
        project=dest/sample['id'];run(sys.executable,ROOT/'scripts/pipeline.py','init',project)
        shutil.copy2(ROOT/'assets/examples/scenes.js',project/'scenes.js')
        duration=sample['durationSeconds']
        film={'schema':'code-animation/v1','title':sample['title'],'width':960,'height':540,'fps':20,'seed':20261103,
              'scenes':[{'id':sample['id'],'title':sample['title'],'visualSeconds':duration,'narration':'','leadSeconds':0,'tailSeconds':0,
                         'director':{'group':sample['id'],'reviewAtSeconds':1.5}}],
              'audioTracks':[{'file':'audio/events.wav','startSeconds':0,'gain':1}]}
        write(project/'film.json',film);(project/'audio').mkdir(exist_ok=True);sound(project/'audio/events.wav',duration,index)
        assets={'schema':'code-animation-assets/v1','assets':[{'id':'events','path':'audio/events.wav','sourceUrl':None,'license':'本项目自制合成音；随仓库许可发布','useBasis':'make_examples.py 数学振荡器生成，无外部采样或私人录音','landingUrl':None}],'links':[]}
        write(project/'assets.json',assets)
        (project/'style-choice.md').write_text('status: delegated\nuser_basis: 2026-11-03 用户要求重新制作样片，作为合并维护验证。\nselected_direction: '+sample['style']+'\n')
        (project/'script.md').write_text('# '+sample['title']+'\n\n原创维护样例，'+str(duration)+'秒；无旁白，画面短句与主体运动说明内容。\n虚构/示例内容：'+str(sample['fictional'])+'。场景代码为完整动作脚本。\n')
        run(sys.executable,project/'tools/asset_review.py','seal',project)
        run(sys.executable,project/'tools/pipeline.py','timeline',project,'--lock')
        run(sys.executable,project/'tools/pipeline.py','mix',project)
        if a.render:
            run('node',project/'tools/render.cjs',project,'--preview')
            # Review image before publishing; this tool only renders and gathers technical evidence.
            run('node',project/'tools/render.cjs',project,'--render','--frame-format','jpeg')
            run(sys.executable,project/'tools/pipeline.py','finish',project)
            run(sys.executable,project/'tools/pipeline.py','review-init',project)
            run('ffmpeg','-y','-v','error','-ss',max(1,duration*.68),'-i',project/'final.mp4','-frames:v','1',project/'still.png')
            write(project/'provenance.json',{'createdAt':datetime.now(timezone.utc).isoformat(),'original':True,'externalMedia':[],
               'description':'自写图形/动作/示例数据/合成音；系统字体仅由浏览器调用，未分发字体文件',
               'sourceSha256':sha(ROOT/'assets/examples/scenes.js'),'generatorSha256':sha(Path(__file__)),
               'artifacts':{name:sha(project/name) for name in ('final.mp4','still.png','film.json','assets.json','render-report.json','delivery-check.json')},
               'visualReview':'pending','audioListening':'not_checked','userAcceptance':'pending'})
        print('generated',project,flush=True)
if __name__=='__main__':main()
