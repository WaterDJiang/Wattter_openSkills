#!/usr/bin/env python3
"""Versioned material review. No reset, overwrite-lock, or force-accept operation."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import urlsplit
import uuid

SCHEMA = 'code-animation-assets/v1'
FIELDS = ('path', 'sourceUrl', 'license', 'useBasis', 'landingUrl', 'sha256')
RESERVED = {'.asset-review', '.git', 'tools', 'config', '.voice-local', 'node_modules'}
OUTPUTS = {'film.json', 'assets.json', 'timeline.json', 'index.html', 'runtime.js', 'scenes.js',
           'silent.mp4', 'final.mp4', 'render-report.json', 'preview-report.json',
           'media-info.json', 'delivery-check.json', 'finalization.json', 'render-failure.json', 'audio/mix-master.wav', 'audio/mix-report.json'}


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def encoded(data):
    return (json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode()


def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        while block := f.read(1024 * 1024):
            h.update(block)
    return h.hexdigest()


def object_sha(data):
    return hashlib.sha256(encoded(data)).hexdigest()


def write_new(p, data):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('xb') as f:
        f.write(encoded(data))


def replace_json(p, data):
    p = Path(p); temp = p.with_name(p.name + '.' + uuid.uuid4().hex + '.tmp')
    write_new(temp, data); os.replace(temp, p)


def state(root):
    return Path(root).resolve() / '.asset-review'


def local(root, name):
    if not isinstance(name, str) or not name or Path(name).is_absolute() or '\\' in name:
        raise ValueError(f'素材路径须为项目内相对路径：{name}')
    path = Path(root) / name
    if '..' in Path(name).parts or any(part.startswith('.') for part in Path(name).parts):
        raise ValueError(f'素材路径含保留目录：{name}')
    if Path(name).parts[0] in RESERVED or name in OUTPUTS:
        raise ValueError(f'素材路径与代码/管理文件冲突：{name}')
    if not path.resolve().is_relative_to(Path(root).resolve()):
        raise ValueError(f'素材路径越界：{name}')
    for parent in (path, *path.parents):
        if parent == Path(root): break
        if parent.is_symlink(): raise ValueError(f'素材路径不能是软链：{name}')
    return path


def valid_id(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-z][a-z0-9-]*', value):
        raise ValueError(f'素材/链接 ID 须为 kebab-case：{value}')


def url(value, optional=False):
    if optional and value is None: return
    if not isinstance(value, str) or urlsplit(value).scheme not in ('http', 'https') or not urlsplit(value).netloc:
        raise ValueError(f'需要完整 HTTP(S) URL：{value}')


def selection(root, data, candidate_sources=False):
    if data.get('schema') != SCHEMA or not isinstance(data.get('assets'), list) or not isinstance(data.get('links'), list):
        raise ValueError('assets.json 须使用 code-animation-assets/v1，并包含 assets/links 数组')
    assets, links, sources, paths = {}, {}, {}, set()
    for item in data['assets']:
        aid = item.get('id'); valid_id(aid)
        if aid in assets: raise ValueError(f'素材 ID 重复：{aid}')
        path = local(root, item.get('path'))
        if item['path'] in paths: raise ValueError('多个素材不能占用同一路径')
        paths.add(item['path'])
        source = path
        if item.get('candidatePath'):
            if not candidate_sources: raise ValueError('当前声明不能包含 candidatePath；变更须先 propose')
            source = (Path(root) / item['candidatePath']).resolve()
            if not source.is_relative_to(state(root) / 'candidates'):
                raise ValueError('新下载/替换文件必须先放在 .asset-review/candidates 内')
        assets[aid] = {'id': aid, **{k: item.get(k) for k in FIELDS if k != 'sha256'},
                       'sha256': sha(source) if source.is_file() else None}
        sources[aid] = source
    for item in data['links']:
        lid = item.get('id'); valid_id(lid)
        if lid in links: raise ValueError(f'导流 ID 重复：{lid}')
        links[lid] = {'id': lid, 'url': item.get('url'), 'purpose': item.get('purpose')}
    return {'schema': SCHEMA, 'assets': sorted(assets.values(), key=lambda x: x['id']),
            'links': sorted(links.values(), key=lambda x: x['id'])}, sources


def validate_selection(data):
    for item in data['assets']:
        if not item['sha256']: raise ValueError(f'素材缺失：{item["id"]} / {item["path"]}')
        for k in ('license', 'useBasis'):
            if not isinstance(item[k], str) or not item[k].strip(): raise ValueError(f'{item["id"]}.{k} 必填')
        url(item['sourceUrl'], True); url(item['landingUrl'], True)
    for item in data['links']:
        url(item['url'])
        if not isinstance(item['purpose'], str) or not item['purpose'].strip(): raise ValueError('导流用途必填')


def declaration(data):
    return {'schema': SCHEMA, 'assets': [{k: v for k, v in a.items() if k != 'sha256'} for a in data['assets']],
            'links': data['links']}


def changes(old, new, reason, impact):
    rows = []
    for kind, fields in (('assets', FIELDS), ('links', ('url', 'purpose'))):
        before = {a['id']: a for a in old[kind]}; after = {a['id']: a for a in new[kind]}
        for aid in sorted(before.keys() | after.keys()):
            a, b = before.get(aid), after.get(aid)
            if a is None or b is None:
                rows.append({'key': f'{kind}.{aid}', 'old': a, 'new': b, 'reason': reason, 'impact': impact})
            else:
                for key in fields:
                    if a.get(key) != b.get(key):
                        rows.append({'key': f'{kind}.{aid}.{key}', 'old': a.get(key), 'new': b.get(key),
                                     'reason': reason, 'impact': impact})
    return rows


def markdown(diff):
    def cell(v):
        return json.dumps(v, ensure_ascii=False).replace('|', '\\|').replace('\n', ' ')
    lines = ['# 素材变更审阅', '', f'基准版本：{diff["base"]["version"]}', '',
             '| 变更项 | 旧值 | 新值 | 原因 | 影响 |', '|---|---|---|---|---|']
    for r in diff['changes']:
        lines.append('| ' + ' | '.join(cell(r[k]) for k in ('key', 'old', 'new', 'reason', 'impact')) + ' |')
    return '\n'.join(lines) + '\n'


def has_history(root):
    film = Path(root)/'film.json'
    return state(root).exists() or film.is_file() and bool(read(film).get('assetReview'))


def history(root):
    root = Path(root).resolve(); folder = state(root)
    if (folder/'transaction.json').exists(): raise ValueError('素材提交曾中断；保留 transaction 与旧版，先恢复该事务，禁止重建锁')
    if not (folder/'current.json').is_file(): raise ValueError('素材锁缺失；不得重建或以哈希报告替代；首次制作使用 seal')
    head = read(folder/'current.json')
    if read(root/'film.json').get('assetReview') != head:
        raise ValueError('film 素材锚点与历史不一致；禁止重建/覆盖清单绕过审阅')
    folders = sorted((folder/'versions').glob('v[0-9]*'))
    if not folders: raise ValueError('素材历史丢失')
    previous = None
    for i, version in enumerate(folders, 1):
        if version.name != f'v{i:04d}': raise ValueError('素材历史版本不连续，禁止删除/跳过历史')
        manifest = read(version/'manifest.json'); receipt = {'version': version.name, 'manifestSha256': sha(version/'manifest.json')}
        commit = read(version/'commit.json')
        if commit['receipt'] != receipt or manifest['parent'] != previous:
            raise ValueError('素材历史清单哈希/父版本不符，禁止覆写基准')
        for entry in manifest['selection']['assets']:
            if sha(version/'files'/entry['id']) != entry['sha256']: raise ValueError('锁定的历史素材被改写')
        for key in ('diff', 'authorization'):
            if sha(version/f'{key}.json') != commit[f'{key}Sha256']: raise ValueError('历史审阅/授权被改写')
        previous = receipt
    if head != previous: raise ValueError('当前锁不是最新历史版本，禁止回退锚点绕过审阅')
    return head, manifest['selection']


@contextmanager
def exclusive(root):
    folder = state(root); folder.mkdir(parents=True, exist_ok=True)
    with (folder/'.mutex').open('a') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        yield


def candidate(root, head, old, new, sources, reason, impact):
    diff = {'base': head, 'changes': changes(old, new, reason, impact)}
    cid = 'review-' + uuid.uuid4().hex
    folder = state(root)/'candidates'/cid; folder.mkdir(parents=True)
    for a in new['assets']:
        if a['sha256']:
            dest = folder/'files'/a['id']; dest.parent.mkdir(exist_ok=True)
            shutil.copyfile(sources[a['id']], dest)
            if sha(dest) != a['sha256']: raise ValueError('候选复制期间源文件变化；重做候选，不能确认旧 diff')
    review = {'id': cid, 'base': head, 'selection': new, 'diff': diff}
    write_new(folder/'review.json', review)
    (folder/'diff.md').write_text(markdown(diff), encoding='utf-8')
    print(markdown(diff), file=sys.stderr)
    print(f'候选：{cid}；reviewSha256={object_sha(review)}', file=sys.stderr)
    return {'candidate': cid, 'reviewSha256': object_sha(review), 'changes': diff['changes']}


def observed_links(root):
    from html import unescape
    pattern = re.compile(r"(?:href\s*=|action\s*=|window\.open\s*\(|(?:window\.)?location(?:\.href)?\s*=)\s*['\"](https?://[^'\"]+)")
    files = [p for p in Path(root).iterdir() if p.suffix in ('.js', '.html') and p.is_file()]
    if (Path(root)/'code').exists():
        files += [p for p in (Path(root)/'code').rglob('*') if p.suffix in ('.js', '.html') and p.is_file()]
    return {unescape(u) for p in files for u in pattern.findall(p.read_text(encoding='utf-8'))}


def unregistered_links(root, selected):
    declared = {a['landingUrl'] for a in selected['assets']} | {x['url'] for x in selected['links']}
    return observed_links(root) - declared


def require(root):
    root = Path(root).resolve()
    head, old = history(root)
    new, sources = selection(root, read(root/'assets.json'))
    for target in sorted(unregistered_links(root, new)):
        new['links'].append({'id': 'observed-' + hashlib.sha256(target.encode()).hexdigest()[:12],
                             'url': target, 'purpose': '代码中出现未登记导流；须补充实际用途并审阅'})
    new['links'].sort(key=lambda a: a['id'])
    if new != old:
        review = candidate(root, head, old, new, sources, '工作区与锁定版本不一致；实际原因待说明',
                           '阻断执行与验收；确认后重新锁时、混音、渲染及验收')
        raise ValueError(f'素材变更未确认，已输出 diff：{review["candidate"]}；不得更新清单或通过验收')
    validate_selection(new)
    return head


def observe(root, target):
    """Runtime-only navigation detection retains a readable candidate before blocking."""
    url(target)
    root = Path(root).resolve(); head, old = history(root)
    new, sources = selection(root, read(root/'assets.json'))
    if target in {x['url'] for x in new['links']} | {x['landingUrl'] for x in new['assets']}:
        return require(root)
    new['links'].append({'id': 'observed-' + hashlib.sha256(target.encode()).hexdigest()[:12],
                         'url': target, 'purpose': '浏览器发现未登记导流；须说明用途并审阅'})
    new['links'].sort(key=lambda x: x['id'])
    review = candidate(root, head, old, new, sources, '浏览器发现清单外导流', '阻断预览、渲染和验收；登记实际目标后审阅')
    raise ValueError(f'导流变更未确认：{review["candidate"]}')


def guard_if_locked(root):
    if has_history(root): return require(root)
    return None


def registered(root, paths):
    require(root)
    _, locked = history(root)
    names = {a['path'] for a in locked['assets']}
    inputs = set(paths)
    for name in paths:
        if Path(name).suffix.lower() in ('.wav', '.mp3', '.m4a', '.flac', '.aiff') and (Path(root)/(name + '.json')).is_file():
            inputs.add(name + '.json')
    missing = inputs - names
    if missing: raise ValueError(f'未登记素材：{sorted(missing)}；先放候选目录并完成审阅')


def protect_output(root, path):
    if not has_history(root): return
    require(root)
    if Path(path).resolve().is_relative_to(state(root)/'candidates'): return
    raise ValueError('禁止写入当前素材目录；新声音/素材须在候选目录生成并审阅')


def seal(root, migration=None):
    root = Path(root).resolve()
    film = read(root/'film.json')
    folder = state(root)
    if folder.exists() or film.get('assetReview'):
        raise ValueError('素材历史已存在或不完整，禁止重建/重新 seal；使用 propose/accept')
    if any((root/name).exists() for name in ('timeline.json', 'render-report.json', 'delivery-check.json', 'final.mp4')) and not migration:
        raise ValueError('已有项目产物，首次纳管须 --migration-note 记录基准核对依据；不自动重跑旧作品')
    selected, sources = selection(root, read(root/'assets.json')); validate_selection(selected)
    if unregistered_links(root, selected): raise ValueError('网页导流尚未完整登记到 assets.json')
    with exclusive(root):
        if (folder/'current.json').exists() or (folder/'versions').exists(): raise ValueError('已有历史不能重新初始化')
        return commit(root, None, selected, sources, {'base': None, 'changes': [], 'initial': True},
                      {'kind': 'initial-selection', 'basis': migration or '首次制作自主检索选材，来源与使用依据见清单'})


def propose(root, proposal, reason, impact):
    root = Path(root).resolve()
    head, old = history(root)
    new, sources = selection(root, read(proposal), candidate_sources=True)
    validate_selection(new)
    if old == new: return {'unchanged': True, 'receipt': head}
    if not reason.strip() or not impact.strip(): raise ValueError('变更原因和影响必填')
    return candidate(root, head, old, new, sources, reason, impact)


def commit(root, parent, selected, sources, diff, authorization):
    folder = state(root)
    version = f'v{int(parent["version"][1:])+1:04d}' if parent else 'v0001'
    dest = folder/'versions'/version
    if dest.exists(): raise ValueError('版本已存在，不能覆盖')
    write_new(folder/'transaction.json', {'version': version, 'parent': parent, 'status': 'applying-authorized-change'})
    dest.mkdir(parents=True)
    for a in selected['assets']:
        out = dest/'files'/a['id']; out.parent.mkdir(exist_ok=True)
        shutil.copyfile(sources[a['id']], out)
        if sha(out) != a['sha256']: raise ValueError('提交期间素材发生变化，事务阻断；不得验收')
    manifest = {'schema': 'code-animation-asset-lock/v1', 'version': version, 'parent': parent,
                'createdAt': datetime.now(timezone.utc).isoformat(), 'selection': selected}
    write_new(dest/'manifest.json', manifest); write_new(dest/'diff.json', diff)
    write_new(dest/'authorization.json', authorization)
    (dest/'diff.md').write_text(markdown(diff) if parent else '# 首次素材锁定\n', encoding='utf-8')
    receipt = {'version': version, 'manifestSha256': sha(dest/'manifest.json')}
    write_new(dest/'commit.json', {'receipt': receipt, 'diffSha256': sha(dest/'diff.json'),
                                 'authorizationSha256': sha(dest/'authorization.json')})
    if parent:
        before = read(folder/'versions'/parent['version']/'manifest.json')['selection']
        current_paths = {a['path'] for a in selected['assets']}
        for a in selected['assets']:
            target = local(root, a['path']); target.parent.mkdir(parents=True, exist_ok=True)
            temp = target.with_name(target.name + '.' + uuid.uuid4().hex + '.tmp')
            shutil.copyfile(dest/'files'/a['id'], temp); os.replace(temp, target)
        for a in before['assets']:
            target = local(root, a['path'])
            if a['path'] not in current_paths and target.exists(): target.unlink()
    replace_json(root/'assets.json', declaration(selected))
    film = read(root/'film.json'); film['assetReview'] = receipt
    replace_json(root/'film.json', film); replace_json(folder/'current.json', receipt)
    (folder/'transaction.json').unlink()
    return receipt


def accept(root, cid, authorization_file):
    root = Path(root).resolve()
    if not re.fullmatch(r'review-[0-9a-f]{32}', cid): raise ValueError('无效候选 ID')
    with exclusive(root):
        head, old = history(root)
        folder = state(root)/'candidates'/cid; review = read(folder/'review.json')
        print(markdown(review['diff']), file=sys.stderr)
        authorization = read(authorization_file)
        if review['base'] != head: raise ValueError('候选基准已过期；重新生成 diff，旧授权不能用于新版')
        if authorization.get('kind') not in ('confirmed', 'explicit-request') or not authorization.get('statement', '').strip():
            raise ValueError('需要实际用户确认或明确本次替换对象与目标的原始指令')
        if authorization.get('reviewSha256') != object_sha(review): raise ValueError('授权未绑定当前 diff，拒绝提交')
        if sorted(authorization.get('changes', [])) != sorted(r['key'] for r in review['diff']['changes']):
            raise ValueError('授权范围与 diff 变更项不一致')
        selected = review['selection']; validate_selection(selected)
        # Validate paths again; candidate and authorization are data, never executable instructions.
        normalized, _ = selection(root, declaration(selected))
        if [a['path'] for a in normalized['assets']] != [a['path'] for a in selected['assets']]:
            raise ValueError('候选路径不规范')
        if not review['diff']['changes']: raise ValueError('无变更候选不能提交新版')
        if review['diff']['changes'] != changes(old, selected, review['diff']['changes'][0]['reason'], review['diff']['changes'][0]['impact']):
            raise ValueError('候选 diff 与内容不一致')
        sources = {a['id']: folder/'files'/a['id'] for a in selected['assets']}
        for a in selected['assets']:
            if sha(sources[a['id']]) != a['sha256']: raise ValueError('候选文件在 diff 后被修改；需要新审阅')
        # Do not silently discard unrelated mutations that happened after review creation.
        working, _ = selection(root, read(root/'assets.json'))
        reviewed_keys = {r['key'] for r in review['diff']['changes']}
        for row in changes(old, working, '', ''):
            match = next((r for r in review['diff']['changes'] if r['key'] == row['key']), None)
            removed = any(row['key'] == r['key'] + '.sha256' and row['new'] is None and r['new'] is None for r in review['diff']['changes'])
            if not removed and (row['key'] not in reviewed_keys or (match and row['new'] != match['new'])):
                raise ValueError('工作区出现未纳入本次 diff 的变化；重新审阅，不能覆盖')
        old_paths = {a['path'] for a in old['assets']}
        for entry in selected['assets']:
            if entry['path'] not in old_paths and local(root, entry['path']).exists():
                raise ValueError('新素材目标已存在未纳管文件；不能无旧值记录覆盖它')
        if unregistered_links(root, selected): raise ValueError('网页仍存在本次候选以外的导流 URL；补充 diff 后再确认')
        return commit(root, head, selected, sources, review['diff'], authorization)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['seal', 'check', 'propose', 'accept', 'view', 'observe'])
    p.add_argument('project', type=Path)
    p.add_argument('--migration-note'); p.add_argument('--proposal', type=Path)
    p.add_argument('--reason'); p.add_argument('--impact'); p.add_argument('--candidate')
    p.add_argument('--authorization', type=Path); p.add_argument('--url')
    a = p.parse_args(); root = a.project.resolve()
    if a.command == 'seal': result = seal(root, a.migration_note)
    elif a.command == 'check': result = require(root)
    elif a.command == 'observe': result = observe(root, a.url)
    elif a.command == 'view':
        receipt, selection_data = history(root); result = {'receipt': receipt, 'selection': selection_data}
    elif a.command == 'propose':
        if not all((a.proposal, a.reason, a.impact)): p.error('propose 需要 --proposal --reason --impact')
        result = propose(root, a.proposal, a.reason, a.impact)
    else:
        if not a.candidate or not a.authorization: p.error('accept 需要 --candidate --authorization')
        result = accept(root, a.candidate, a.authorization)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try: main()
    except (ValueError, OSError, KeyError, TypeError) as e:
        print(f'ERROR: {e}', file=sys.stderr); sys.exit(1)
