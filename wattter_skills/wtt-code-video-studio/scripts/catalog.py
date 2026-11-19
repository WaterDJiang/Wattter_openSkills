#!/usr/bin/env python3
"""Generate navigation and a portable local gallery from one catalog. No network."""
import argparse
import html
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def validate_frontend_libraries(data):
    if data.get('schema') != 'code-video-frontend-libraries/v1':
        raise ValueError('前端库目录schema错误')
    import datetime
    try:
        datetime.date.fromisoformat(data['checkedOn'])
    except (KeyError, TypeError, ValueError):
        raise ValueError('前端库缺少核实日期') from None
    ids = set()
    for row in data.get('libraries', []):
        if not row.get('id') or row['id'] in ids:
            raise ValueError('前端库ID缺失或重复')
        ids.add(row['id'])
        for key in ('name', 'role', 'needs', 'limits', 'frameAdapter'):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError('前端库缺少'+key)
        for key in ('capabilities', 'aliases', 'sourceUrls'):
            if not isinstance(row.get(key), list) or not row[key] or not all(isinstance(x,str) and x.strip() for x in row[key]):
                raise ValueError('前端库缺少'+key)
        if not all(x.startswith('https://') for x in row['sourceUrls']):
            raise ValueError('前端库必须记录官方HTTPS来源')
        if row.get('verification') != 'research-only' or row.get('pinnedVersion') is not None:
            raise ValueError('研究目录不能冒充已实装或已锁定版本')
    routes = set()
    for route in data.get('routes', []):
        if not route.get('id') or route['id'] in routes:
            raise ValueError('路线ID缺失或重复')
        routes.add(route['id'])
        for key in ('name', 'when', 'inputs', 'notFor'):
            if not isinstance(route.get(key), str) or not route[key].strip():
                raise ValueError('路线缺少'+key)
        groups = [route.get(k) for k in ('primaryIds','optionalIds','alternativeIds')]
        if any(not isinstance(g,list) for g in groups) or not groups[0]:
            raise ValueError('路线缺少主选/可选/替代库列表')
        members = [x for g in groups for x in g]
        if len(set(members)) != len(members) or not set(members) <= ids:
            raise ValueError('路线引用未知或重复库')
    if not ids or not routes:
        raise ValueError('前端库与路线不能为空')


def frontend_libraries(root):
    data = json.loads((root/'config/frontend-libraries.json').read_text())
    validate_frontend_libraries(data)
    return data


def select_libraries(data, query='', route=None):
    validate_frontend_libraries(data)
    chosen = next((r for r in data['routes'] if r['id']==route), None) if route else None
    if route and chosen is None:
        raise ValueError('未知技术路线：'+route)
    roles = {x:role for role,key in [('primary','primaryIds'),('optional','optionalIds'),('alternative','alternativeIds')]
             for x in (chosen[key] if chosen else [])}
    return [dict(row, routeRole=roles[row['id']]) if chosen else dict(row)
            for row in data['libraries']
            if (not chosen or row['id'] in roles)
            and query.casefold() in json.dumps(row,ensure_ascii=False).casefold()]


def frontend_library_document(data):
    validate_frontend_libraries(data)
    lines = ['# 前端代码库与地理路线', '', '由config/frontend-libraries.json生成；修改元数据后运行catalog.py build。', '',
             f"官方功能核实日期：{data['checkedOn']}。{data['scope']}。{data['adoption']}。", '',
             '图片生成/二维/三维的决策与接入步骤见[地理叙事](geographic-storytelling.md)；旧画法状态见[画法适配](visual-recipes.md)。', '',
             '## 内容对应路线', '', '| route | 内容与选择 | 主选 | 可选 | 替代 | 输入与不适用 |', '|---|---|---|---|---|---|']
    for r in data['routes']:
        lines.append(f"| `{r['id']}` | {r['name']}：{r['when']} | {', '.join(r['primaryIds'])} | {', '.join(r['optionalIds']) or '无'} | {', '.join(r['alternativeIds']) or '无'} | {r['inputs']}；不适用：{r['notFor']} |")
    lines += ['', '主选/可选/替代不是整套必须安装；确定路线后只准备本片必需库。下列均为research-only，未完成新的后端渲染验证。', '']
    for r in data['libraries']:
        lines += [f"## {r['name']}（{r['id']}）", '', f"职责：{r['role']}。能力：{'；'.join(r['capabilities'])}。", '',
                  f"输入：{r['needs']}。边界：{r['limits']}。", '', f"接入帧契约：{r['frameAdapter']}。", '',
                  '官方来源：'+'、'.join(f'[文档{i+1}]({url})' for i,url in enumerate(r['sourceUrls'])), '']
    return '\n'.join(lines)

