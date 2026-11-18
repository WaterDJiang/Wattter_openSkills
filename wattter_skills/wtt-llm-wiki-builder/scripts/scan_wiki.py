#!/usr/bin/env python3
"""
scan_wiki.py — Wiki 健康度扫描器

用法：
    python3 scan_wiki.py {target_dir} --light            # 轻量 8 项
    python3 scan_wiki.py {target_dir} --deep             # 深度 18 项
    python3 scan_wiki.py {target_dir} --check L8         # 单项

输出：JSON 到 stdout，LLM 读取后翻译成自然语言报告。
对应 references/lint-spec.md 中定义的检查项。
L17/L18 为知识时效检查（references/knowledge-freshness.md）：
存量库首次出现大面积 L17 时，先跑 backfill_knowledge_date.py 回填。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# ---------- 数据结构 ----------

def make_finding(severity: str, category: str, path: str, evidence: str, fix_hint: str) -> dict:
    return {
        "severity": severity,           # error / warning / info
        "category": category,           # L1..L16
        "path": path,
        "evidence": evidence,
        "fix_hint": fix_hint,
    }


# ---------- frontmatter 解析 ----------

FM_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

def parse_frontmatter(text: str) -> dict | None:
    """极简 YAML frontmatter parser，只支持 key: value 与 list。无 PyYAML 依赖。"""
    m = FM_PATTERN.match(text)
    if not m:
        return None
    fm: dict = {}
    for line in m.group(1).splitlines():
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        # 去引号
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        # list 形式 [a, b, c]
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            if not inner:
                fm[key] = []
            else:
                fm[key] = [v.strip().strip('"').strip("'") for v in inner.split(",")]
        else:
            fm[key] = value
    return fm


def extract_links(text: str) -> list[str]:
    """提取所有 markdown 链接的 target（不含 anchor）。"""
    return re.findall(r"\[[^\]]*\]\(([^)#]+)(?:#[^)]*)?\)", text)


# ---------- 扫描收集 ----------

def collect_kp_files(wiki_dir: Path) -> list[Path]:
    """收集所有知识点文件（排除 _module-summary.md, index.md）。"""
    if not wiki_dir.exists():
        return []
    files: list[Path] = []
    for p in wiki_dir.rglob("*.md"):
        if p.name == "index.md" or p.name.startswith("_") or "indexes" in p.parts:
            continue
        files.append(p)
    return files


# ---------- 七项轻量检查 ----------

REQUIRED_FIELDS_KP = {"kp_name", "module", "knowledge_domain", "knowledge_type", "tags", "source_marking"}
ALLOWED_SOURCE_MARKING = {"已提取", "AI补全"}
ALLOWED_KNOWLEDGE_TYPES = {"框架", "模型", "原则", "方法", "流程", "工具", "概念"}
ALLOWED_DATE_BASIS = {"exact", "approximate"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# L18 同体系候选扫描时剔除的通用词——共享子串命中这些词不算同体系证据
FRESHNESS_STOP_TOKENS = {
    "模型", "方法", "原则", "理论", "策略", "框架", "法则", "定律", "范式",
    "课程", "培训", "讲师", "知识", "体系", "思维", "管理", "分析", "工具", "流程",
}


def check_L1_frontmatter_required(target: Path, kp_files: list[Path]) -> list[dict]:
    """L1: frontmatter 必需字段缺失（kp 六字段；knowledge_date 归 L17 按卡片类型检查）"""
    findings = []
    for f in kp_files:
        text = f.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if is_note_card(f, fm):
            continue  # note 卡字段集不同，由 L17 查 date
        if fm is None:
            findings.append(make_finding(
                "error", "L1", str(f.relative_to(target)),
                "无 frontmatter",
                "在文件头部添加 YAML frontmatter，包含 kp_name/module/knowledge_domain/knowledge_type/tags/source_marking"
            ))
            continue
        missing = REQUIRED_FIELDS_KP - set(fm.keys())
        if missing:
            findings.append(make_finding(
                "error", "L1", str(f.relative_to(target)),
                f"缺字段: {sorted(missing)}",
                f"在 frontmatter 添加: {', '.join(sorted(missing))}"
            ))
    return findings


def check_L2_source_marking(target: Path, kp_files: list[Path]) -> list[dict]:
    """L2: source_marking 取值非法"""
    findings = []
    for f in kp_files:
        fm = parse_frontmatter(f.read_text(encoding="utf-8"))
        if fm is None:
            continue
        sm = fm.get("source_marking")
        if sm and sm not in ALLOWED_SOURCE_MARKING:
            findings.append(make_finding(
                "error", "L2", str(f.relative_to(target)),
                f"source_marking={sm}",
                f"改为 已提取 或 AI补全"
            ))
    return findings


def check_L3_index_drift(target: Path, wiki_dir: Path, kp_files: list[Path]) -> list[dict]:
    """L3: index.md 漂移"""
    findings = []
    index_path = wiki_dir / "indexes" / "index.md"
    if not index_path.exists():
        findings.append(make_finding(
            "error", "L3", str(index_path.relative_to(target)),
            "wiki/indexes/index.md 不存在",
            "用 assets/index-template.md 初始化"
        ))
        return findings

    index_text = index_path.read_text(encoding="utf-8")
    listed_links = extract_links(index_text)
    # 把链接归一化为相对 wiki_dir 的 POSIX 路径
    listed_paths = set()
    for link in listed_links:
        if link.startswith("./") or link.startswith("../") or not link.startswith(("http", "/")):
            try:
                resolved = (index_path.parent / link).resolve()
                if resolved.suffix == ".md":
                    listed_paths.add(resolved)
            except (OSError, RuntimeError):
                continue

    actual_paths = {f.resolve() for f in kp_files}

    # 死链：index 列了但文件不存在
    for p in listed_paths - actual_paths:
        try:
            rel = p.relative_to(target.resolve())
        except ValueError:
            rel = p
        findings.append(make_finding(
            "error", "L3", "wiki/indexes/index.md",
            f"死链: {rel}",
            "从 index.md 删除该链接，或恢复对应文件"
        ))

    # 漏录：文件存在但 index 没列
    for p in actual_paths - listed_paths:
        try:
            rel = p.relative_to(target.resolve())
        except ValueError:
            rel = p
        findings.append(make_finding(
            "error", "L3", "wiki/indexes/index.md",
            f"漏录: {rel}",
            "在 index.md 对应段（领域索引/类型索引/课程清单）补上链接"
        ))
    return findings


def check_L4_log_format(target: Path, wiki_dir: Path) -> list[dict]:
    """L4: log.md 缺失或格式异常"""
    log_path = wiki_dir / "indexes" / "log.md"
    if not log_path.exists():
        return [make_finding(
            "warning", "L4", str(log_path.relative_to(target)),
            "wiki/indexes/log.md 不存在",
            "用 assets/log-template.md 初始化"
        )]
    text = log_path.read_text(encoding="utf-8")
    if not re.search(r"##\s*\[\d{4}-\d{2}-\d{2}", text):
        return [make_finding(
            "warning", "L4", "wiki/indexes/log.md",
            "未发现 ## [YYYY-MM-DD ...] 格式条目",
            "确认 log.md 至少有一条符合 references/log-spec.md 的条目"
        )]
    return []


def check_L5_module_summary(target: Path, wiki_dir: Path) -> list[dict]:
    """L5: 模块文件夹缺 _module-summary.md"""
    findings = []
    kps_dir = wiki_dir / "kps"
    if not kps_dir.exists():
        return findings
    for course_dir in kps_dir.iterdir():
        if not course_dir.is_dir():
            continue
        for module_dir in course_dir.iterdir():
            if not module_dir.is_dir():
                continue
            if not re.match(r"\d{2}-", module_dir.name):
                continue
            if not (module_dir / "_module-summary.md").exists():
                findings.append(make_finding(
                    "warning", "L5", str(module_dir.relative_to(target)),
                    "缺 _module-summary.md",
                    "用 assets/module-summary-template.md 创建"
                ))
    return findings


def check_L6_naming(target: Path, kp_files: list[Path]) -> list[dict]:
    """L6: 知识点文件命名违规"""
    findings = []
    for f in kp_files:
        name = f.name
        # 序号前缀
        if re.match(r"^\d{2}-", name):
            findings.append(make_finding(
                "warning", "L6", str(f.relative_to(target)),
                f"含序号前缀: {name}",
                "去除序号前缀（跨课程引用稳定性）"
            ))
        # 空格
        if " " in name:
            findings.append(make_finding(
                "warning", "L6", str(f.relative_to(target)),
                f"文件名含空格: {name}",
                "用 - 替换空格"
            ))
        # 扩展名大写
        if not name.endswith(".md"):
            findings.append(make_finding(
                "warning", "L6", str(f.relative_to(target)),
                f"扩展名非 .md: {name}",
                "改为小写 .md"
            ))
    return findings


def check_L7_dead_links(target: Path, kp_files: list[Path]) -> list[dict]:
    """L7: 跨知识点链接失效"""
    findings = []
    for f in kp_files:
        text = f.read_text(encoding="utf-8")
        for link in extract_links(text):
            if link.startswith(("http://", "https://", "mailto:")):
                continue
            target_path = (f.parent / link).resolve()
            if not target_path.exists():
                findings.append(make_finding(
                    "error", "L7", str(f.relative_to(target)),
                    f"失效链接 → {link}",
                    "修正路径、改为纯文本，或删除链接"
                ))
    return findings


# ---------- 深度九项 ----------

def check_L8_orphan(target: Path, wiki_dir: Path, kp_files: list[Path]) -> list[dict]:
    """L8: 孤儿卡片"""
    findings = []
    inbound = defaultdict(int)
    # 扫所有 markdown（含 index、_module-summary）找入边
    for md in wiki_dir.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        for link in extract_links(text):
            if link.startswith(("http", "mailto:")):
                continue
            try:
                resolved = (md.parent / link).resolve()
                inbound[resolved] += 1
            except (OSError, RuntimeError):
                continue
    for f in kp_files:
        if inbound.get(f.resolve(), 0) == 0:
            findings.append(make_finding(
                "warning", "L8", str(f.relative_to(target)),
                "无任何入边链接",
                "加入对应 _module-summary 或 index；或移到 wiki/.drafts/；或删除"
            ))
    return findings


def check_L9_stale_marking(target: Path, wiki_dir: Path, kp_files: list[Path]) -> list[dict]:
    """L9: 陈旧 source_marking（AI补全 但 raw/ 中已有同名内容）"""
    findings = []
    raw_dir = target / "raw"
    if not raw_dir.exists():
        return findings
    raw_stems = {p.stem for p in raw_dir.rglob("*") if p.is_file()}
    concepts_dir = wiki_dir / "concepts"
    concept_stems = set()
    if concepts_dir.exists():
        concept_stems = {p.stem for p in concepts_dir.glob("*.md")}

    for f in kp_files:
        fm = parse_frontmatter(f.read_text(encoding="utf-8"))
        if fm is None or fm.get("source_marking") != "AI补全":
            continue
        kp_name = fm.get("kp_name", f.stem)
        if any(kp_name in s for s in raw_stems) or kp_name in concept_stems:
            findings.append(make_finding(
                "info", "L9", str(f.relative_to(target)),
                f"标 AI补全 但 raw/ 或 concepts/ 已有 {kp_name}",
                "升级为 已提取，加 upgraded_at 字段"
            ))
    return findings


CONFLICT_PATTERN = re.compile(r"^>\s*⚠️\s*与上次产出冲突", re.MULTILINE)

def check_L10_unresolved_conflict(target: Path, kp_files: list[Path]) -> list[dict]:
    """L10: 冲突块未决（>30 天）"""
    findings = []
    today = datetime.now(timezone.utc).date()
    for f in kp_files:
        text = f.read_text(encoding="utf-8")
        if not CONFLICT_PATTERN.search(text):
            continue
        fm = parse_frontmatter(text)
        last = fm.get("last_compiled") if fm else None
        if last:
            try:
                last_date = datetime.strptime(last, "%Y-%m-%d").date()
                age = (today - last_date).days
                sev = "error" if age > 30 else "warning"
            except ValueError:
                sev = "warning"
        else:
            sev = "warning"
        findings.append(make_finding(
            sev, "L10", str(f.relative_to(target)),
            "存在 ⚠️ 冲突块",
            "二选一保留 / 改写为更通用表述 / 拆为两张卡"
        ))
    return findings


def check_L11_cross_course_synonym(target: Path, wiki_dir: Path, kp_files: list[Path]) -> list[dict]:
    """L11: 跨课程同义未归并"""
    findings = []
    name_to_files = defaultdict(list)

    def normalize(s: str) -> str:
        s = re.sub(r"[原则|方法|法则|论|说]+$", "", s)
        s = re.sub(r"[\s\-_·]+", "", s)
        return s.lower()

    for f in kp_files:
        fm = parse_frontmatter(f.read_text(encoding="utf-8"))
        kp_name = (fm.get("kp_name") if fm else None) or f.stem
        name_to_files[normalize(kp_name)].append(f)

    concepts_dir = wiki_dir / "concepts"
    existing_concepts = set()
    if concepts_dir.exists():
        existing_concepts = {normalize(p.stem) for p in concepts_dir.glob("*.md")}

    for norm, files in name_to_files.items():
        if len(files) >= 2 and norm not in existing_concepts:
            findings.append(make_finding(
                "warning", "L11",
                ", ".join(str(f.relative_to(target)) for f in files),
                f"{len(files)} 张同义卡未归并: {[f.stem for f in files]}",
                f"抽到 wiki/concepts/{files[0].stem}.md，各 kp 改为引用"
            ))
    return findings


def check_L12_field_value(target: Path, kp_files: list[Path]) -> list[dict]:
    """L12: frontmatter 字段值越界"""
    findings = []
    domain_count: dict[str, int] = defaultdict(int)
    domain_files: dict[str, list[str]] = defaultdict(list)

    for f in kp_files:
        fm = parse_frontmatter(f.read_text(encoding="utf-8"))
        if fm is None:
            continue
        kt = fm.get("knowledge_type")
        if kt and kt not in ALLOWED_KNOWLEDGE_TYPES:
            findings.append(make_finding(
                "warning", "L12", str(f.relative_to(target)),
                f"knowledge_type={kt} 不在七选一",
                f"改为: {sorted(ALLOWED_KNOWLEDGE_TYPES)} 之一"
            ))
        kd = fm.get("knowledge_domain")
        if kd:
            domain_count[kd] += 1
            domain_files[kd].append(str(f.relative_to(target)))

    # 频次=1 的 domain 标 info
    for d, c in domain_count.items():
        if c == 1:
            findings.append(make_finding(
                "info", "L12", domain_files[d][0],
                f"knowledge_domain={d} 仅出现 1 次",
                "可能是错别字；与目录其他 domain 对照"
            ))
    return findings


THREE_LINE_PLACEHOLDERS = ["[待补]", "{...}", "TODO", "todo"]
THREE_LINE_TEMPLATES = ["逻辑递进", "情感升华", "本模块逻辑"]

def check_L13_three_lines(target: Path, wiki_dir: Path) -> list[dict]:
    """L13: 三线缺失或空泛"""
    findings = []
    kps_dir = wiki_dir / "kps"
    if not kps_dir.exists():
        return findings
    for ms in kps_dir.rglob("_module-summary.md"):
        text = ms.read_text(encoding="utf-8")
        if "三线" not in text:
            findings.append(make_finding(
                "warning", "L13", str(ms.relative_to(target)),
                "缺三线段",
                "添加情绪线/逻辑线/哲理线三段"
            ))
            continue
        if any(ph in text for ph in THREE_LINE_PLACEHOLDERS):
            findings.append(make_finding(
                "warning", "L13", str(ms.relative_to(target)),
                "三线含占位符 [待补]/TODO",
                "补全实际内容"
            ))
        if any(t in text for t in THREE_LINE_TEMPLATES):
            findings.append(make_finding(
                "info", "L13", str(ms.relative_to(target)),
                "三线表述疑似套话",
                "重写为有具体信息量的内容"
            ))
    return findings


def check_L14_one_way_relation(target: Path, kp_files: list[Path]) -> list[dict]:
    """L14: 关联单边"""
    findings = []
    # 简化版：grep "前置依赖" 块，提取关联的目标 kp，检查目标 kp 中是否反向写回
    forward = defaultdict(set)
    file_by_stem = {f.stem: f for f in kp_files}
    for f in kp_files:
        text = f.read_text(encoding="utf-8")
        # 找形如 "前置依赖" 段中链接
        m = re.search(r"前置依赖[^\n]*\n([\s\S]*?)(?=\n##|\n---|\Z)", text)
        if m:
            for link in extract_links(m.group(1)):
                target_stem = Path(link).stem
                forward[f.stem].add(target_stem)
    for src, targets in forward.items():
        for t in targets:
            tf = file_by_stem.get(t)
            if tf is None:
                continue
            target_text = tf.read_text(encoding="utf-8")
            # 反向：t 文件中应含 src 的反向关联（被 src 依赖 / 关联 src）
            if src not in target_text:
                findings.append(make_finding(
                    "warning", "L14", str(tf.relative_to(target)),
                    f"{src} 标了前置依赖 {t}，但 {t} 没反向写回",
                    f"在 {t}.md 关联段添加: 被 {src} 依赖"
                ))
    return findings


def check_L15_uncompiled_raw(target: Path, wiki_dir: Path) -> list[dict]:
    """L15: raw 未编译"""
    findings = []
    raw_dir = target / "raw"
    log_path = wiki_dir / "indexes" / "log.md"
    if not raw_dir.exists() or not log_path.exists():
        return findings
    log_text = log_path.read_text(encoding="utf-8")
    for raw_file in raw_dir.rglob("*"):
        if not raw_file.is_file() or raw_file.name.startswith("."):
            continue
        rel = raw_file.relative_to(target)
        rel_str = str(rel)
        if rel_str not in log_text and raw_file.name not in log_text:
            findings.append(make_finding(
                "info", "L15", rel_str,
                "log.md 中未引用过此 raw 文件",
                "跑 Compile / 标为参考资料 / 删除"
            ))
    return findings


def check_L16_mapping(target: Path, wiki_dir: Path, kp_files: list[Path]) -> list[dict]:
    """L16: mapping.json 与现实不一致（仅当文件存在时）"""
    findings = []
    mapping_path = wiki_dir / "indexes" / "mapping.json"
    if not mapping_path.exists():
        return findings
    try:
        mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [make_finding(
            "warning", "L16", "wiki/indexes/mapping.json",
            f"JSON 解析失败: {e}",
            "修复 JSON 格式"
        )]
    raw_dir = target / "raw"
    for raw_path, wiki_paths in mapping.items():
        if not (target / raw_path).exists():
            findings.append(make_finding(
                "warning", "L16", "wiki/indexes/mapping.json",
                f"mapping 中的 raw 不存在: {raw_path}",
                "更新 mapping.json"
            ))
        for wp in wiki_paths if isinstance(wiki_paths, list) else [wiki_paths]:
            if not (target / wp).exists():
                findings.append(make_finding(
                    "warning", "L16", "wiki/indexes/mapping.json",
                    f"mapping 中的 wiki 不存在: {wp}",
                    "更新 mapping.json"
                ))
    return findings


# ---------- 知识时效检查（references/knowledge-freshness.md） ----------

def is_note_card(f: Path, fm: dict | None) -> bool:
    """note 卡片的知识时间字段是 date，不是 knowledge_date。"""
    if fm and (fm.get("note_type") or fm.get("type") == "note"):
        return True
    return "notes" in f.parts


def check_valid_date(value: str, findings: list[dict], cid: str, rel: str, field: str) -> None:
    """日期字段格式与合法性校验（供 L17 复用）。"""
    if not DATE_RE.match(value):
        findings.append(make_finding(
            "error", cid, rel,
            f"{field}={value} 格式非法（应为 YYYY-MM-DD）",
            "改为 YYYY-MM-DD"
        ))
        return
    try:
        d = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        findings.append(make_finding("error", cid, rel, f"{field}={value} 不是有效日期", "修正日期"))
        return
    if d > datetime.now(timezone.utc).date():
        findings.append(make_finding(
            "warning", cid, rel,
            f"{field}={value} 是未来日期",
            "核对是笔误还是时区差；knowledge_date 是知识发生时间，不应晚于今天"
        ))


def check_L17_knowledge_date(target: Path, kp_files: list[Path]) -> list[dict]:
    """L17: 知识时效字段缺失或非法。大面积报错时先跑 backfill_knowledge_date.py。"""
    findings = []
    for f in kp_files:
        fm = parse_frontmatter(f.read_text(encoding="utf-8"))
        rel = str(f.relative_to(target))
        if is_note_card(f, fm):
            if fm is None or not fm.get("date"):
                findings.append(make_finding(
                    "error", "L17", rel, "note 卡缺 date 字段", "补 YYYY-MM-DD 的笔记发生日期"
                ))
            elif fm.get("date"):
                check_valid_date(fm["date"], findings, "L17", rel, "date")
            continue
        if fm is None:
            continue  # 无 frontmatter 已由 L1 报告
        kd = fm.get("knowledge_date")
        if not kd:
            findings.append(make_finding(
                "error", "L17", rel,
                "缺 knowledge_date（知识发生时间）",
                "跑 scripts/backfill_knowledge_date.py --dry-run 批量回填"
            ))
            continue
        check_valid_date(kd, findings, "L17", rel, "knowledge_date")
        basis = fm.get("knowledge_date_basis")
        if basis and basis not in ALLOWED_DATE_BASIS:
            findings.append(make_finding(
                "warning", "L17", rel,
                f"knowledge_date_basis={basis} 非法",
                "改为 exact 或 approximate"
            ))
    return findings


def normalize_link_value(value) -> str:
    """superseded_by 取值 → 目标标识（容错：list 误判、单双层括号、引号、.md 后缀）。"""
    if isinstance(value, list):
        value = value[0] if value else ""
    v = str(value).strip().strip("'\"")
    m = re.match(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", v)
    if m:
        v = m.group(1)
    else:
        v = v.strip("[]")  # 极简解析器可能把 "[[X]]" 剥掉一层引号后误判为 list，残留单层括号
        m = re.match(r"\[\[([^\]|]+)\]\]", v)
        if m:
            v = m.group(1)
    return v.strip().removesuffix(".md").strip()


def longest_common_substring(a: str, b: str) -> str:
    """两字符串的最长公共子串（O(len_a*len_b)，卡片名很短，够用）。"""
    if not a or not b:
        return ""
    prev = [""] * (len(b) + 1)
    best = ""
    for i in range(1, len(a) + 1):
        cur = [""] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1] + a[i - 1]
                if len(cur[j]) > len(best):
                    best = cur[j]
        prev = cur
    return best


def check_L18_freshness_chains(target: Path, wiki_dir: Path, kp_files: list[Path]) -> list[dict]:
    """L18: 新旧体系健康——superseded_by 链（死链+回链）+ 同体系候选扫描。

    候选只列 info 不标取代：字面相似 ≠ 知识演进，判定必须 LLM 语义 + 用户确认
    （references/knowledge-freshness.md 第 6 节已知局限）。
    """
    findings = []
    stem_to_file = {}
    cards = []  # (file, fm, name, date)
    for f in kp_files:
        fm = parse_frontmatter(f.read_text(encoding="utf-8"))
        stem_to_file.setdefault(f.stem, f)
        if fm is None:
            continue
        name = (fm.get("kp_name") or fm.get("model_name") or fm.get("case_name")
                or fm.get("concept_name") or fm.get("note_name") or f.stem)
        date = fm.get("knowledge_date") or (fm.get("date") if is_note_card(f, fm) else None)
        cards.append((f, fm, name, date))

    # ① superseded_by 链健康
    linked_pairs = set()
    for f, fm, name, _ in cards:
        sup = fm.get("superseded_by")
        if not sup:
            continue
        key = normalize_link_value(sup)
        tf = None
        direct = (f.parent / f"{key}.md").resolve()
        if direct.exists():
            tf = direct
        else:
            tf = stem_to_file.get(key)
            if tf is None:  # 按 name 字段兜底
                tf = next((c[0] for c in cards if c[2] == key), None)
        if tf is None:
            findings.append(make_finding(
                "warning", "L18", str(f.relative_to(target)),
                f"superseded_by 死链: {key}",
                "修正为现存卡片的文件名/路径，或删除该字段"
            ))
            continue
        tf_resolved = tf.resolve()
        linked_pairs.add(frozenset({f.resolve(), tf_resolved}))
        tf_text = tf.read_text(encoding="utf-8")
        if f.stem not in tf_text and name not in tf_text:
            findings.append(make_finding(
                "info", "L18", str(tf_resolved.relative_to(target)),
                f"被取代关系缺回链: {key} 未提及 {f.stem}",
                f"在 {key} 的演进史/关联段写回 {f.stem} 及差异说明"
            ))

    # ② 同体系候选扫描（同领域 + 剔通用词后共享 ≥3 字中文子串 + 时间有先后 + 未标取代）
    by_domain = defaultdict(list)
    for f, fm, name, date in cards:
        domain = fm.get("knowledge_domain")
        if domain:
            by_domain[domain].append((f, name, date))

    def strip_stop_tokens(name: str) -> str:
        """先剔通用词再比对——「XX模型/XX方法」的后缀重叠不算同体系证据。"""
        out = name
        for stop in sorted(FRESHNESS_STOP_TOKENS, key=len, reverse=True):
            out = out.replace(stop, "")
        return out

    def is_cjk_shared(s: str) -> bool:
        """共享子串必须含中文且 ≥3 字——纯 ASCII 碎片（Agent/AI 前缀）是主题泛词切片。"""
        return len(s) >= 3 and any("一" <= ch <= "鿿" for ch in s)

    for domain, items in by_domain.items():
        dated = [(f, n, d) for f, n, d in items if d and DATE_RE.match(d)]
        for i in range(len(dated)):
            for j in range(i + 1, len(dated)):
                fa, na, da = dated[i]
                fb, nb, db = dated[j]
                if frozenset({fa.resolve(), fb.resolve()}) in linked_pairs:
                    continue
                shared = longest_common_substring(strip_stop_tokens(na), strip_stop_tokens(nb))
                if not is_cjk_shared(shared):
                    continue
                if da == db:
                    continue
                a_t, b_t = (fa, na, da), (fb, nb, db)
                old, new = (a_t, b_t) if da < db else (b_t, a_t)
                findings.append(make_finding(
                    "info", "L18",
                    f"{old[0].relative_to(target)}, {new[0].relative_to(target)}",
                    f"同体系候选（共享「{shared}」）: 旧 {old[1]}（{old[2]}） vs 新 {new[1]}（{new[2]}）",
                    "人工判定：取代（标 superseded_by+演进史回链）/ 互补（合并）/ 并存（边界对比关联）；拿不准保持现状"
                ))
    return findings


# ---------- 调度 ----------

LIGHT_CHECKS = ["L1", "L2", "L3", "L4", "L5", "L6", "L7", "L17"]
DEEP_CHECKS = LIGHT_CHECKS + ["L8", "L9", "L10", "L11", "L12", "L13", "L14", "L15", "L16", "L18"]

CHECK_REGISTRY = {
    "L1": ("frontmatter 必需字段缺失", lambda t, w, k: check_L1_frontmatter_required(t, k)),
    "L2": ("source_marking 取值非法", lambda t, w, k: check_L2_source_marking(t, k)),
    "L3": ("index.md 漂移", lambda t, w, k: check_L3_index_drift(t, w, k)),
    "L4": ("log.md 缺失或格式异常", lambda t, w, k: check_L4_log_format(t, w)),
    "L5": ("模块文件夹缺 _module-summary.md", lambda t, w, k: check_L5_module_summary(t, w)),
    "L6": ("文件命名违规", lambda t, w, k: check_L6_naming(t, k)),
    "L7": ("跨知识点链接失效", lambda t, w, k: check_L7_dead_links(t, k)),
    "L8": ("孤儿卡片", lambda t, w, k: check_L8_orphan(t, w, k)),
    "L9": ("陈旧 source_marking", lambda t, w, k: check_L9_stale_marking(t, w, k)),
    "L10": ("冲突块未决", lambda t, w, k: check_L10_unresolved_conflict(t, k)),
    "L11": ("跨课程同义未归并", lambda t, w, k: check_L11_cross_course_synonym(t, w, k)),
    "L12": ("frontmatter 字段值越界", lambda t, w, k: check_L12_field_value(t, k)),
    "L13": ("三线缺失或空泛", lambda t, w, k: check_L13_three_lines(t, w)),
    "L14": ("关联单边", lambda t, w, k: check_L14_one_way_relation(t, k)),
    "L15": ("raw 未编译", lambda t, w, k: check_L15_uncompiled_raw(t, w)),
    "L16": ("mapping.json 与现实不一致", lambda t, w, k: check_L16_mapping(t, w, k)),
    "L17": ("知识时效字段缺失或非法", lambda t, w, k: check_L17_knowledge_date(t, k)),
    "L18": ("新旧体系健康（superseded 链 + 同体系候选）", lambda t, w, k: check_L18_freshness_chains(t, w, k)),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="LLM Wiki 健康度扫描")
    parser.add_argument("target", type=Path, help="目标目录（含 wiki/）")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--light", action="store_true", help="轻量 7 项")
    g.add_argument("--deep", action="store_true", help="深度 16 项")
    g.add_argument("--check", action="append", help="单项，如 --check L8（可重复）")
    args = parser.parse_args()

    target: Path = args.target.resolve()
    if not target.exists():
        print(json.dumps({"error": f"目标目录不存在: {target}"}, ensure_ascii=False))
        return 2

    wiki_dir = target / "wiki"
    kp_files = collect_kp_files(wiki_dir)

    if args.light:
        ids = LIGHT_CHECKS
    elif args.deep:
        ids = DEEP_CHECKS
    else:
        ids = args.check

    findings: list[dict] = []
    skipped: list[str] = []
    for cid in ids:
        if cid not in CHECK_REGISTRY:
            skipped.append(cid)
            continue
        _, fn = CHECK_REGISTRY[cid]
        try:
            findings.extend(fn(target, wiki_dir, kp_files))
        except Exception as e:
            findings.append(make_finding(
                "warning", cid, str(target),
                f"检查执行失败: {type(e).__name__}: {e}",
                "查看脚本异常并修复"
            ))

    summary = defaultdict(int)
    for f in findings:
        summary[f["severity"]] += 1
    by_category = defaultdict(list)
    for f in findings:
        by_category[f["category"]].append(f)

    output = {
        "target": str(target),
        "wiki_exists": wiki_dir.exists(),
        "kp_files_count": len(kp_files),
        "checks_run": ids,
        "checks_skipped": skipped,
        "summary": {
            "error": summary.get("error", 0),
            "warning": summary.get("warning", 0),
            "info": summary.get("info", 0),
            "total": len(findings),
        },
        "by_category": {
            cid: {
                "name": CHECK_REGISTRY[cid][0],
                "count": len(by_category[cid]),
                "findings": by_category[cid],
            }
            for cid in ids if cid in CHECK_REGISTRY and by_category[cid]
        },
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
