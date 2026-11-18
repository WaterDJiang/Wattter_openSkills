#!/usr/bin/env python3
"""Deterministic v1.2 visual contract checks; no content generation."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

KINDS = {"none", "parallel", "causal", "steps", "comparison", "rubric", "demonstration", "practice"}
RELATIONSHIP = {"none": "none", "parallel": "parallel", "causal": "causal", "steps": "sequence", "comparison": "comparison", "rubric": "orthogonal", "demonstration": "sequence"}
TOPOLOGY = {"parallel": {"grid", "parallel", "columns"}, "causal": {"cause_effect", "branch"}, "steps": {"sequence"}, "comparison": {"split", "table"}, "rubric": {"table", "matrix"}, "demonstration": {"sequence"}}
GENERIC = re.compile(r"^(?:逐行顺读|图文结合|纵向排列|高亮关键点|单焦点页面[，,]?内容清晰可读)[。.!！]?$|pros_cons|红绿(?:对比|配色)|正确.*(?:绿色|放大)|错误.*红色", re.I)


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def inserted_source_page(intent: dict, *, legacy: bool = False) -> dict:
    page = {"page_id": intent.get("page_id"), "slide_text": intent.get("ins_content", {})}
    # The original insertion fingerprint covered only the ID and visible text.
    if not legacy:
        for key in ("speaker_notes_ref", "teaching"):
            if key in intent:
                page[key] = intent[key]
    return page


def page_hash(page: dict, root: Path, *, legacy: bool = False,
              material_hashes: dict[Path, str | None] | None = None) -> str:
    """Bind page/teaching fields, retaining the original notes-inclusive fingerprint."""
    if not legacy:
        visual_page = {key: value for key, value in page.items() if key != "speaker_notes_ref"}
        teaching = page.get("teaching")
        refs = teaching.get("material_refs") if isinstance(teaching, dict) else None
        if isinstance(refs, list) and refs:
            cache = {} if material_hashes is None else material_hashes
            digests = {}
            for ref in refs:
                if not isinstance(ref, str):
                    continue
                name = ref.partition("#")[0]
                path = (root / name).resolve()
                if not name or "://" in name or Path(name).is_absolute() or not path.is_relative_to(root.resolve()):
                    digests[ref] = None
                    continue
                if path not in cache:
                    cache[path] = None
                    if path.is_file():
                        digest = hashlib.sha256()
                        with path.open("rb") as stream:
                            for chunk in iter(lambda: stream.read(65536), b""):
                                digest.update(chunk)
                        cache[path] = digest.hexdigest()
                digests[ref] = cache[path]
            return "visual-" + canonical_hash({"page": visual_page, "material_sha256": digests})
        return "visual-" + canonical_hash(visual_page)

    ref = page.get("speaker_notes_ref")
    notes_hash = None
    if ref:
        name = ref.partition("#")[0] if isinstance(ref, str) else ""
        path = (root / name).resolve()
        if not name or Path(name).is_absolute() or not path.is_relative_to(root.resolve()) or not path.is_file():
            raise ValueError(f"{page.get('page_id')}.speaker_notes_ref: missing/unsafe file {ref!r}")
        notes_hash = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    return canonical_hash({"page": page, "speaker_notes_sha256": notes_hash})


def resolve(page: dict, ref: str) -> Any:
    """JSON Pointer rooted in slide_text; references never contain duplicate text."""
    if not isinstance(ref, str) or not ref.startswith("/slide_text/"):
        raise ValueError(f"invalid visible field reference {ref!r}; use /slide_text/... JSON Pointer")
    current: Any = page
    for token in ref[1:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        try:
            if isinstance(current, list):
                if not re.fullmatch(r"0|[1-9]\d*", token):
                    raise KeyError(token)
                current = current[int(token)]
            elif isinstance(current, dict):
                current = current[token]
            else:
                raise KeyError(token)
        except (KeyError, IndexError):
            raise ValueError(f"unresolved field {ref}") from None
    return current


def leaves(value: Any, prefix: str) -> set[str]:
    if isinstance(value, dict):
        return set().union(*(leaves(v, prefix + "/" + k.replace("~", "~0").replace("/", "~1")) for k, v in value.items())) if value else set()
    if isinstance(value, list):
        return set().union(*(leaves(v, prefix + "/" + str(i)) for i, v in enumerate(value))) if value else set()
    return {prefix}


def validate_visual(intent: dict, page: dict, pages: list[dict], root: Path,
                    material_hashes: dict[Path, str | None] | None = None) -> list[str]:
    errors: list[str] = []
    label = f"{intent.get('page_id')}.visual_contract"
    vc = intent.get("visual_contract")
    if not isinstance(vc, dict):
        return [f"{label}: v1.2 requires an object; legacy description is insufficient"]

    def fail(field: str, message: str) -> None:
        errors.append(f"{label}.{field}: {message}")

    def text(field: str, value: Any) -> None:
        if not isinstance(value, str) or not value.strip() or GENERIC.search(value.strip()):
            fail(field, "specific non-generic explanation required")

    def refs(field: str, value: Any, *, empty: bool = False, container: bool = False) -> set[str]:
        if not isinstance(value, list) or (not value and not empty):
            fail(field, "field-reference array required")
            return set()
        result: set[str] = set()
        for ref in value:
            try:
                target = resolve(page, ref)
                if isinstance(target, (dict, list)) and not container:
                    raise ValueError(f"{ref}: scalar leaf required")
                found = leaves(target, ref)
                if result & found:
                    fail(field, f"duplicate fields {sorted(result & found)}")
                result |= found
            except ValueError as exc:
                fail(field, str(exc))
        return result

    try:
        observed = vc.get("source_page_hash")
        legacy = isinstance(observed, str) and observed.startswith("sha256:")
        hashed_page = inserted_source_page(intent, legacy=True) if legacy and intent.get("origin") == "inserted" else page
        expected = page_hash(hashed_page, root, legacy=legacy, material_hashes=material_hashes)
        if observed != expected:
            scope = "content/notes" if legacy else "visual content/materials"
            fail("source_page_hash", f"stale {scope}; expected {expected}; recheck scope/count/focus/placements/reading_order")
    except (OSError, ValueError) as exc:
        fail("source_page_hash", str(exc))
    for field in ("teaching_purpose", "core_conclusion"):
        text(field, vc.get(field))
    text("visual_description", intent.get("visual_description"))
    focus = refs("focus_refs", vc.get("focus_refs"))
    relation = vc.get("relation")
    if not isinstance(relation, dict):
        fail("relation", "object required")
        relation = {}
    kind = relation.get("kind")
    if not isinstance(kind, str) or kind not in KINDS:
        fail("relation.kind", f"expected one of {sorted(KINDS)}")
        kind = "invalid"
    if kind in RELATIONSHIP and intent.get("relationship") != RELATIONSHIP[kind]:
        fail("relation.kind", f"{kind} requires relationship={RELATIONSHIP[kind]}")
    composition = intent.get("composition") or {}
    if not isinstance(composition, dict):
        composition = {}
    if kind in TOPOLOGY and composition.get("topology") not in TOPOLOGY[kind]:
        fail("relation.kind", f"{kind} incompatible topology={composition.get('topology')!r}")
    scope = refs("relation.scope_refs", relation.get("scope_refs"), container=True)
    objects = relation.get("objects")
    if not isinstance(objects, list) or not objects:
        fail("relation.objects", "non-empty object-reference array required")
        objects = []
    used: set[str] = set()
    for i, obj in enumerate(objects):
        obj_refs = refs(f"relation.objects[{i}]", obj)
        if used & obj_refs:
            fail(f"relation.objects[{i}]", f"overlap with other object: {sorted(used & obj_refs)}")
        used |= obj_refs
    if type(intent.get("item_count")) is not int or intent.get("item_count") != len(objects):
        fail("relation.objects", f"item_count={intent.get('item_count')!r}, actual objects={len(objects)}")
    if kind == "none" and len(objects) != 1:
        fail("relation.objects", "none is a single-object page, not an unspecified multi-object relation")
    teaching = page.get("teaching") or {}
    if not isinstance(teaching, dict):
        teaching = {}
    if kind == "demonstration" and teaching.get("mode") != "demo":
        fail("relation.kind", "demonstration requires the original teaching.mode=demo")
    if kind == "practice" and teaching.get("mode") != "practice" and page.get("page_type") != "exercise":
        fail("relation.kind", "practice requires original teaching.mode=practice or page_type=exercise")
    if scope != used:
        fail("relation.scope_refs", f"scope/object mismatch; unmapped={sorted(scope-used)}, outside={sorted(used-scope)}")
    hint = intent.get("content_form_hint")
    match = re.fullmatch(r"points_(\d+)", hint) if isinstance(hint, str) else None
    if match and int(match.group(1)) != len(objects):
        fail("relation.objects", f"content_form_hint={hint} carries an obsolete count; actual={len(objects)}")
    # Only explicit relation counts are checked; unrelated dates/scores are ignored.
    number = r"(\d+|[一二两三四五六七八九十])"
    units = {"parallel": r"(?:条线(?:任务)?|项任务|项并列|项(?=[，。；：\s]|$))", "steps": r"(?:段操作|段流程|步(?:操作|流程)?)", "comparison": r"个选项"}
    numeral = {"一":1,"二":2,"两":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9,"十":10}
    if kind in units:
        for field, value in [("visual_description", intent.get("visual_description")), ("composition.emphasis", composition.get("emphasis"))]:
            if isinstance(value, str):
                for count in re.findall(number + r"\s*" + units[kind], value):
                    actual = int(count) if count.isdigit() else numeral[count]
                    if actual != len(objects):
                        fail(field, f"obsolete explicit relation count {count}; actual objects={len(objects)}")
    all_visible = leaves(page.get("slide_text", {}), "/slide_text")
    # raw_markdown is legacy author metadata, not visible content.
    all_visible = {ref for ref in all_visible if ref != '/slide_text/raw_markdown' and not ref.startswith('/slide_text/raw_markdown/')}
    placements = vc.get("placements")
    if not isinstance(placements, list) or not placements:
        fail("placements", "non-empty region/reference array required")
        placements = []
    placed: set[str] = set()
    for i, placement in enumerate(placements):
        if not isinstance(placement, dict):
            fail(f"placements[{i}]", "object required")
            continue
        text(f"placements[{i}].region", placement.get("region"))
        fields = refs(f"placements[{i}].refs", placement.get("refs"))
        if fields & placed:
            fail(f"placements[{i}].refs", f"duplicate placement {sorted(fields & placed)}")
        placed |= fields
    if placed != all_visible:
        fail("placements", f"unplaced={sorted(all_visible-placed)}, outside={sorted(placed-all_visible)}")
    if not focus <= placed:
        fail("focus_refs", f"focus lacks placement: {sorted(focus-placed)}")
    order = vc.get("reading_order")
    if not isinstance(order, list) or not order:
        fail("reading_order", "ordered array of field-reference arrays required; same stage = simultaneous")
        order = []
    read: set[str] = set()
    for i, stage in enumerate(order):
        fields = refs(f"reading_order[{i}]", stage)
        if read & fields:
            fail(f"reading_order[{i}]", f"duplicate reading fields {sorted(read & fields)}")
        read |= fields
    if read != placed:
        fail("reading_order", f"missing={sorted(placed-read)}, unplaced={sorted(read-placed)}")
    timing = vc.get("timing")
    if not isinstance(timing, dict):
        fail("timing", "object required, including non-question pages")
        timing = {}
    mode = timing.get("mode")
    if not isinstance(mode, str) or mode not in {"not_applicable", "immediate", "separate_page"}:
        fail("timing.mode", "expected not_applicable/immediate/separate_page")
    questions = refs("timing.question_refs", timing.get("question_refs"), empty=True)
    answers = refs("timing.answer_refs", timing.get("answer_refs"), empty=True)
    answer_ids = timing.get("answer_page_ids")
    if not isinstance(answer_ids, list) or not all(isinstance(x, str) for x in answer_ids):
        fail("timing.answer_page_ids", "page-id array required")
        answer_ids = []
    by_id = {p.get('page_id'): p for p in pages}
    linked_answers = [p.get('page_id') for p in pages if isinstance(p.get('teaching'), dict) and p['teaching'].get('reveal_after') == page.get('page_id')]
    if linked_answers and (mode != "separate_page" or set(answer_ids) != set(linked_answers)):
        fail("timing.answer_page_ids", f"original reveal_after links require separate_page and answers {linked_answers}")
    if teaching.get('reveal_after') is not None and (mode != 'immediate' or not answers):
        fail("timing.answer_refs", "original reveal page must identify its answer fields in immediate mode")
    if mode == "not_applicable" and (questions or answers or answer_ids):
        fail("timing", "not_applicable cannot contain question/answer references")
    if mode == "immediate" and (questions or answer_ids):
        fail("timing", "immediate cannot reveal answers on a question page")
    if mode == "separate_page":
        if not questions or answers or not answer_ids:
            fail("timing", "question references and later answer page required; answers forbidden on question page")
        for pid in answer_ids:
            target = by_id.get(pid)
            if target is None or target.get('sequence', 0) <= page.get('sequence', 0):
                fail("timing.answer_page_ids", f"{pid}: answer must be a later existing page")
            elif target.get('teaching', {}).get('reveal_after') != page.get('page_id'):
                fail("timing.answer_page_ids", f"{pid}.teaching.reveal_after must be {page.get('page_id')}")
    if kind == "comparison" and mode == "separate_page":
        if timing.get("neutral_choices") is not True:
            fail("timing.neutral_choices", "question comparison must be neutral")
        style = vc.get("choice_style")
        if style != {"equal_color": True, "equal_size": True, "equal_weight": True}:
            fail("choice_style", "neutral question requires equal color, size and weight")
        if len(objects) < 2 or not any(used <= refs("reading_order.choice_stage", stage) for stage in order):
            fail("reading_order", "neutral choices must be read in one simultaneous stage")
        if focus != used:
            fail("focus_refs", "neutral comparison focus must include all choices equally")
        if re.search(r"pros_cons|正确.*(?:绿|放大)|错误.*红|甲优于乙|乙优于甲|先看答案", json.dumps({"description": intent.get('visual_description'), "composition": composition}, ensure_ascii=False)):
            fail("choice_style", "visual description/composition cues the answer")
    if kind == "rubric":
        rubrics = vc.get("rubrics")
        if not isinstance(rubrics, list) or not rubrics:
            fail("rubrics", "separate source-backed rubric rows/totals required")
            rubrics = []
        rubric_refs: set[str] = set()
        rubric_scopes: set[str] = set()
        for i, rubric in enumerate(rubrics):
            if not isinstance(rubric, dict):
                fail(f"rubrics[{i}]", "object required")
                continue
            scope_ref = rubric.get("scope_ref")
            try:
                source_rubric = resolve(page, scope_ref)
                if not isinstance(source_rubric, dict):
                    raise ValueError("rubric scope must be a source object")
                if scope_ref in rubric_scopes:
                    raise ValueError("distinct rubrics cannot be merged/reused")
                rubric_scopes.add(scope_ref)
            except ValueError as exc:
                fail(f"rubrics[{i}].scope_ref", str(exc))
                source_rubric = {}
                scope_ref = "/invalid"
            rows = rubric.get("rows")
            if not isinstance(rows, list) or not rows:
                fail(f"rubrics[{i}].rows", "dimension/score/standard reference rows required")
                continue
            for j, row in enumerate(rows):
                if not isinstance(row, dict) or set(row) != {"dimension_ref", "score_ref", "standard_ref"}:
                    fail(f"rubrics[{i}].rows[{j}]", "dimension_ref/score_ref/standard_ref required")
                    continue
                row_refs = refs(f"rubrics[{i}].rows[{j}]", list(row.values()))
                if row_refs and (len({r.rsplit('/', 1)[0] for r in row_refs}) != 1 or not all(r.startswith(scope_ref + '/') for r in row_refs)):
                    fail(f"rubrics[{i}].rows[{j}]", "dimension/score/standard must belong to the same source row and rubric")
                if row_refs not in [set(obj) for obj in objects if isinstance(obj, list) and all(isinstance(r,str) for r in obj)]:
                    fail(f"rubrics[{i}].rows[{j}]", "row must match exactly one relation object")
                if rubric_refs & row_refs:
                    fail(f"rubrics[{i}].rows[{j}]", "row reused across rubrics")
                rubric_refs |= row_refs
            # A total is a source reference, never a generated sum; null = source has none.
            total = rubric.get("total_ref")
            if total is not None:
                refs(f"rubrics[{i}].total_ref", [total])
                if not isinstance(total, str) or not total.startswith(scope_ref + '/'):
                    fail(f"rubrics[{i}].total_ref", "total must reference this rubric; no combined/generated total")
            if "total" in source_rubric and total != scope_ref + '/total':
                fail(f"rubrics[{i}].total_ref", "preserve this rubric's original total reference")
        if rubric_refs != used:
            fail("rubrics", f"rubric/relationship rows mismatch: {sorted(rubric_refs ^ used)}")
    return errors
