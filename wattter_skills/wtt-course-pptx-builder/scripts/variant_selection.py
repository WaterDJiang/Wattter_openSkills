#!/usr/bin/env python3
"""Deterministic semantic profiling and controlled rotation for SVG variants.

The module is renderer-local: upstream design skills only describe generic
composition semantics. Explicit catalog metadata wins; filename inference keeps
all built-in Deck, Layout, and Chart SVGs eligible without a mass manual edit.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any


DEFAULT_VARIANT_POLICY: dict[str, Any] = {
    "mode": "controlled_rotation",
    "repeat_window": 3,
    "max_same_topology_run": 2,
    "equivalence_score_delta": 10,
    "deterministic_seed": "outline_hash",
}

_TOPOLOGY_ALIASES = {
    "split": "split",
    "columns": "split",
    "column": "split",
    "two-column": "split",
    "2col": "split",
    "左右": "split",
    "双栏": "split",
    "两栏": "split",
    "radial": "radial",
    "orbit": "radial",
    "circular": "radial",
    "circle": "radial",
    "环形": "radial",
    "轨道": "radial",
    "辐射": "radial",
    "grid": "grid",
    "matrix": "grid",
    "网格": "grid",
    "矩阵": "grid",
    "sequence": "sequence",
    "flow": "sequence",
    "timeline": "sequence",
    "roadmap": "sequence",
    "流程": "sequence",
    "时间线": "sequence",
    "layered": "layered",
    "layers": "layered",
    "pyramid": "layered",
    "funnel": "layered",
    "层级": "layered",
    "金字塔": "layered",
    "single_focus": "single_focus",
    "single-focus": "single_focus",
    "hero": "single_focus",
    "single": "single_focus",
    "单焦点": "single_focus",
}

_EMPHASIS_ALIASES = {
    "center": "center",
    "centre": "center",
    "central": "center",
    "center-divider": "center",
    "focal": "center",
    "中心": "center",
    "居中": "center",
    "balanced": "balanced",
    "balance": "balanced",
    "equal": "balanced",
    "均衡": "balanced",
    "平衡": "balanced",
    "directional": "directional",
    "direction": "directional",
    "方向": "directional",
    "hierarchy": "hierarchy",
    "hierarchical": "hierarchy",
    "层级": "hierarchy",
    "distributed": "distributed",
    "分布": "distributed",
    "neutral": "neutral",
    "standard": "neutral",
}

_TOPOLOGY_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "radial",
        (
            "orbit",
            "radial",
            "hub_spoke",
            "hub-spoke",
            "wheel",
            "cycle",
            "circular",
            "radar",
            "sunburst",
            "donut",
            "环形",
            "轨道",
            "辐射",
            "闭环",
        ),
    ),
    (
        "split",
        (
            "compare",
            "comparison",
            "pros_cons",
            "pros-cons",
            "before_after",
            "before-after",
            "two_col",
            "2col",
            "dual",
            "butterfly",
            "versus",
            "左右",
            "双栏",
            "两栏",
            "对比",
        ),
    ),
    (
        "grid",
        (
            "matrix",
            "grid",
            "cards",
            "table",
            "agenda",
            "quadrant",
            "heatmap",
            "treemap",
            "网格",
            "矩阵",
            "卡片",
            "表格",
        ),
    ),
    (
        "sequence",
        (
            "flow",
            "timeline",
            "roadmap",
            "swimlane",
            "process",
            "steps",
            "journey",
            "sankey",
            "waterfall",
            "流程",
            "时间线",
            "路线图",
            "步骤",
        ),
    ),
    (
        "layered",
        (
            "pyramid",
            "funnel",
            "layer",
            "hierarchy",
            "tree",
            "金字塔",
            "漏斗",
            "层级",
            "树状",
        ),
    ),
    (
        "single_focus",
        (
            "hero",
            "quote",
            "gauge",
            "single",
            "feature",
            "spotlight",
            "大数字",
            "单焦点",
            "金句",
        ),
    ),
)


def _normalized_text(*values: Any) -> str:
    leaves: list[str] = []
    for value in values:
        if isinstance(value, str):
            leaves.append(value)
        elif isinstance(value, list):
            leaves.extend(str(item) for item in value)
        elif isinstance(value, dict):
            leaves.extend(str(item) for item in value.values())
    return re.sub(r"[\s/|]+", " ", " ".join(leaves).lower())


def normalize_topology(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip().lower().replace("_", "-")
    if normalized in _TOPOLOGY_ALIASES:
        return _TOPOLOGY_ALIASES[normalized]
    for alias, topology in _TOPOLOGY_ALIASES.items():
        if alias in normalized:
            return topology
    return normalized.replace("-", "_")


def normalize_emphasis(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip().lower().replace("_", "-")
    if normalized in _EMPHASIS_ALIASES:
        return _EMPHASIS_ALIASES[normalized]
    for alias, emphasis in _EMPHASIS_ALIASES.items():
        if alias in normalized:
            return emphasis
    return normalized.replace("-", "_")


def infer_variant_profile(
    identifier: str,
    *,
    selection: dict[str, Any] | None = None,
    tag: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Return a non-empty generic variant profile for any SVG candidate."""
    selection = selection or {}
    tag = tag or {}
    explicit = selection.get("variant_profile")
    if not isinstance(explicit, dict):
        explicit = {}
    dimensions = tag.get("dimensions")
    if not isinstance(dimensions, dict):
        dimensions = {}

    text = _normalized_text(
        identifier,
        selection.get("structure"),
        selection.get("keywords"),
        selection.get("content_forms"),
        tag.get("content_forms"),
        dimensions,
    )
    topology = normalize_topology(
        explicit.get("topology") or selection.get("topology")
    )
    if not topology:
        topology = next(
            (
                candidate
                for candidate, patterns in _TOPOLOGY_PATTERNS
                if any(pattern in text for pattern in patterns)
            ),
            "standard",
        )

    emphasis = normalize_emphasis(
        explicit.get("emphasis") or selection.get("emphasis")
    )
    if not emphasis:
        emphasis = {
            "radial": "center",
            "single_focus": "center",
            "split": "balanced",
            "grid": "balanced",
            "sequence": "directional",
            "layered": "hierarchy",
        }.get(topology, "neutral")

    visual_weight = explicit.get("visual_weight") or selection.get("visual_weight")
    if visual_weight not in {"standard", "hero", "dense"}:
        if any(token in text for token in ("hero", "orbit", "radial", "feature", "quote")):
            visual_weight = "hero"
        elif any(token in text for token in ("table", "matrix", "swimlane", "heatmap")):
            visual_weight = "dense"
        else:
            visual_weight = "standard"
    return {
        "topology": topology,
        "emphasis": emphasis,
        "visual_weight": visual_weight,
    }