def validate_use_cases(data):
    """Editorial mappings must not invent rendered evidence."""
    if 'useCases' not in data:
        return
    cases = data['useCases']
    if not isinstance(cases, list) or not cases:
        raise ValueError('用法映射不能为空；旧元数据可不含useCases字段')
    styles = {s['id'] for s in data['styles']}
    purposes = {c['id'] for c in data['categories']}
    samples = {s['id']: s for s in data['samples']}
    ids, aliases, covered = set(), {}, set()
    def required(value, label):
        if not isinstance(value, str) or not value.strip():
            raise ValueError('用法映射缺少'+label)
    for case in cases:
        cid = case['id']
        if cid in ids:
            raise ValueError('useCases: duplicate id')
        ids.add(cid)
        for key in ('id', 'name', 'goal', 'structure'):
            required(case.get(key), key)
        if not case.get('purposes') or not set(case['purposes']) <= purposes:
            raise ValueError('用法映射包含未知用途')
        for key in ('aliases', 'needs'):
            if not isinstance(case.get(key), list) or not case[key]:
                raise ValueError('用法映射缺少'+key)
            for value in case[key]:
                required(value, key)
        for alias in [cid, case['name'], *case['aliases']]:
            key = alias.strip().casefold()
            if key in aliases and aliases[key] != cid:
                raise ValueError('用法别名冲突：'+alias)
            aliases[key] = cid
        if not case.get('matches'):
            raise ValueError('用法映射缺少风格候选')
        seen = set()
        for match in case['matches']:
            sid = match['styleId']
            if sid not in styles:
                raise ValueError('用法映射引用未知风格：'+sid)
            if sid in seen:
                raise ValueError('用法风格映射重复：'+cid+'/'+sid)
            seen.add(sid); covered.add(sid)
            if match.get('fit') not in ('primary', 'conditional'):
                raise ValueError('未知匹配条件：'+sid)
            required(match.get('why'), '推荐理由')
            if not isinstance(match.get('conditions'), list) or not match['conditions']:
                raise ValueError('用法映射缺少适用条件')
            for value in match['conditions']:
                required(value, '适用条件')
            example = match.get('example', {})
            if example.get('status') != 'concept':
                raise ValueError('样例构想不能冒充已渲染样片')
            for key in ('title', 'keyShot'):
                required(example.get(key), '示例'+key)
            evidence = match.get('evidenceSampleIds', [])
            if not isinstance(evidence, list) or len(evidence) != len(set(evidence)):
                raise ValueError('样片证据引用重复或格式错误')
            for sample_id in evidence:
                sample = samples.get(sample_id)
                if not sample or sample['style'] != sid or sample['category'] not in case['purposes'] or sample['status'] != 'rendered':
                    raise ValueError('样片证据与用法/风格不匹配：'+sample_id)
    if covered != styles:
        raise ValueError('用法映射漏覆盖风格：'+', '.join(sorted(styles-covered)))


def use_case_matches(data, style_id, case_id=None):
    return [dict(m, useCaseId=c['id'], useCaseName=c['name'])
            for c in data.get('useCases', []) if not case_id or c['id'] == case_id
            for m in c['matches'] if m['styleId'] == style_id]


