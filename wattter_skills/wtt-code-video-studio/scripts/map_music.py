#!/usr/bin/env python3
"""Original 20s cyclic music box / 8bit synthesis; no external samples or private voice."""
import argparse,array,math,wave,sys
from pathlib import Path

def synth(style='music-box',sr=48000):
    n=20*sr;signal=array.array('d',[0.0])*n
    notes=[72,76,79,83,79,76,74,71,69,72,76,79,76,72,71,67]
    for k,midi in enumerate(notes):
        start=round(k*1.25*sr);freq=440*2**((midi-69)/12)
        for j in range(2*sr):
            t=j/sr;env=min(1,t/.008)*math.exp(-t*4)
            v=math.sin(2*math.pi*freq*t)
            if style=='8bit':v=(1 if v>=0 else -1)*.6+math.sin(2*math.pi*freq/2*t)*.25
            else:v+=.3*math.sin(2*math.pi*freq*2*t)+.12*math.sin(2*math.pi*freq*3*t)
            signal[(start+j)%n]+=.14*v*env
    return array.array('h',(round(max(-.95,min(.95,x))*32767) for x in signal))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);p.add_argument('--style',choices=['music-box','8bit'],default='music-box');a=p.parse_args()
    if a.output.exists():p.error('不覆盖已有声音；输出到新工程或素材候选目录')
    samples=synth(a.style)
    if sys.byteorder!='little':samples.byteswap()
    with a.output.open('xb') as f:
        with wave.open(f,'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(48000);w.writeframes(samples.tobytes())
    print('20秒 / 48000Hz / 原创循环合成，跨边界尾音已回绕；主观试听另验')
if __name__=='__main__':main()