def requested_variant_profile(intent: dict[str, Any]) -> dict[str, str]:
    """Read only renderer-neutral intent fields; never inspect template ids."""
    composition = intent.get("composition")
    if not isinstance(composition, dict):
        composition = {}
    topology = normalize_topology(composition.get("topology"))
    emphasis = normalize_emphasis(composition.get("emphasis"))

    description = intent.get("visual_description")
    if not topology and isinstance(description, str):
        description_text = description.lower()
        topology = next(
            (
                candidate
                for candidate, patterns in _TOPOLOGY_PATTERNS
                if any(pattern in description_text for pattern in patterns)
            ),
            None,
        )
    if not emphasis and isinstance(description, str):
        description_text = description.lower()
        emphasis = next(
            (
                normalized
                for alias, normalized in _EMPHASIS_ALIASES.items()
                if alias in description_text
            ),
            None,
        )
    result: dict[str, str] = {}
    if topology:
        result["topology"] = topology
    if emphasis:
        result["emphasis"] = emphasis
    return result


def local_variant_precision(
    layout: dict[str, Any] | None,
    intent: dict[str, Any],
    variant_files: set[str],
) -> tuple[bool, list[str]]:
    """Classify a local form candidate after its semantic gate was checked.

    A broad content-form tag admits a page for consideration; it is not proof
    that this particular page is a precise fit for the requested content.
    """
    if not layout or layout.get("file") not in variant_files:
        return False, ["no local page tagged for resolved form"]
    selection = layout.get("selection") or {}
    wanted_count = intent.get("item_count")
    actual_count = selection.get("item_count")
    if isinstance(actual_count, int) and not isinstance(actual_count, bool):
        if not isinstance(wanted_count, int) or isinstance(wanted_count, bool):
            return False, ["local fixed slots require declared intent item_count"]
        if wanted_count != actual_count:
            return False, [
                f"local fixed slots differ: wanted={wanted_count}, actual={actual_count}"
            ]
    image_requirements = selection.get("image_requirements") or []
    requires_content_image = any(
        not any(marker in str(item) for marker in ("不要求", "无需", "可选", "或可编辑"))
        for item in image_requirements
    )
    if requires_content_image and intent.get("image_need") != "required":
        return False, ["local page requires content images"]
    composition = intent.get("composition")
    if isinstance(composition, dict) and composition.get("topology"):
        requested = requested_variant_profile(intent)
        requested_topology = requested.get("topology")
        requested_emphasis = requested.get("emphasis")
        profile = infer_variant_profile(
            str(layout.get("file") or layout.get("reference") or ""),
            selection=selection,
        )
        if requested_topology and profile["topology"] != requested_topology:
            return False, [
                f"local composition differs: wanted={requested_topology}, actual={profile['topology']}"
            ]
        if requested_emphasis and profile["emphasis"] != requested_emphasis:
            return False, [
                f"local emphasis differs: wanted={requested_emphasis}, actual={profile['emphasis']}"
            ]
    if selection.get("semantic_require_any"):
        return True, ["local purpose gate matched"]
    if isinstance(composition, dict) and composition.get("topology"):
        if requested_topology in {"radial", "layered", "single_focus"}:
            return True, [
                f"explicit distinctive composition matched: {requested_topology}"
            ]
    return False, ["local page has only a broad content-form match"]


