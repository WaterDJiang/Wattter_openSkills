#!/usr/bin/env python3
"""Original cyclic postcard score; optional sound events share exact drawing frame times."""
import argparse,array,json,math,wave,sys
from pathlib import Path

def synth(style='music-box',sr=48000,duration=20,events=None):
    if style not in ('music-box','8bit','pentatonic'): raise ValueError('未知配乐风格')
    if not isinstance(duration,(int,float)) or not math.isfinite(duration) or duration<4 or duration>180: raise ValueError('片长须为4–180秒')
    n=round(duration*sr);signal=array.array('d',[0.0])*n
    notes=([72,74,76,79,81,79,76,74,69,72,74,76,79,76,74,67] if style=='pentatonic' else [72,76,79,83,79,76,74,71,69,72,76,79,76,72,71,67])
    for k,midi in enumerate(notes):
        start=round(k*duration/len(notes)*sr);freq=440*2**((midi-69)/12)
        for j in range(2*sr):
            t=j/sr;env=min(1,t/.008)*math.exp(-t*4)
            v=math.sin(2*math.pi*freq*t)
            if style=='8bit':v=(1 if v>=0 else -1)*.6+math.sin(2*math.pi*freq/2*t)*.25
            else:v+=.3*math.sin(2*math.pi*freq*2*t)+.12*math.sin(2*math.pi*freq*3*t)
            signal[(start+j)%n]+=.14*v*env
    if style=='pentatonic':
        # Quiet periodic synthetic breeze, not a recording from any named place.
        for j in range(n):
            phase=j/n;signal[j]+=.007*(math.sin(math.tau*137*phase)+.35*math.sin(math.tau*211*phase))* (.6+.4*math.sin(math.tau*phase)**2)
    for event in events or []:
        at=event['seconds'];typ=event['type'];start=round(at*sr)
        if not 0<=at<duration: raise ValueError('音效事件超出片长')
        if typ not in ('chirp','soft-step'): raise ValueError('未实现事件音效 '+str(typ))
        for j in range(round(sr*(.22 if typ=='chirp' else .12))):
            t=j/sr
            if typ=='chirp':v=math.sin(math.tau*(1300*t+2500*t*t))*.075*math.exp(-t*17)*min(1,t/.006)
            else:v=math.sin(math.tau*185*t)*.10*math.exp(-t*48)*min(1,t/.004)
            signal[(start+j)%n]+=v
    return array.array('h',(round(max(-.95,min(.95,x))*32767) for x in signal))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);p.add_argument('--style',choices=['music-box','8bit','pentatonic'],default='music-box');p.add_argument('--seconds',type=float,default=20);p.add_argument('--events',type=Path);a=p.parse_args()
    if a.output.exists():p.error('不覆盖已有声音；输出到新工程或素材候选目录')
    events=[]
    if a.events:
        event_doc=json.loads(a.events.read_text());fps=event_doc['fps']
        if not isinstance(fps,int) or fps<1: p.error('事件fps无效')
        if abs(event_doc['durationSeconds']-a.seconds)>1/48000:p.error('音效事件片长与配乐不符')
        events=event_doc['events']
        for e in events:
            if not isinstance(e.get('frame'),int) or abs(e['frame']/fps-e['seconds'])>1e-8:p.error('事件帧与秒不一致')
    samples=synth(a.style,duration=a.seconds,events=events)
    if sys.byteorder!='little':samples.byteswap()
    with a.output.open('xb') as f:
        with wave.open(f,'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(48000);w.writeframes(samples.tobytes())
    print(f'{a.seconds:g}秒 / 48000Hz / 原创循环合成，事件{len(events)}个；跨边界尾音已回绕，主观试听另验')
if __name__=='__main__':main()