def validate_reference_cases(data):
    cases = data.get('referenceCases', [])
    if 'referenceCases' in data and (not isinstance(cases, list) or not cases):
        raise ValueError('研究案例不能为空')
    use_cases = {c['id']: c for c in data.get('useCases', [])}
    engines = {e['id'] for e in data['engines']}
    ids = set()
    for case in cases:
        cid = case['id']
        if cid in ids:
            raise ValueError('研究案例ID重复：'+cid)
        ids.add(cid)
        if case.get('verification') != 'research-only':
            raise ValueError('研究案例不能冒充本库已渲染样片')
        if case.get('outputKind') not in ('video', 'interactive-demo', 'hybrid-video', 'mixed-footage'):
            raise ValueError('未知作品形态：'+cid)
        if not case.get('useCases') or not set(case['useCases']) <= set(use_cases):
            raise ValueError('研究案例引用未知用法：'+cid)
        if not set(case.get('suggestedEngines', [])) <= engines:
            raise ValueError('复现建议引用未知引擎：'+cid)
        for key in ('id', 'title', 'selectionReason'):
            if not isinstance(case.get(key), str) or not case[key].strip():
                raise ValueError('研究案例缺少'+key)
        for key in ('reportedTechnology', 'unknownTechnology', 'evidence'):
            if not isinstance(case.get(key), list) or not case[key]:
                raise ValueError('研究案例缺少'+key)
        if not case.get('originalUrl', '').startswith('https://'):
            raise ValueError('研究案例缺少原始URL')
        for evidence in case['evidence']:
            if evidence.get('level') not in ('source-inspected', 'author-article', 'relayed-author', 'index-only'):
                raise ValueError('未知案例证据等级')
            if not evidence.get('url', '').startswith('https://') or not evidence.get('finding', '').strip():
                raise ValueError('研究案例缺少证据URL或依据')
        heat = case.get('attention', {})
        views = heat.get('views')
        if views is None:
            if heat.get('basis') != 'not-verified' or heat.get('sourceUrl') is not None:
                raise ValueError('未核实热度不能保留已核实标记')
        elif type(views) is not int or views < 0 or heat.get('basis') != 'index-snapshot' or not heat.get('sourceUrl', '').startswith('https://') or not heat.get('metricAsOf') or not heat.get('retrievedAt'):
            raise ValueError('热度数字缺少来源、日期或快照口径')
    for use_case in use_cases.values():
        refs = use_case.get('referenceCaseIds', [])
        if len(refs) != len(set(refs)) or not set(refs) <= ids:
            raise ValueError('用法引用未知或重复研究案例')
        expected = {c['id'] for c in cases if use_case['id'] in c['useCases']}
        if set(refs) != expected:
            raise ValueError('案例与用法反向引用不一致')


def select_reference_cases(data, purpose=None, query='', use_case=None):
    validate_reference_cases(data)
    cid = resolve_use_case(data, use_case) if use_case else None
    categories = {c['id'] for c in data['categories']}
    if purpose and purpose not in categories:
        raise ValueError('未知用途：'+purpose)
    purpose_cases = {c['id'] for c in data.get('useCases', []) if not purpose or purpose in c['purposes']}
    return [c for c in data.get('referenceCases', [])
            if (not cid or cid in c['useCases']) and set(c['useCases']) & purpose_cases
            and query.casefold() in ' '.join([c['id'], c['title'], *c['reportedTechnology'], *c['unknownTechnology']]).casefold()]


def resolve_use_case(data, value):
    key = value.strip().casefold()
    for case in data.get('useCases', []):
        if key in {x.casefold() for x in [case['id'], case['name'], *case['aliases']]}:
            return case['id']
    raise ValueError('未知用法：'+value+'；运行 catalog.py use-cases 查看入口')


def search_text(data, style):
    matches = use_case_matches(data, style['id'])
    cases = {m['useCaseId'] for m in matches}
    extra = [x for c in data.get('useCases', []) if c['id'] in cases for x in [c['name'], *c['aliases']]]
    extra += [x for m in matches for x in [m['why'], m['example']['title'], m['example']['keyShot']]]
    return ' '.join([style['id'], style.get('sourceId',''), style['name'], style.get('en', ''), style.get('material', ''), *style.get('aliases', []), *extra]).casefold()


def select_styles(data, purpose=None, query='', use_case=None):
    validate_use_cases(data)
    validate_reference_cases(data)
    cid = resolve_use_case(data, use_case) if use_case else None
    if purpose and purpose not in {c['id'] for c in data['categories']}:
        raise ValueError('未知用途：'+purpose)
    result = []
    for style in data['styles']:
        matches = use_case_matches(data, style['id'], cid)
        if (purpose and purpose not in style.get('purposes', [])) or (cid and not matches) or query.casefold() not in search_text(data, style):
            continue
        result.append(dict(style, useCaseMatches=matches) if cid else style)
    return result


def style_summary(style):
    """Discovery view: keep source facts; do not invent missing legacy fields."""
    result = {key: style[key] for key in ('id', 'name', 'status', 'material', 'action', 'reference')
              if key in style}
    if 'useCaseMatches' in style:
        result['useCaseMatches'] = [
            {key: match[key] for key in ('useCaseId', 'fit', 'why', 'conditions')}
            for match in style['useCaseMatches']]
    return result


