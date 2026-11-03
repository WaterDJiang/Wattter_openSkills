"""Original 12-second synthetic score and foley; no samples, no speech, fixed seed."""
from pathlib import Path
import numpy as np, wave, json, hashlib
ROOT=Path(__file__).resolve().parent.parent
# Only a newly scaffolded, unsealed demo may generate these first materials.
if not (ROOT/'tools/pipeline.py').is_file():
 raise RuntimeError('先运行 scripts/handpainted.py 新目录，禁止在Skill资源目录写素材')
from asset_review import has_history
if has_history(ROOT):
 raise RuntimeError('项目已有素材锁；音频变更须走候选/diff/确认，禁止覆盖')
existing=json.loads((ROOT/'assets.json').read_text())
if existing.get('assets') or existing.get('links'):
 raise RuntimeError('已有素材/导流记录，不能用示例合成覆盖')
OUT=ROOT/'audio'
if any((OUT/name).exists() for name in ['music.wav','foley.wav','composition.json']):
 raise RuntimeError('已有音频或制作记录；保留旧版并走候选审阅')
OUT.mkdir(exist_ok=True)
SR=48000; D=12; n=SR*D
r=np.random.default_rng(20261103)
music=np.zeros((n,2)); foley=np.zeros((n,2))
def add(arr,signal,start,pan=0):
 k=round(start*SR); length=min(len(signal),n-k)
 if length>0:arr[k:k+length,0]+=signal[:length]*np.sqrt((1-pan)/2);arr[k:k+length,1]+=signal[:length]*np.sqrt((1+pan)/2)
def note(midi,start,length=2.1,gain=.1,pan=0):
 t=np.arange(round(length*SR))/SR;f=440*2**((midi-69)/12)
 env=(1-np.exp(-t*65))*np.exp(-t*2.2)*(1-np.exp(-(length-t)*15))
 sig=(np.sin(2*np.pi*f*t)+.28*np.sin(2*np.pi*f*2*t)*np.exp(-t*3)+.12*np.sin(2*np.pi*f*3.003*t)*np.exp(-t*5))*env*gain
 add(music,sig,start,pan)
 for delay,amp in [(.13,.15),(.29,.08)]:add(music,sig*amp,start+delay,-pan)
# Harmonic bed: C / Am / F / G / C, soft sine partials, slow attack/release.
for start,chord in [(0,[48,55,60,64]),(3,[45,52,57,60]),(6,[41,48,53,57]),(9,[43,50,55,59])]:
 t=np.arange(SR*3)/SR;env=np.sin(np.pi*t/3)**1.3
 for j,m in enumerate(chord):
  f=440*2**((m-69)/12);sig=(np.sin(2*np.pi*f*t)+.15*np.sin(2*np.pi*f*2*t))*env*.027
  add(music,sig,start,(j-1.5)*.16)
for m,start in [(67,.35),(72,1.1),(76,1.85),(74,2.6),(72,3.35),(69,4.1),(72,4.85),(76,5.6),(77,6.35),(76,7.1),(72,7.85),(74,8.6),(71,9.35),(72,10.1)]:note(m,start,gain=.12 if start<6 else .14,pan=np.sin(start)*.25)
# Soft foot contacts (same gait cycle as the scene). Last contact is damped as walking stops.
contacts=[]
for k in range(9):
 start=k/(2*1.55)
 if start>2.65:break
 duration=.095;t=np.arange(round(duration*SR))/SR
 noise=r.normal(0,1,len(t));noise=np.convolve(noise,np.ones(21)/21,mode='same')
 env=np.exp(-t*48)*(1-np.exp(-t*450));sig=(noise*.25+np.sin(2*np.pi*(95-120*t)*t)*.15)*env
 add(foley,sig,start,-.2);contacts.append(start)
# Paper opening / wing flutter: filtered deterministic noise, synced to frame 185 release.
for start,gain in [(5.9,.045),(6.1666666667,.075),(6.4,.04),(6.64,.03),(6.88,.018)]:
 t=np.arange(round(.19*SR))/SR;noise=r.normal(0,1,len(t));low=np.convolve(noise,np.ones(9)/9,mode='same');sig=(noise-low)*np.sin(np.pi*t/.19)**2*gain;add(foley,sig,start,.05+(start-6)*.2)
fade=np.minimum(np.arange(n)/SR/.5,1)*np.minimum((n-1-np.arange(n))/SR/1.0,1)
for arr in [music,foley]:arr*=fade[:,None]
def save(name,arr):
 if np.max(np.abs(arr))>=.95:raise ValueError('clip risk')
 with (OUT/name).open('xb') as handle, wave.open(handle,'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes(np.round(arr*32767).astype('<i2').tobytes())
 return {'file':f'audio/{name}','sha256':hashlib.sha256((OUT/name).read_bytes()).hexdigest(),'samplePeak':float(np.max(np.abs(arr))),'durationSeconds':D}
result={'basis':'本片原创音符/正弦泛音/固定种子噪声；无外部采样，无声线克隆','sampleRate':SR,'seed':20261103,'footContactSeconds':contacts,'releaseFrame':185,'subjectiveListening':'not_checked','files':[save('music.wav',music),save('foley.wav',foley)]}
with (OUT/'composition.json').open('x') as handle:handle.write(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
assets={'schema':'code-animation-assets/v1','assets':[{'id':name,'path':file,'sourceUrl':None,'landingUrl':None,'license':'本片原创合成音频与制作记录；无第三方采样','useBasis':basis} for name,file,basis in [('original-score','audio/music.wav','原创和声、旋律及正弦泛音；配本片无对白角色动作'),('original-foley','audio/foley.wav','固定seed噪声合成脚步与纸翼；按角色步态/离手帧校时'),('composition-record','audio/composition.json','音符生成方法、采样率、动作锚点及文件哈希；不代表主观听感通过')]],'links':[]}
(ROOT/'assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
