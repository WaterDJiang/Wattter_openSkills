#!/usr/bin/env python3
"""Check encoded video first/last RGB pixels; supplement unmasked world checks."""
import argparse,hashlib,json,subprocess
from pathlib import Path

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('video',type=Path);p.add_argument('--frames',type=int,default=600);p.add_argument('--width',type=int,default=1080);p.add_argument('--height',type=int,default=1080);p.add_argument('--fps',type=int,default=30);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 if a.out.exists():p.error('报告已存在，保留原记录并使用新路径')
 meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-of','json',str(a.video)]));v=next(s for s in meta['streams'] if s['codec_type']=='video')
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(a.video),'-vf',f'select=eq(n\\,0)+eq(n\\,{a.frames-1})','-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
 size=a.width*a.height*3
 if len(raw)!=size*2:raise ValueError('未读到期望尺寸的首尾两帧')
 mad=sum(abs(x-y) for x,y in zip(raw[:size],raw[size:]))/size/255
 from fractions import Fraction
 report={'videoSha256':hashlib.sha256(a.video.read_bytes()).hexdigest(),'seamMAD':mad,'threshold':12/255,'size':[v['width'],v['height']],'frames':int(v['nb_read_frames']),'fps':v['r_frame_rate'],'scope':'编码首尾像素；不能替代未遮罩世界、动作连续性或听感检查'}
 report['passed']=mad<12/255 and report['frames']==a.frames and report['size']==[a.width,a.height] and Fraction(report['fps'])==a.fps
 with a.out.open('x') as f:json.dump(report,f,ensure_ascii=False,indent=2)
 print(json.dumps(report,ensure_ascii=False))
 if not report['passed']:raise SystemExit(1)
if __name__=='__main__':main()