def style_detail(data, style_id, use_case=None):
    """One chosen candidate, with only the requested topic's matches when given."""
    cid = resolve_use_case(data, use_case) if use_case else None
    style = next((s for s in data['styles'] if s['id'] == style_id or s.get('sourceId') == style_id), None)
    if style is None:
        raise ValueError('未知风格ID：'+style_id)
    style_id = style['id']
    matches = use_case_matches(data, style_id, cid)
    if cid and not matches:
        raise ValueError('该风格没有此用法映射：'+style_id+'/'+cid)
    result = dict(style, useCaseMatches=matches)
    coverage = data.get('referenceLibrary', {}).get('coverage', [])
    source = next((e for e in coverage if e['styleId'] == style_id), None)
    if source:
        result['sourceFile'] = source['sourceFile']
    if style.get('engines'):
        result['engineStates'] = [e for e in data['engines'] if e['id'] in style['engines']]
    return result


def discovery_rows(rows, command, view='full', limit=None, offset=None):
    """Opt-in summaries/pagination leave legacy full-array output untouched."""
    if limit is not None and limit < 1:
        raise ValueError('limit须为正整数')
    if offset is not None and offset < 0:
        raise ValueError('offset须为非负整数')
    total = len(rows)
    if view == 'summary':
        if command == 'list':
            rows = [style_summary(row) for row in rows]
        elif command == 'use-cases':
            rows = [{k: row[k] for k in ('id', 'name', 'purposes', 'goal')} for row in rows]
        elif command == 'cases':
            rows = [{k: row[k] for k in ('id', 'title', 'verification', 'outputKind', 'useCases',
                                         'selectionReason', 'originalUrl')} for row in rows]
    if limit is None and offset is None:
        return rows
    start = offset or 0
    selected = rows[start:] if limit is None else rows[start:start+limit]
    return {'total': total, 'offset': start, 'returned': len(selected),
            'hasMore': start+len(selected) < total,
            'order': 'catalog-order-not-recommendation', 'items': selected}


def mapping_document(data):
    styles = {s['id']: s for s in data['styles']}
    samples = {s['id']: s for s in data['samples']}
    esc = lambda text: str(text).replace('|', '\\|').replace('\n', ' ')
    lines = ['# 主题用法与风格映射', '',
             '由 `config/capabilities.json` 的 useCases 生成。用法与风格多对多；六个主用途和现有风格ID不变。', '',
             '## 怎么使用', '',
             '先识别内容目标、受众、事实/虚构和素材条件，再检索用法；交叉题材可取多个入口。候选是检索起点，模型结合本片脚本重新推荐五个完整方向，由用户决定。主匹配不是自动选中，有条件匹配不代表已具备依赖。风格决定后先展示四张真实样帧拼图，用户确认后才完整渲染；已指定画风不重复五选，仍需四帧审片。', '',
             '每条示例均为**原创样例构想，未渲染**；另列的同风格工程样片只证明其已有实现范围，不证明该构想、题材效果或全目录均已验证。', '',
             '```sh', 'python3 scripts/catalog.py use-cases --view summary', 'python3 scripts/catalog.py list --use-case 广告 --view summary',
             'python3 scripts/catalog.py show desktop-flythrough --use-case 个人宣传',
             'python3 scripts/catalog.py list --use-case 浪漫电影 --query 水彩', '```', '',
             '## 用法入口', '', '| 用法 | 主用途 | 内容目标 | 结构起点 | 候选数 |', '|---|---|---|---|---|']
    categories = {c['id']: c['name'] for c in data['categories']}
    for case in data['useCases']:
        lines.append(f"| [{case['name']}](#{case['id']}) | {' / '.join(categories[p] for p in case['purposes'])} | {esc(case['goal'])} | {esc(case['structure'])} | {len(case['matches'])} |")
    for case in data['useCases']:
        lines += ['', f'<a id="{case["id"]}"></a>', '', f"## {case['name']}", '',
                  '检索：`'+case['id']+'`；别名：'+'、'.join(case['aliases'])+'。', '',
                  '内容/素材条件：'+'；'.join(case['needs'])+'。', '',
                  '| 风格 / 匹配 | 为什么适合 | 样例构想（未渲染）与关键镜头 | 条件 / 已有工程证据 |', '|---|---|---|---|']
        for m in case['matches']:
            style = styles[m['styleId']]
            link = Path(style['reference']).relative_to('references').as_posix()
            evidence = '；'.join(f"[同风格工程样片：{samples[s]['title']}](../{samples[s]['project']}/DEMO.md)" for s in m['evidenceSampleIds'])
            lines.append(f"| [{style['name']}]({link}) / {'主匹配' if m['fit']=='primary' else '有条件'} | {esc(m['why'])} | **{esc(m['example']['title'])}**：{esc(m['example']['keyShot'])} | {esc('；'.join(m['conditions']))}"+('；'+evidence if evidence else '')+' |')
        refs = case.get('referenceCaseIds', [])
        if refs:
            research = {c['id']: c for c in data['referenceCases']}
            lines += ['', '外部研究案例（非本库成片验收）：'+'、'.join(f"[{research[cid]['title']}](production-cases.md#{cid})" for cid in refs)+'。']
    lines += ['', f'## 反向查询：{len(styles)}种风格适合哪些用法', '', '| ID / 风格 | 可匹配用法 |', '|---|---|']
    for style in data['styles']:
        links = '、'.join(f"[{m['useCaseName']}](#{m['useCaseId']})"+('（有条件）' if m['fit']=='conditional' else '') for m in use_case_matches(data, style['id']))
        lines.append(f"| `{style['id']}` / {style['name']} | {links} |")
    return '\n'.join(lines)+'\n'


