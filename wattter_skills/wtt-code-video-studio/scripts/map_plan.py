#!/usr/bin/env python3
"""Validate declared location research, then draw an ORIGINAL schematic composition. No fetching."""
import argparse,hashlib,html,json,math
from pathlib import Path
from urllib.parse import urlencode,urlsplit

TYPES={'landmark','river','road','greenery'}
RIGHTS={'user-owned','open-license','explicit-permission'}
def restricted_overview(s):
 host=urlsplit(s.get('url') or '').hostname or ''
 return s.get('provider') in ('google','baidu') or host=='google.com' or host.endswith('.google.com') or host=='map.baidu.com' or host.endswith('.map.baidu.com')

def validate(d):
 if d.get('schema')!='map-research/v1':raise ValueError('schema须为map-research/v1')
 place=d.get('place',{})
 for k in ('nameZh','nameEn','scope','season','orientation'):
  if not isinstance(place.get(k),str) or not place[k].strip():raise ValueError('缺地点/构图范围字段：'+k)
 if place['season'] not in ('春','夏','秋','冬'):raise ValueError('季节不明确')
 sources=d.get('sources',[]);ids=[s.get('id') for s in sources]
 if not sources or None in ids or len(ids)!=len(set(ids)):raise ValueError('来源为空或ID重复')
 source_map=dict(zip(ids,sources))
 if (place.get('latitude') is None)!=(place.get('longitude') is None):raise ValueError('经纬度必须成对提供')
 if place.get('latitude') is not None or place.get('longitude') is not None:
  if place.get('coordinateSystem') not in ('WGS84','GCJ-02','BD-09'):raise ValueError('坐标必须标注WGS84/GCJ-02/BD-09')
 overview=d.get('overview',{})
 if not d.get('fixture') and overview.get('status')!='viewed':raise ValueError('真实地点须先实际查看可用概览或授权本地替代图')
 if overview.get('status')=='viewed' and not all(overview.get(k) for k in ('provider','url','viewedAt','scopeNotes')):raise ValueError('实际概览记录不完整')
 if not isinstance(place.get('sourceIds'),list) or not place['sourceIds']:raise ValueError('地点范围须有关联依据')
 def derive(refs):
  if not isinstance(refs,list) or not refs:raise ValueError('构图内容缺少来源')
  for sid in refs:
   if sid not in source_map:raise ValueError('未知来源：'+str(sid))
   s=source_map[sid]
   if restricted_overview(s):raise ValueError('地图平台缩略图仅定位/许可展示，不进入提取或转绘构图链')
   if s.get('reviewed') is not True:raise ValueError('来源尚未实际核对：'+sid)
   if s.get('rightsStatus') not in RIGHTS or not s.get('license') or not s.get('useBasis'):raise ValueError('来源复用依据尚未明确：'+sid)
   if not s.get('url') and not s.get('localReference'):raise ValueError('来源缺URL或本地引用：'+sid)
 derive(place['sourceIds'])
 for key,max_value in [('latitude',90),('longitude',180)]:
  v=place.get(key)
  if v is not None and (isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or abs(v)>max_value):raise ValueError('无效坐标：'+key)
 elements=d.get('elements',[]);seen=set();landmarks=[]
 for e in elements:
  if e.get('id') in seen or not isinstance(e.get('id'),str):raise ValueError('构图对象ID缺失或重复')
  seen.add(e['id'])
  if e.get('type') not in TYPES or not e.get('name') or not e.get('reason'):raise ValueError('对象缺类型、名称或构图理由')
  derive(e.get('sourceIds'))
  b=e.get('box')
  if not isinstance(b,list) or len(b)!=4 or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in b):raise ValueError('box须为x/y/宽/高四数')
  x,y,w,h=b
  if min(x,y)<0 or min(w,h)<=0 or x+w>1080 or y+h>1440:raise ValueError('构图对象超出1080×1440世界')
  if e['type']=='landmark':
   if len(e.get('features',[]))<2 or not all(isinstance(v,str) and v.strip() for v in e['features']):raise ValueError('地标至少写出两个可辨识造型特征')
   if e.get('shape') not in ('tower','bridge','roof','block'):raise ValueError('地标草图形状须为tower/bridge/roof/block；正式场景另画真实特征')
   landmarks.append(e)
 if not landmarks:raise ValueError('缺少地方特色建筑')
 for i,a in enumerate(landmarks):
  ax,ay,aw,ah=a['box']
  for b in landmarks[i+1:]:
   bx,by,bw,bh=b['box']
   if max(ax,bx)<min(ax+aw,bx+bw) and max(ay,by)<min(ay+ah,by+bh):raise ValueError('地标构图互相重叠，先调整位置')
 if not d.get('geographyTreatment') or not d.get('loopTreatment') or not d.get('cameraRoute'):raise ValueError('缺地理取舍/循环接缝/镜头路线说明')
 return source_map

