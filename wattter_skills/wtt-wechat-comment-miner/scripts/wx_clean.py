# -*- coding: utf-8 -*-
"""清洗微信留言 OCR 文本：去文章正文干扰行 + 相邻屏重叠去重。

用法：
    python3 wx_clean.py [输入glob] [输出文件] [正文干扰阈值]

默认：
    输入  /tmp/wx_full_*.txt
    输出  /tmp/wx_clean_lines.txt
    阈值  12（某行出现在 >=12 屏即判为每屏重复的文章正文）

阈值说明：设为「总屏数 × 0.3」较稳。若采集屏数远多于/少于 41，
可调整第三个参数，避免把真实留言误判为正文（或反之）。
"""
import re, glob, collections, sys

pattern = sys.argv[1] if len(sys.argv) > 1 else '/tmp/wx_full_*.txt'
outfile = sys.argv[2] if len(sys.argv) > 2 else '/tmp/wx_clean_lines.txt'
threshold = int(sys.argv[3]) if len(sys.argv) > 3 else 12

files = sorted(
    [p for p in glob.glob(pattern) if re.search(r'_(\d+)\.txt', p)],
    key=lambda p: int(re.search(r'_(\d+)\.txt', p).group(1)),
)
if not files:
    sys.exit(f'未找到匹配文件: {pattern}')

screens = []
for f in files:
    n = int(re.search(r'_(\d+)\.txt', f).group(1))
    lines = [l.rstrip('\n') for l in open(f, encoding='utf-8')]
    screens.append((n, lines))

# 全局行频次：文章正文在每屏左侧重复出现，留言在右侧滚动
cnt = collections.Counter()
for n, lines in screens:
    seen = set()
    for l in lines:
        s = l.strip()
        if s:
            seen.add(s)
    for s in seen:
        cnt[s] += 1

noise = {s for s, c in cnt.items() if c >= threshold}
print(f'=== 判为正文干扰的行(出现>={threshold}屏, 共{len(noise)}种) ===')
for s in sorted(noise, key=lambda x: -cnt[x]):
    print(f'[{cnt[s]}] {s}')

clean_screens = []
for n, lines in screens:
    cl = [l.strip() for l in lines if l.strip() and l.strip() not in noise]
    clean_screens.append((n, cl))


def tail_match(prev, cur, maxk=12):
    """若本屏开头 k 行与上屏结尾 k 行相同，返回 k（scroll 造成的重叠）。"""
    best = 0
    for k in range(1, min(maxk, len(prev), len(cur)) + 1):
        if prev[-k:] == cur[:k]:
            best = k
    return best


merged = []
for n, cl in clean_screens:
    if merged:
        k = tail_match(merged[-1][1], cl)
        if k:
            print(f'屏{n}: 去重叠 {k} 行')
            cl = cl[k:]
    merged.append((n, cl))

allclean = []
for n, cl in merged:
    allclean.extend(cl)
print(f'\n=== 清洗后总行数 {len(allclean)} → {outfile} ===')
open(outfile, 'w', encoding='utf-8').write('\n'.join(allclean))
