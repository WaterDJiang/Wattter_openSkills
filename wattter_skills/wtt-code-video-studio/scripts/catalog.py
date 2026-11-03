#!/usr/bin/env python3
"""Generate navigation and a portable local gallery from one catalog. No network."""
import argparse
import html
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def documents(root):
    data = json.loads((root/'config/capabilities.json').read_text())
    for collection in ('categories','styles','engines','samples'):
        ids = [x['id'] for x in data[collection]]
        if len(ids) != len(set(ids)): raise ValueError(f'{collection}: duplicate id')
    categories = {x['id']: x for x in data['categories']}
    styles = {x['id']: x for x in data['styles']}
    library=data.get('referenceLibrary')
    if library:
        index=json.loads((root/'config/reference-index.json').read_text())
        coverage=library['coverage']
        ids=[e['id'] for e in coverage]
        if library['commit']!=index['commit'] or len(ids)!=len(set(ids)) or set(ids)!=set(index['styleIds']):
            raise ValueError('参考风格覆盖不完整、重复或版本不一致')
        if {g['id'] for g in index['groups']}!={e['group'] for e in coverage}: raise ValueError('参考分组覆盖不完整')
        for entry in coverage:
            if entry['styleId'] not in styles: raise ValueError('参考条目缺少本库风格映射')
            if (root/entry['sourceFile']).is_file() and hashlib.sha256((root/entry['sourceFile']).read_bytes()).hexdigest()!=entry['localSourceSha256']: raise ValueError('固定来源文本哈希变化')
            style=styles[entry['styleId']]
            if entry['reference']!=style['reference']: raise ValueError('风格入口与参考映射不一致')
            for key in ('material','action','risk','inputs','engines','purposes'):
                if not style.get(key): raise ValueError('风格缺少具体方法：'+key)
            if not set(style['purposes'])<=set(categories): raise ValueError('未知用途')
            for field in ('reference','sourceFile'):
                if not (root/entry[field]).is_file(): raise ValueError('缺少风格方法文件：'+entry[field])
    for sample in data['samples']:
        if sample['category'] not in categories or sample['style'] not in styles: raise ValueError('unknown sample category/style')
        for key in ('source',):
            if not (root/sample[key]).is_file(): raise ValueError(f'missing {sample[key]}')
        if sample['status'] == 'rendered':
            for name in ('final.mp4','still.png','provenance.json'):
                if not (root/sample['project']/name).is_file(): raise ValueError(f'missing rendered evidence: {name}')
            manifest=json.loads((root/sample['project']/'provenance.json').read_text())
            digest=lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
            for name,expected in manifest['artifacts'].items():
                if digest(root/sample['project']/name)!=expected: raise ValueError(f'样片证据哈希变化：{sample["id"]}/{name}')
            if digest(root/sample['source'])!=manifest['sourceSha256']: raise ValueError('样片源码哈希变化')
            report=json.loads((root/sample['project']/'delivery-check.json').read_text())
            if not report.get('passed') or report['durationSeconds']!=sample['durationSeconds']:
                raise ValueError('样片技术检查或时长与目录不一致')
            if report['finalSha256']!=digest(root/sample['project']/'final.mp4'): raise ValueError('样片检查未绑定当前成片')
    lines=['# 分类路径与能力状态','','由 `config/capabilities.json` 生成；修改元数据后运行 `python3 scripts/catalog.py build`。','','## 按目的找到制作路径','','| 目的 | 形式（可组合） | 输入示例 | 方法 |','|---|---|---|---|']
    for c in data['categories']:
        lines.append(f"| **{c['name']}**：{c['goal']} | {' / '.join(c['forms'])} | {c['prompt']} | [配方]({Path(c['reference']).name}) |")
    lines += ['','路径：**想法/材料 → 主用途 → 内容与脚本 → 五种完整方向（形式+策略+画风） → 用户决定 → 代码实现 → MP4及验收**。','', '分类用于浏览和自动路由，不是新加的开场选择。文字/静态SVG/交互HTML可从知识解释分支直接交付。','', '## 视觉风格（与用途自由组合）','','| ID | 风格 | 基础状态 |','|---|---|---|']
    for style in data['styles']: lines.append(f"| `{style['id']}` | [{style['name']}]({Path(style['reference']).relative_to('references').as_posix()}) | {'起步模板；按内容重画' if style['status']=='template' else '方法已收录；本片须实现验证'} |")
    if library:
        lines += ['', '## 完整参考目录覆盖', '', f"固定版本：`{library['commit']}`；参考11组66条全部映射，本库去重后共{len(styles)}项（含{sum(s.get('group')=='local' for s in data['styles'])}项本库补充），上面的6类是用途。", '', '| 参考组 | 数量 | 本地方法入口 |', '|---|---|---|']
        for group in index['groups']:
            members=[e for e in library['coverage'] if e['group']==group['id']]
            links='、'.join(f"[{e['name']}]({Path(e['reference']).relative_to('references').as_posix()})" for e in members)
            lines.append(f"| {group['name']} | {len(members)} | {links} |")
        lines += ['', '查看[可筛选风格库](../assets/gallery/styles.html)。SOURCE.md保留带MIT归属的完整方法，STYLE.md为本库中文适配。方法收录不等于每条都完成本库原创视频验证；当前实测样片仍为6个。', '']
    lines += ['','长篇画法见[风格配方](style-catalog.md)。具体样例状态独立列于下面，不能从一个样例推广到整类能力。','','## 技术选项','','| 技术 | 状态 | 用途与边界 |','|---|---|---|']
    for e in data['engines']: lines.append(f"| {e['id']} | {e['status']} | {e['use']} |")
    lines += ['','**有 Three.js 路线**，但当前内置逐帧底座和本轮六例均为 Canvas；Three.js/p5.js/Remotion 等需要为具体镜头接入、检查确定性和渲染，不能当作已安装即用的全部后端。','','## 新制样片','','| 用途 | 作品 | 风格 | 秒数 | 状态 |','|---|---|---|---|---|']
    cards=[]
    for s in data['samples']:
        folder='../'+s['project']
        lines.append(f"| {categories[s['category']]['name']} | [{s['title']}]({folder}/DEMO.md) | {styles[s['style']]['name']} | {s['durationSeconds']} | {s['status']} |")
        media='../examples/'+s['id']
        cards.append(f'''<article data-category="{s['category']}"><div class="media"><video controls preload="none" poster="{media}/still.png" src="{media}/final.mp4"></video></div><p class="tag">{html.escape(categories[s['category']]['name'])} · {s['durationSeconds']}秒</p><h2>{html.escape(s['title'])}</h2><p>{html.escape(styles[s['style']]['name'])} · {s['status']}</p><p><a href="{media}/DEMO.md">内容 / 复跑 / 边界</a> · <a href="{media}/still.png">静帧</a> · <a href="{media}/provenance.json">来源与哈希</a></p></article>''')
    lines += ['','打开[本地画廊](../assets/gallery/index.html)浏览视频和静帧。`rendered`仅表示真实生成并有技术证据；视觉/试听/用户采用详见每片报告。纪实/产品/数据样例含明确标注的虚构或示例内容。','']
    page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>代码视频工作室 · 原创样片</title><style>*{box-sizing:border-box}body{margin:0;background:#f3f0e9;color:#152b36;font-family:system-ui,"PingFang SC",sans-serif}header,main,footer{max-width:1320px;margin:auto;padding:42px 5vw}header{padding-top:70px;padding-bottom:20px}.eyebrow{letter-spacing:3px;font-size:13px;color:#426964}h1{font-size:clamp(34px,5vw,64px);letter-spacing:-2px;margin:16px 0}header p{max-width:800px;line-height:1.8;color:#53656b}nav{display:flex;gap:8px;flex-wrap:wrap;margin-top:26px}button{border:1px solid #becac6;border-radius:30px;background:transparent;padding:10px 18px;color:inherit;cursor:pointer}button[aria-pressed=true]{background:#153b37;color:white}main{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:30px;padding-top:12px}article{background:#fffdf8;border:1px solid #dce0d7;padding:16px;border-radius:18px}article[hidden]{display:none}.media{overflow:hidden;border-radius:10px;background:#14282e}video{display:block;width:100%;aspect-ratio:16/9}h2{font-size:24px;margin:8px 0}.tag{font-size:13px;color:#577465;letter-spacing:1px}article p{line-height:1.6}a{color:#176e67}footer{font-size:14px;line-height:1.9}@media(max-width:760px){main{grid-template-columns:1fr}}</style><header><div class="eyebrow">WTT / CODE VIDEO STUDIO</div><h1>从一个想法，到一段会动的表达。</h1><p>六条制作路径，同一套代码管线。这里的图形、故事、数据和事件音均为本轮新作；没有搬运参考项目的演示媒体。短片展示方法，不代表整类视频都能套模板完成。</p><nav><button data-filter="all" aria-pressed="true">全部</button>'''
    page+=''.join(f'<button data-filter="{c["id"]}" aria-pressed="false">{c["name"]}</button>' for c in data['categories'])
    page+='</nav></header><main>'+''.join(cards)+'</main><footer>真实渲染 ≠ 全部视觉验收 ≠ 用户采用。声音为代码生成事件音，无人声。纪实样例使用虚构事件；数据与产品均为示例。<br><a href="../../references/classification.md">完整分类与技术状态</a> · <a href="../../README.md">使用说明</a></footer><script>document.querySelectorAll("button[data-filter]").forEach(b=>b.onclick=()=>{document.querySelectorAll("button[data-filter]").forEach(x=>x.setAttribute("aria-pressed",x===b));document.querySelectorAll("article").forEach(a=>a.hidden=b.dataset.filter!=="all"&&a.dataset.category!==b.dataset.filter)});</script></html>'
    page=page.replace('<nav>','<p><a href="styles.html">浏览完整风格库：11参考组66条＋本库补充</a></p><nav>')
    options=lambda items: ''.join('<option value="'+html.escape(i['id'])+'">'+html.escape(i['name'])+'</option>' for i in items)
    cards=[]
    for style in data['styles']:
        search=' '.join([style['name'],style.get('en',''),style['id'],style.get('material',''),' '.join(style.get('aliases',[]))]).lower()
        cards.append('<article data-group="'+style.get('group','local')+'" data-purposes="'+','.join(style.get('purposes',[]))+'" data-search="'+html.escape(search,quote=True)+'"><h2>'+html.escape(style['name'])+'</h2><p>'+html.escape(style.get('material','本库原有组合画法，按片实现。'))+'</p><p>'+html.escape(style.get('action','按内容设计动作。'))+'</p><a href="../../'+style['reference']+'">方法与验收</a><small>方法配方 · 按本片验证</small></article>')
    stylepage='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>完整风格库 · 代码视频</title><style>body{max-width:1280px;margin:40px auto;padding:0 22px;background:#f3f0e9;color:#163a3c;font:17px system-ui}input,select{font:inherit;padding:10px;max-width:100%;margin:8px 4px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(290px,100%),1fr));gap:16px}article{padding:20px;background:#fffdf8;border:1px solid #d6ded4;border-radius:12px}article[hidden]{display:none}p{line-height:1.7}a{color:#176e67}small{display:block;margin-top:12px;color:#61726b}h2{font-size:22px}</style><h1>完整风格库</h1><p>11参考组66条方法已完整收录，加本库补充共STYLE_COUNT项。按用途、组别或关键词查找；新吸收方法尚未逐条在本库制作成片。</p><label>搜索<input id="query" placeholder="例如 水墨 / 纪录片 / 3D"></label><label>用途<select id="purpose"><option value="">全部用途</option>'''+options(data['categories'])+'</select></label><label>风格组<select id="group"><option value="">全部组别</option>'+options(data.get('styleGroups',[]))+'</select></label><p id="count"></p><main>'+''.join(cards)+'''</main><p><a href="index.html">原创样片</a> · <a href="../../references/classification.md">分类与技术状态</a></p><script>function update(){const q=document.querySelector('#query').value.toLowerCase(),p=document.querySelector('#purpose').value,g=document.querySelector('#group').value;let n=0;document.querySelectorAll('article').forEach(a=>{a.hidden=!!(q&&!a.dataset.search.includes(q)||p&&!a.dataset.purposes.split(',').includes(p)||g&&a.dataset.group!==g);if(!a.hidden)n++});document.querySelector('#count').textContent=n+' 项可浏览方法';}document.querySelectorAll('input,select').forEach(e=>e.addEventListener('input',update));update();</script></html>'''
    stylepage=stylepage.replace('STYLE_COUNT',str(len(styles)))
    return {'references/classification.md':'\n'.join(lines),'assets/gallery/index.html':page,'assets/gallery/styles.html':stylepage}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['build','check','list']);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--purpose');p.add_argument('--query',default='');a=p.parse_args()
    if a.command=='list':
        data=json.loads((a.root/'config/capabilities.json').read_text());
        if a.purpose and a.purpose not in {c['id'] for c in data['categories']}: p.error('未知用途')
        rows=[s for s in data['styles'] if (not a.purpose or a.purpose in s.get('purposes',[])) and a.query.lower() in (s['id']+' '+s['name']+' '+s.get('en','')+' '+s.get('material','')+' '+' '.join(s.get('aliases',[]))).lower()]
        print(json.dumps(rows,ensure_ascii=False,indent=2));return
    for name,content in documents(a.root).items():
        file=a.root/name
        if a.command=='build': file.parent.mkdir(parents=True,exist_ok=True);file.write_text(content,encoding='utf-8')
        elif not file.exists() or file.read_text()!=content: raise SystemExit(f'目录过期：{name}；运行 catalog.py build')
    print('目录与元数据一致' if a.command=='check' else '已生成分类与画廊')
if __name__=='__main__': main()