def generate(d):
 validate(d);escape=lambda s:html.escape(str(s),quote=True);p=d['place'];nodes=[]
 colors={'river':'#b6d6dc','road':'#e9e5d9','greenery':'#d6e4bc','landmark':'#ecc88d'}
 for e in sorted(d['elements'],key=lambda e:e['type']=='landmark'):
  x,y,w,h=e['box'];color=colors[e['type']]
  nodes.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{color}" stroke="#526c61" stroke-width="2"/>')
  if e.get('shape')=='tower':nodes.append(f'<path d="M {x+w*.25} {y+h*.8} L {x+w*.5} {y+h*.12} L {x+w*.75} {y+h*.8} Z" fill="#faf5e9" stroke="#526c61" stroke-width="3"/>')
  elif e.get('shape')=='roof':nodes.append(f'<path d="M {x+w*.12} {y+h*.45} Q {x+w*.5} {y-h*.1} {x+w*.88} {y+h*.45}" fill="none" stroke="#526c61" stroke-width="5"/>')
  elif e.get('shape')=='bridge':nodes.append(f'<path d="M {x+w*.1} {y+h*.8} Q {x+w*.5} {y-h*.3} {x+w*.9} {y+h*.8}" fill="none" stroke="#faf5e9" stroke-width="16"/>')
  nodes.append(f'<text x="{x+w/2}" y="{y+h-16}" text-anchor="middle" font-size="25">{escape(e["name"])}</text>')
 name=escape(p['nameZh']+' · '+p['season']);fixture='虚构夹具，未进行真实地点研究' if d.get('fixture') else '原创构图草案 · 非导航地图'
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1580" width="1080" height="1580"><rect width="1080" height="1580" fill="#FDFDF9"/><g font-family="sans-serif" fill="#314e45"><text x="40" y="48" font-size="30">{name}</text><text x="40" y="84" font-size="20">{fixture}</text><g transform="translate(0,110)">'+''.join(nodes)+'</g></g></svg>'
 from map_access import location_url
 overview=d.get('overview',{})
 provider=overview.get('provider','google')
 if provider not in ('google','baidu','local'):raise ValueError('overview.provider须为google/baidu/local')
 map_url=location_url(provider,p['nameZh']) if provider!='local' else overview['url']
 lines=['# 地点研究与构图草案','',fixture,'',f'地点：{p["nameZh"]} / {p["nameEn"]}；范围：{p["scope"]}；朝向：{p["orientation"]}。','',f'[{provider}地图定位入口]({map_url})（仅链接，未声称已获取缩略图）','',f'地理取舍：{d["geographyTreatment"]}',f'镜头路线：{d["cameraRoute"]}',f'循环处理：{d["loopTreatment"]}','','## 地标与构图理由','']
 for e in d['elements']:lines.append('- '+e['name']+'：'+e['reason']+'；可辨特征：'+'、'.join(e.get('features',[]))+'；依据：'+','.join(e['sourceIds']))
 lines+=['','## 研究来源','']
 for s in d['sources']:lines.append('- '+s['id']+'：'+(s.get('url') or s.get('localReference',''))+'；'+s.get('license','仅定位/展示')+'；'+s.get('useBasis',''))
 lines+=['','这是构图交接，尚未生成本地建筑动画。SVG中的tower/roof/bridge/block仅作占位，正式实现必须按已核对特征重画；地图模板不会自动读取此研究JSON。将本构图纳入原方案选择，已有方向不重复五选；源图/地标等已锁素材变化沿用diff审阅。','']
 return svg,'\n'.join(lines)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('research',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 if a.out.exists():p.error('输出须为新目录，不能覆盖已有构图或素材审阅')
 raw=a.research.read_bytes();d=json.loads(raw);svg,md=generate(d)
 a.out.mkdir(parents=True);(a.out/'composition.svg').write_text(svg);(a.out/'composition.md').write_text(md)
 (a.out/'handoff.json').write_text(json.dumps({'schema':'map-plan/v1','researchSha256':hashlib.sha256(raw).hexdigest(),'compositionSha256':hashlib.sha256(svg.encode()).hexdigest(),'researchFixture':bool(d.get('fixture')),'status':'draft','renderReady':False,'validationScope':'字段与关联完整性；不自动判断来源真假或法律授权'},ensure_ascii=False,indent=2))
 print('构图草案已输出；须实际查看并按已授权方案实现地标后继续渲染')
if __name__=='__main__':main()
