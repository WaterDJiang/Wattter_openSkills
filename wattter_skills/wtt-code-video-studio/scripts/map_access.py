#!/usr/bin/env python3
"""Bounded Google/Baidu entry-page probes; no keys, screenshots, geocoding, or billing."""
import argparse,concurrent.futures,json,time,urllib.request
from datetime import datetime,timezone
from urllib.parse import quote,urlencode
PROVIDERS={'google':'https://www.google.com/maps','baidu':'https://map.baidu.com/'}

def location_url(provider,place):
 if provider=='google':return 'https://www.google.com/maps/search/?'+urlencode({'api':1,'query':place})
 if provider=='baidu':return 'https://map.baidu.com/search/'+quote(place,safe='')
 raise ValueError('未知地图供应商')

def probe(provider,timeout=4):
 start=time.monotonic()
 try:
  req=urllib.request.Request(PROVIDERS[provider],headers={'User-Agent':'WTT-Map-Reference-Check/1.0'})
  with urllib.request.urlopen(req,timeout=timeout) as response:
   body=response.read(65536).decode('utf-8',errors='replace').lower();status=response.status
  blocked=any(s in body for s in ('captcha','unusual traffic','安全验证','consent.google'))
  return {'provider':provider,'entryReachable':status==200 and not blocked,'httpStatus':status,'milliseconds':round((time.monotonic()-start)*1000),'reason':'verification-or-consent' if blocked else 'entry-response-only','mapLoaded':False}
 except Exception as e:
  return {'provider':provider,'entryReachable':False,'milliseconds':round((time.monotonic()-start)*1000),'reason':type(e).__name__+': '+str(e),'mapLoaded':False}

def choose(reports,preferred='auto'):
 if preferred not in ('auto',*PROVIDERS):raise ValueError('未知地图偏好')
 available=[r for r in reports if r['entryReachable']]
 if not available:return None,'both-unavailable-use-authorized-local-reference'
 selected=next((r for r in available if r['provider']==preferred),None)
 if selected:return selected['provider'],'preferred-entry-reachable-needs-browser'
 selected=min(available,key=lambda r:r['milliseconds'])
 return selected['provider'],'fastest-entry-needs-browser' if preferred=='auto' else 'preferred-unavailable-fallback-needs-browser'

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--place',required=True);p.add_argument('--preferred',choices=['auto','google','baidu'],default='auto');p.add_argument('--timeout',type=float,default=4);a=p.parse_args()
 if not 0<a.timeout<=10:p.error('timeout须在0到10秒之间')
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:reports=list(pool.map(lambda name:probe(name,a.timeout),PROVIDERS))
 candidate,reason=choose(reports,a.preferred)
 print(json.dumps({'checkedAt':datetime.now(timezone.utc).isoformat(),'preferred':a.preferred,'candidateProvider':candidate,'reason':reason,'mapConfirmed':False,'thumbnailAcquired':False,'reports':reports,'locationUrls':{name:location_url(name,a.place) for name in PROVIDERS}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