def reference_case_document(data):
    labels = {'source-inspected':'源码已查看', 'author-article':'作者制作记录', 'relayed-author':'作者陈述的公开转引', 'index-only':'索引描述'}
    kinds = {'video':'视频', 'interactive-demo':'交互作品的演示', 'hybrid-video':'生成素材与代码混合', 'mixed-footage':'原视频与代码补画'}
    uses = {c['id']: c['name'] for c in data['useCases']}
    lines = ['# 外部作品与技术依据', '', '由config/capabilities.json的referenceCases生成。只存研究信息，不搬运媒体；均为research-only，不是本库渲染验收。', '',
             '热度来自注明来源的索引快照，不是实时播放量、全网排名或效果保证。作者未公开或本次未读到的库保持未知；复现建议与原片实际技术分开。选择时配合[案例驱动选型](case-driven-techniques.md)和[用法映射](use-case-mapping.md)。', '',
             '```sh', 'python3 scripts/catalog.py cases --use-case 概念解释', 'python3 scripts/catalog.py cases --query p5', '```', '',
             '| 案例 | 形态 | 对应用法 | 关注依据 |', '|---|---|---|---|']
    for c in data['referenceCases']:
        a=c['attention'];heat=f"{a['views']:,}次播放（索引快照）" if a['views'] is not None else '未核实热度；技术/用法参考'
        lines.append(f"| [{c['title']}](#{c['id']}) | {kinds[c['outputKind']]} | {' / '.join(uses[x] for x in c['useCases'])} | {heat} |")
    for c in data['referenceCases']:
        a=c['attention']
        lines += ['', f'<a id="{c["id"]}"></a>', '', '## '+c['title'], '', f"[原作或作者入口]({c['originalUrl']})。{c['selectionReason']}。", '',
                  '- 已披露或可查的做法：'+'；'.join(c['reportedTechnology'])+'。',
                  '- 尚不确定：'+'；'.join(c['unknownTechnology'])+'。',
                  '- 本库复现候选：'+(' / '.join(c['suggestedEngines']) if c['suggestedEngines'] else '独立外部渲染路线，按指南评估')+'；不是原片依赖认定或已适配声明。']
        if a['views'] is not None:
            lines.append(f"- [热度来源]({a['sourceUrl']})：{a['views']:,}次播放；指标日期：{a['metricAsOf']}；检索日期：{a['retrievedAt']}。")
        lines += ['']+[f"- [{labels[e['level']]}]({e['url']})：{e['finding']}。" for e in c['evidence']]
    return '\n'.join(lines)+'\n'

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
    validate_use_cases(data)
    validate_reference_cases(data)
    lines=['# 分类路径与能力状态','','由 `config/capabilities.json` 生成；修改元数据后运行 `python3 scripts/catalog.py build`。','','## 按目的找到制作路径','','| 目的 | 形式（可组合） | 输入示例 | 方法 |','|---|---|---|---|']
    for c in data['categories']:
        lines.append(f"| **{c['name']}**：{c['goal']} | {' / '.join(c['forms'])} | {c['prompt']} | [配方]({Path(c['reference']).name}) |")
    lines += ['','路径：**想法/材料 → 主用途 → 内容与脚本 → 五种完整方向（形式+策略+画风） → 风格决定 → 代码样帧 → 四帧拼图确认 → 完整渲染及验收**。','', '分类用于浏览和自动路由，不是新加的开场选择。已指定画风跳过五选，仍须四帧审片；文字/静态SVG/交互HTML可从知识解释分支直接交付。','', '## 视觉风格（与用途自由组合）','','| ID | 风格 | 基础状态 |','|---|---|---|']
    for style in data['styles']: lines.append(f"| `{style['id']}` | [{style['name']}]({Path(style['reference']).relative_to('references').as_posix()}) | {'起步模板；按内容重画' if style['status']=='template' else '方法已收录；本片须实现验证'} |")
    if library:
        groups = index.get('archive', {}).get('groups', [])
        sourced = [s for s in styles.values() if s.get('sourceId')]
        by_source = {s['sourceId']: s for s in sourced}
        if len(sourced) != len(by_source) or (any('continuityAnchor' in s for s in sourced) and not groups):
            raise ValueError('附件风格覆盖缺少索引或来源重复')
        if groups:
            group_map = {g['id']: g for g in data['styleGroups']}
            slugs = [sid for group in groups for sid in group['styleIds']]
            if len(slugs) != len(by_source) or len(set(slugs)) != len(slugs) or set(slugs) != set(by_source):
                raise ValueError('附件风格覆盖不完整或重复')
            if any(by_source[sid]['group'] != group['id'] or group_map.get(group['id'], {}).get('name') != group['name']
                   for group in groups for sid in group['styleIds']):
                raise ValueError('附件风格分组不一致')
            lines += ['', '## 完整参考目录覆盖', '',
                      f"附件 {len(groups)} 组 {len(slugs)} 项，另有本库 {len(styles)-len(slugs)} 项。旧版 {len(ids)} 份固定来源保留，本次新增条目使用本地原创配方。", '',
                      '| 参考组 | 数量 | 本地方法入口 |', '|---|---|---|']
            for group in groups:
                members = [by_source[sid] for sid in group['styleIds']]
                links = '、'.join(f"[{row['name']}]({Path(row['reference']).relative_to('references').as_posix()})" for row in members)
                lines.append(f"| {group['name']} | {len(members)} | {links} |")
        else:
            lines += ['', '## 固定参考目录', '', f"固定来源版本 {library['commit']}，共 {len(ids)} 条。", '']
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
    page=page.replace('<nav>','<p><a href="styles.html">浏览完整风格库：附件风格和本库补充</a></p><nav>')
    options=lambda items: ''.join('<option value="'+html.escape(i['id'])+'">'+html.escape(i['name'])+'</option>' for i in items)
    cards=[]
    for style in data['styles']:
        matches=use_case_matches(data,style['id'])
        details=[]
        for m in matches:
            evidence=''.join('<p><a href="../../'+next(s['project'] for s in data['samples'] if s['id']==sid)+'/DEMO.md">同风格工程样片（非此构想）</a></p>' for sid in m['evidenceSampleIds'])
            details.append('<details><summary>'+html.escape(m['useCaseName'])+(' · 有条件' if m['fit']=='conditional' else '')+'</summary><p>'+html.escape(m['why'])+'</p><p>构想，未渲染：'+html.escape(m['example']['title'])+'。'+html.escape(m['example']['keyShot'])+'</p><p>条件：'+html.escape('；'.join(m['conditions']))+'</p>'+evidence+'</details>')
        cards.append('<article data-group="'+style.get('group','local')+'" data-purposes="'+','.join(style.get('purposes',[]))+'" data-cases="'+','.join(m['useCaseId'] for m in matches)+'" data-search="'+html.escape(search_text(data,style),quote=True)+'"><h2>'+html.escape(style['name'])+'</h2><p>'+html.escape(style.get('material','本库原有组合画法，按片实现。'))+'</p><p>'+html.escape(style.get('action','按内容设计动作。'))+'</p>'+''.join(details)+'<a href="../../'+style['reference']+'">方法与验收</a><small>方法配方 · 按本片验证</small></article>')
    stylepage='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>完整风格库 · 代码视频</title><style>body{max-width:1280px;margin:40px auto;padding:0 22px;background:#f3f0e9;color:#163a3c;font:17px system-ui}input,select{font:inherit;padding:10px;max-width:100%;margin:8px 4px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(290px,100%),1fr));gap:16px}article{padding:20px;background:#fffdf8;border:1px solid #d6ded4;border-radius:12px}article[hidden]{display:none}p{line-height:1.7}a{color:#176e67}small{display:block;margin-top:12px;color:#61726b}h2{font-size:22px}</style><h1>完整风格库</h1><p>附件风格与本库补充共STYLE_COUNT项。按用途、组别或关键词查找；新吸收方法尚未逐条在本库制作成片。</p><label>搜索<input id="query" placeholder="例如 水墨 / 纪录片 / 3D"></label><label>用途<select id="purpose"><option value="">全部用途</option>'''+options(data['categories'])+'</select></label><label>风格组<select id="group"><option value="">全部组别</option>'+options(data.get('styleGroups',[]))+'</select></label><p id="count"></p><main>'+''.join(cards)+'''</main><p><a href="index.html">原创样片</a> · <a href="../../references/classification.md">分类与技术状态</a></p><script>function update(){const q=document.querySelector('#query').value.toLowerCase(),p=document.querySelector('#purpose').value,g=document.querySelector('#group').value;let n=0;document.querySelectorAll('article').forEach(a=>{a.hidden=!!(q&&!a.dataset.search.includes(q)||p&&!a.dataset.purposes.split(',').includes(p)||g&&a.dataset.group!==g);if(!a.hidden)n++});document.querySelector('#count').textContent=n+' 项可浏览方法';}document.querySelectorAll('input,select').forEach(e=>e.addEventListener('input',update));update();</script></html>'''
    stylepage=stylepage.replace('STYLE_COUNT',str(len(styles)))
    result={'references/classification.md':'\n'.join(lines),'assets/gallery/index.html':page,'assets/gallery/styles.html':stylepage}
    if data.get('useCases'):
        result['references/use-case-mapping.md']=mapping_document(data)
        result['references/classification.md']=result['references/classification.md'].replace('## 视觉风格（与用途自由组合）', f"## 按具体主题用法检索\n\n[{len(data['useCases'])}种主题用法与{len(styles)}种风格的正反向映射](use-case-mapping.md)：广告、个人宣传、纪录片、浪漫故事、概念解释等。每条含理由、关键镜头构想和条件；不增加开场分类选择。\n\n## 视觉风格（与用途自由组合）")
        case_select='<label>具体用法<select id="use-case"><option value="">全部用法</option>'+options(data['useCases'])+'</select></label>'
        stylepage=stylepage.replace('<label>搜索',case_select+'<label>搜索')
        stylepage=stylepage.replace('</style>', 'label{display:inline-flex;flex-direction:column;gap:6px;vertical-align:top;margin:12px 12px 12px 0}label input,label select{margin:0;box-sizing:border-box;width:230px}details{margin:10px 0}summary{cursor:pointer}@media(max-width:600px){label{display:flex;margin:16px 0}label input,label select{width:100%}}</style>',1)
        stylepage=stylepage.replace('按用途、组别或关键词查找', '按具体用法、用途、组别或关键词查找；展开卡片可看匹配理由和未渲染构想')
        stylepage=stylepage.replace("g=document.querySelector('#group').value;", "g=document.querySelector('#group').value,u=document.querySelector('#use-case').value;")
        stylepage=stylepage.replace('g&&a.dataset.group!==g)', "g&&a.dataset.group!==g||u&&!a.dataset.cases.split(',').includes(u))")
        stylepage=stylepage.replace('<p id="count">','<p>用法可交叉，同一风格可多用；新构想未渲染，工程样片不等于本题材成片验证。<a href="../../references/use-case-mapping.md">完整映射表</a></p><p id="count">')
        result['assets/gallery/styles.html']=stylepage
    if data.get('referenceCases'):
        result['references/production-cases.md']=reference_case_document(data)
    for style in styles.values():
        if 'continuityAnchor' not in style:
            continue
        matches = use_case_matches(data, style['id'])
        method = [f"# {style['name']}", '', f"目录 ID：`{style['id']}`。状态：制作配方，按镜验证。", '',
                  '## 本镜怎么画', '', style['material'] + '。' + style['action'] + '。', '',
                  '素材与数据：' + style['inputs'] + '。', '可选技术：' + ' / '.join(style['engines']) + '。']
        if style.get('referenceNeeds'):
            method += ['参考制作路线用到图像生成；本片可使用已有授权分层素材，核对角色和道具锚点。']
        method += ['', '## 怎样接镜和验收', '', style['continuityAnchor'] + '。' + style['risk'] + '。',
                   '在动作开始、变化中点和落定处查看主体与关键读数。实现见[连续动作与画法交接](../../style-continuity.md)。',
                   '', '## 用法与原创镜头构想', '']
        for m in matches:
            method.append(f"- {m['useCaseId']}：{m['why']}。{m['example']['title']}——{m['example']['keyShot']}。")
        result[style['reference']] = '\n'.join(method) + '\n'
    library_path = root/'config/frontend-libraries.json'
    if library_path.is_file():
        result['references/frontend-libraries.md'] = frontend_library_document(frontend_libraries(root))
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['build','check','list','show','use-cases','cases','libraries'])
    p.add_argument('style_id',nargs='?',help='show命令的风格ID')
    p.add_argument('--root',type=Path,default=ROOT)
    p.add_argument('--purpose');p.add_argument('--query',default='');p.add_argument('--use-case')
    p.add_argument('--route',help='libraries的技术路线ID；名称与输入要求见references/frontend-libraries.md')
    p.add_argument('--view',choices=['full','summary'],default='full',help='summary仅返回发现所需字段；默认完整JSON保持兼容')
    p.add_argument('--limit',type=int,help='显式分页，不是推荐前N项')
    p.add_argument('--offset',type=int,help='显式分页起点，源目录顺序不是推荐排名')
    a=p.parse_args()
    if a.route and a.command != 'libraries':
        p.error('--route仅用于libraries')
    if a.command == 'libraries':
        if a.style_id or a.purpose or a.use_case:
            p.error('libraries使用--query/--route，不接受风格ID或用途筛选')
        try:
            rows = select_libraries(frontend_libraries(a.root), a.query, a.route)
            if a.view == 'summary':
                rows = [{k:r[k] for k in ('id','name','role','capabilities','verification','routeRole') if k in r} for r in rows]
            rows = discovery_rows(rows, 'libraries', 'full', a.limit, a.offset)
        except (ValueError, OSError) as error:
            p.error(str(error))
        print(json.dumps(rows,ensure_ascii=False,indent=2));return
    if a.command != 'show' and a.style_id:
        p.error('只有show命令接受风格ID')
    if a.command == 'show' and (not a.style_id or a.purpose or a.query or a.limit is not None or a.offset is not None):
        p.error('show须指定风格ID，可选--use-case，不接受列表过滤或分页')
    if a.command in ('build','check') and (a.view != 'full' or a.limit is not None or a.offset is not None):
        p.error('build/check不接受摘要或分页')
    if a.command in ('list','show','use-cases','cases'):
        data=json.loads((a.root/'config/capabilities.json').read_text());
        try:
            validate_use_cases(data)
            validate_reference_cases(data)
            if a.command == 'show':
                row = style_detail(data, a.style_id, a.use_case)
                rows = style_summary(row) if a.view == 'summary' else row
            else:
                rows=select_styles(data,a.purpose,a.query,a.use_case) if a.command=='list' else select_reference_cases(data,a.purpose,a.query,a.use_case) if a.command=='cases' else [{k:c[k] for k in ('id','name','aliases','purposes','goal','structure','needs')} for c in data.get('useCases',[])]
                rows=discovery_rows(rows,a.command,a.view,a.limit,a.offset)
        except ValueError as error: p.error(str(error))
        print(json.dumps(rows,ensure_ascii=False,indent=2));return
    for name,content in documents(a.root).items():
        file=a.root/name
        if a.command=='build': file.parent.mkdir(parents=True,exist_ok=True);file.write_text(content,encoding='utf-8')
        elif not file.exists() or file.read_text()!=content: raise SystemExit(f'目录过期：{name}；运行 catalog.py build')
    print('目录与元数据一致' if a.command=='check' else '已生成分类与画廊')
if __name__=='__main__': main()