def _stable_jitter(seed: str, page_id: str, candidate_id: str) -> int:
    digest = hashlib.sha256(
        f"{seed}|{page_id}|{candidate_id}".encode("utf-8")
    ).hexdigest()
    return int(digest[:8], 16) % 10


def select_controlled_variant(
    candidates: list[dict[str, Any]],
    *,
    page_id: str,
    seed: str,
    requested_profile: dict[str, str] | None = None,
    history: list[dict[str, str]] | None = None,
    enabled: bool = True,
    policy: dict[str, Any] | None = None,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """Select one candidate from a semantically equivalent deterministic pool.

    Candidate shape:
      id, base_score, profile, payload, reasons
    """
    policy = {**DEFAULT_VARIANT_POLICY, **(policy or {})}
    requested_profile = requested_profile or {}
    history = history or []
    if not candidates:
        return None, {
            "enabled": enabled,
            "requested_profile": requested_profile,
            "selected_profile": None,
            "equivalent_pool": [],
            "reason": "no candidates",
        }

    working = list(candidates)
    requested_topology = requested_profile.get("topology")
    if requested_topology:
        exact = [
            item
            for item in working
            if (item.get("profile") or {}).get("topology") == requested_topology
        ]
        if exact:
            working = exact

    for item in working:
        semantic_score = int(item.get("base_score") or 0)
        profile = item.get("profile") or {}
        if requested_topology and profile.get("topology") == requested_topology:
            semantic_score += 30
        requested_emphasis = requested_profile.get("emphasis")
        if requested_emphasis and profile.get("emphasis") == requested_emphasis:
            semantic_score += 12
        item["_semantic_score"] = semantic_score

    best_semantic = max(item["_semantic_score"] for item in working)
    delta = int(policy["equivalence_score_delta"])
    pool = [
        item
        for item in working
        if best_semantic - item["_semantic_score"] <= delta
    ]

    repeat_window = max(1, int(policy["repeat_window"]))
    topology_run = max(1, int(policy["max_same_topology_run"]))
    recent = history[-repeat_window:]
    recent_ids = {item.get("id") for item in recent}
    recent_topologies = [
        item.get("topology") for item in history[-topology_run:]
    ]
    for item in pool:
        profile = item.get("profile") or {}
        repeat_penalty = -40 if item.get("id") in recent_ids and len(pool) > 1 else 0
        topology_penalty = (
            -25
            if len(pool) > 1
            and len(recent_topologies) == topology_run
            and all(
                topology == profile.get("topology")
                for topology in recent_topologies
            )
            else 0
        )
        jitter = _stable_jitter(seed, page_id, str(item.get("id")))
        item["_rotation_adjustment"] = (
            repeat_penalty + topology_penalty if enabled else 0
        )
        item["_deterministic_tiebreak"] = jitter if enabled else 0
        item["_final_score"] = (
            item["_semantic_score"]
            + item["_rotation_adjustment"]
            + item["_deterministic_tiebreak"]
        )

    if enabled:
        pool.sort(
            key=lambda item: (
                item["_final_score"],
                item["_semantic_score"],
                str(item.get("id")),
            ),
            reverse=True,
        )
        reason = "controlled rotation within semantic-equivalence pool"
    else:
        pool.sort(
            key=lambda item: (
                item["_semantic_score"],
                -int(item.get("position") or 0),
            ),
            reverse=True,
        )
        reason = "stable selection; rotation disabled"
    selected = pool[0]
    audit = {
        "enabled": enabled,
        "requested_profile": requested_profile,
        "selected_profile": selected.get("profile"),
        "equivalent_pool": [item.get("id") for item in pool],
        "semantic_score": selected["_semantic_score"],
        "rotation_adjustment": selected["_rotation_adjustment"],
        "deterministic_tiebreak": selected["_deterministic_tiebreak"],
        "reason": reason,
    }
    return selected, audit
