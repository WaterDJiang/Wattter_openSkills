#!/usr/bin/env python3
"""Query, resolve, and validate semantic template page catalogs.

Canonical mirror/fidelity filename::

    <NNN>_<page_type>_<layout_id>.svg

``page_catalog.json`` keeps selection metadata beside the SVG files and maps
legacy basenames to the canonical semantic reference without duplicating SVGs.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    from template_capabilities import CAPABILITY_FILE, validate_capabilities
    from update_spec import parse_lock
    from variant_selection import (
        infer_variant_profile,
        local_variant_precision,
        normalize_emphasis,
        normalize_topology,
        requested_variant_profile,
    )
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from template_capabilities import CAPABILITY_FILE, validate_capabilities
    from update_spec import parse_lock
    from variant_selection import (
        infer_variant_profile,
        local_variant_precision,
        normalize_emphasis,
        normalize_topology,
        requested_variant_profile,
    )


CANONICAL_PAGE_TYPES = {"cover", "toc", "chapter", "content", "ending"}
REFERENCE_FORMATS = {
    "<NNN>_<page_type>_<layout_id>",
    "basename",
}
PAGE_USAGES = {"output", "reference_only"}
SEMANTIC_STEM_RE = re.compile(
    r"^(?P<order>\d{3})_"
    r"(?P<page_type>cover|toc|chapter|content|ending)_"
    r"(?P<layout_id>[a-z0-9]+(?:_[a-z0-9]+)*)$"
)
CONTENT_DENSITIES = {"low", "medium", "high"}
PAGE_RENDER_MODES = {"mirror", "brand_shell", "themed_rebuild"}
PAGE_PROVENANCE_KINDS = {"source_mirror", "adapted_component"}


class CatalogError(RuntimeError):
    """Raised when a page catalog cannot be loaded or resolved."""


def load_catalog(template_dir: Path) -> dict[str, Any]:
    path = template_dir / "page_catalog.json"
    if not path.exists():
        raise CatalogError(f"missing page_catalog.json in {template_dir}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CatalogError(f"invalid page_catalog.json: {exc}") from exc
    if not isinstance(data, dict):
        raise CatalogError("page_catalog.json root must be an object")
    return data


def _page_search_text(page: dict[str, Any]) -> str:
    selection = page.get("selection") or {}
    values: list[str] = [
        str(page.get("reference", "")),
        str(page.get("layout_id", "")),
        str(page.get("label", "")),
        str(selection.get("structure", "")),
    ]
    for key in (
        "aliases",
        "use_cases",
        "keywords",
        "content_slots",
        "visuals",
        "image_requirements",
        "semantic_require_any",
        "semantic_exclude_any",
    ):
        source = page.get(key) if key == "aliases" else selection.get(key)
        if isinstance(source, list):
            values.extend(str(item) for item in source)
    return " ".join(values).lower()


def resolve_reference(catalog: dict[str, Any], reference: str) -> dict[str, Any]:
    """Resolve canonical basename, layout_id, filename, or legacy alias."""
    needle = Path(reference).name
    if needle.endswith(".svg"):
        needle = needle[:-4]

    pages = catalog.get("pages")
    if not isinstance(pages, list):
        raise CatalogError("page_catalog.json pages must be an array")

    exact: list[dict[str, Any]] = []
    layout_matches: list[dict[str, Any]] = []
    alias_matches: list[dict[str, Any]] = []
    for page in pages:
        if not isinstance(page, dict):
            continue
        if needle == page.get("reference") or f"{needle}.svg" == page.get("file"):
            exact.append(page)
        if needle == page.get("layout_id"):
            layout_matches.append(page)
        if needle in (page.get("aliases") or []):
            alias_matches.append(page)

    matches = exact or layout_matches or alias_matches
    if not matches:
        raise CatalogError(f"unknown template page reference: {reference}")
    if len(matches) > 1:
        refs = ", ".join(str(page.get("reference")) for page in matches)
        raise CatalogError(f"ambiguous template page reference {reference!r}: {refs}")
    return matches[0]


def search_catalog(
    catalog: dict[str, Any],
    query: str,
    *,
    page_type: str | None = None,
    content_form: str | None = None,
    item_count: int | None = None,
    density: str | None = None,
    topology: str | None = None,
    emphasis: str | None = None,
    image_need: str | None = None,
    precise_only: bool = False,
    limit: int = 5,
    include_reference: bool = False,
) -> list[dict[str, Any]]:
    """Return ranked pages for a lightweight Chinese/English semantic query."""
    if page_type and page_type not in CANONICAL_PAGE_TYPES:
        raise CatalogError(f"invalid page_type: {page_type}")
    normalized = query.strip().lower()
    normalized_compact = "".join(normalized.split())
    tokens = [token for token in re.split(r"[\s,，、/|;；]+", normalized) if token]
    query_profile = requested_variant_profile(
        {
            "composition": {
                "topology": topology,
                "emphasis": emphasis,
            },
            "visual_description": query,
        }
    )
    pages = catalog.get("pages")
    if not isinstance(pages, list):
        raise CatalogError("page_catalog.json pages must be an array")

    ranked: list[tuple[int, int, dict[str, Any]]] = []
    for position, page in enumerate(pages):
        if not isinstance(page, dict):
            continue
        if page.get("usage", "output") == "reference_only" and not include_reference:
            continue
        if page_type and page.get("page_type") != page_type:
            continue
        selection = page.get("selection") or {}
        exact_reference = normalized in {
            str(page.get("reference", "")).lower(),
            str(page.get("layout_id", "")).lower(),
            *(str(alias).lower() for alias in page.get("aliases") or []),
        }
        if not exact_reference:
            required = selection.get("semantic_require_any") or []
            excluded = selection.get("semantic_exclude_any") or []
            def matches_term(term: object) -> bool:
                lowered = str(term).lower()
                return lowered in normalized or "".join(lowered.split()) in normalized_compact
            if normalized and required and not any(
                matches_term(term) for term in required
            ):
                continue
            if normalized and any(matches_term(term) for term in excluded):
                continue
            if (
                item_count is not None
                and selection.get("strict_item_count") is True
                and selection.get("item_count") != item_count
            ):
                continue
        page_forms = selection.get("content_forms") or []
        if content_form:
            if content_form in page_forms:
                form_score = 60
            elif page_forms:
                continue
            elif selection.get("generic_shell"):
                form_score = 5
            else:
                continue
        else:
            form_score = 0
        if precise_only and content_form and not exact_reference:
            precise, _fit_reasons = local_variant_precision(
                page,
                {
                    "item_count": item_count,
                    "image_need": image_need,
                    "composition": {"topology": topology, "emphasis": emphasis},
                },
                {str(page.get("file"))} if content_form in page_forms else set(),
            )
            if not precise:
                continue
        haystack = _page_search_text(page)
        score = form_score
        if normalized and any(
            str(term).lower() in normalized
            or "".join(str(term).lower().split()) in normalized_compact
            for term in selection.get("semantic_require_any") or []
        ):
            score += 45
        variant_profile = infer_variant_profile(
            str(page.get("file") or page.get("reference") or ""),
            selection=selection,
        )
        requested_topology = query_profile.get("topology")
        if requested_topology and variant_profile["topology"] == requested_topology:
            score += 20
        requested_emphasis = query_profile.get("emphasis")
        if requested_emphasis and variant_profile["emphasis"] == requested_emphasis:
            score += 8
        if item_count is not None:
            actual_count = selection.get("item_count")
            if actual_count == item_count:
                score += 25
            elif actual_count is not None:
                score -= 15
        if density and selection.get("content_density") == density:
            score += 8
        if normalized:
            if normalized == str(page.get("reference", "")).lower():
                score += 100
            if normalized == str(page.get("layout_id", "")).lower():
                score += 90
            if normalized in [str(a).lower() for a in page.get("aliases") or []]:
                score += 80
            if normalized in haystack:
                score += 12
            score += sum(3 for token in tokens if token in haystack)
            for keyword in (page.get("selection") or {}).get("keywords") or []:
                keyword_text = str(keyword).lower()
                if keyword_text and keyword_text in normalized:
                    score += 8
                elif normalized and normalized in keyword_text:
                    score += 5
            for avoid in (page.get("selection") or {}).get("avoid_when") or []:
                avoid_text = str(avoid).lower()
                if avoid_text and avoid_text in normalized:
                    score -= 20
        else:
            score = 1
        if score > 0:
            ranked.append((score, -position, page))

    ranked.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [page for _score, _position, page in ranked[: max(1, limit)]]


def validate_catalog(template_dir: Path) -> list[str]:
    """Return all catalog/schema/filesystem consistency errors."""
    errors: list[str] = []
    try:
        catalog = load_catalog(template_dir)
    except CatalogError as exc:
        return [str(exc)]

    if catalog.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if not isinstance(catalog.get("template_id"), str) or not catalog.get("template_id"):
        errors.append("template_id is required")
    selection_contract_version = catalog.get("selection_contract_version", 1)
    if selection_contract_version not in (1, 2):
        errors.append("selection_contract_version must be 1 or 2")
    reference_format = catalog.get("reference_format")
    if selection_contract_version >= 2 and reference_format not in REFERENCE_FORMATS:
        errors.append(
            "reference_format must be <NNN>_<page_type>_<layout_id> or basename "
            "for selection contract v2"
        )
    policy = catalog.get("selection_policy")
    if not isinstance(policy, dict):
        errors.append("selection_policy must be an object")
    else:
        if not isinstance(policy.get("match_order"), list) or not policy.get("match_order"):
            errors.append("selection_policy.match_order must be a non-empty array")
        if policy.get("fallback") != "no-template-match":
            errors.append("selection_policy.fallback must be no-template-match")
    pages = catalog.get("pages")
    if not isinstance(pages, list):
        return errors + ["pages must be an array"]

    disk_files = {path.name for path in template_dir.glob("*.svg")}
    catalog_files: set[str] = set()
    references: set[str] = set()
    layout_ids: set[str] = set()
    aliases: set[str] = set()

    for index, page in enumerate(pages):
        prefix = f"pages[{index}]"
        if not isinstance(page, dict):
            errors.append(f"{prefix} must be an object")
            continue

        file_name = page.get("file")
        reference = page.get("reference")
        page_type = page.get("page_type")
        layout_id = page.get("layout_id")
        label = page.get("label")
        source_slide = page.get("source_slide")
        provenance = page.get("provenance")
        render_mode = page.get("render_mode")
        usage = page.get("usage", "output")

        provenance_kind = None
        if provenance is not None:
            if not isinstance(provenance, dict):
                errors.append(f"{prefix}.provenance must be an object")
            else:
                provenance_kind = provenance.get("kind")
                if provenance_kind not in PAGE_PROVENANCE_KINDS:
                    errors.append(f"{prefix}.provenance.kind is invalid")
                if provenance_kind == "adapted_component":
                    for key in ("source_template", "source_reference"):
                        value = provenance.get(key)
                        if not isinstance(value, str) or not value.strip():
                            errors.append(f"{prefix}.provenance.{key} is required")
                    if "source_slide" in page:
                        errors.append(f"{prefix}.source_slide is reserved for source mirror pages")
                    if render_mode not in {"brand_shell", "themed_rebuild"}:
                        errors.append(
                            f"{prefix}.render_mode must be brand_shell or themed_rebuild "
                            "for adapted components"
                        )
        if render_mode is not None and render_mode not in PAGE_RENDER_MODES:
            errors.append(f"{prefix}.render_mode is invalid")

        if not isinstance(file_name, str) or not file_name.endswith(".svg"):
            errors.append(f"{prefix}.file must be an .svg filename")
            continue
        if file_name in catalog_files:
            errors.append(f"duplicate catalog file: {file_name}")
        catalog_files.add(file_name)

        stem = file_name[:-4]
        if reference_format == "<NNN>_<page_type>_<layout_id>":
            match = SEMANTIC_STEM_RE.fullmatch(stem)
            if not match:
                errors.append(
                    f"{file_name} must match <NNN>_<page_type>_<layout_id>.svg"
                )
            else:
                if provenance_kind != "adapted_component" and (
                    not isinstance(source_slide, int)
                    or isinstance(source_slide, bool)
                    or source_slide != int(match.group("order"))
                ):
                    errors.append(f"{prefix}.source_slide must equal filename order")
                if page_type != match.group("page_type"):
                    errors.append(f"{prefix}.page_type does not match filename")
                if layout_id != match.group("layout_id"):
                    errors.append(f"{prefix}.layout_id does not match filename")
        elif provenance_kind != "adapted_component" and (
            not isinstance(source_slide, int)
            or isinstance(source_slide, bool)
            or source_slide < 1
        ):
            errors.append(f"{prefix}.source_slide must be a positive integer")

        if reference != stem:
            errors.append(f"{prefix}.reference must equal filename stem")
        if reference in references:
            errors.append(f"duplicate reference: {reference}")
        if isinstance(reference, str):
            references.add(reference)

        if not isinstance(layout_id, str) or not layout_id:
            errors.append(f"{prefix}.layout_id is required")
        elif layout_id in layout_ids:
            errors.append(f"duplicate layout_id: {layout_id}")
        else:
            layout_ids.add(layout_id)
        if page_type not in CANONICAL_PAGE_TYPES:
            errors.append(f"{prefix}.page_type is invalid: {page_type}")
        if usage not in PAGE_USAGES:
            errors.append(
                f"{prefix}.usage must be output or reference_only"
            )
        if not isinstance(label, str) or not label.strip():
            errors.append(f"{prefix}.label is required")

        page_aliases = page.get("aliases") or []
        if not isinstance(page_aliases, list):
            errors.append(f"{prefix}.aliases must be an array")
        else:
            for alias in page_aliases:
                if not isinstance(alias, str) or not alias:
                    errors.append(f"{prefix}.aliases contains an invalid value")
                    continue
                if alias.endswith(".svg"):
                    errors.append(f"alias must be a basename without .svg: {alias}")
                if alias in aliases or alias in references:
                    errors.append(f"duplicate or colliding alias: {alias}")
                aliases.add(alias)

        selection = page.get("selection")
        if not isinstance(selection, dict):
            errors.append(f"{prefix}.selection must be an object")
        else:
            if not isinstance(selection.get("structure"), str):
                errors.append(f"{prefix}.selection.structure is required")
            for key in ("content_slots", "use_cases", "keywords", "visuals"):
                value = selection.get(key)
                if not isinstance(value, list) or not value:
                    errors.append(f"{prefix}.selection.{key} must be an array")
                elif any(not isinstance(item, str) or not item.strip() for item in value):
                    errors.append(
                        f"{prefix}.selection.{key} entries must be non-empty strings"
                    )
            for key in ("avoid_when", "image_requirements"):
                value = selection.get(key)
                if value is None and selection_contract_version < 2:
                    continue
                if not isinstance(value, list) or not value:
                    errors.append(f"{prefix}.selection.{key} must be a non-empty array when present")
                elif any(not isinstance(item, str) or not item.strip() for item in value):
                    errors.append(
                        f"{prefix}.selection.{key} entries must be non-empty strings"
                    )
            for key in ("semantic_require_any", "semantic_exclude_any"):
                value = selection.get(key)
                if value is None:
                    continue
                if not isinstance(value, list) or not value:
                    errors.append(
                        f"{prefix}.selection.{key} must be a non-empty array when present"
                    )
                elif any(not isinstance(item, str) or not item.strip() for item in value):
                    errors.append(
                        f"{prefix}.selection.{key} entries must be non-empty strings"
                    )
            strict_item_count = selection.get("strict_item_count")
            if strict_item_count is not None and not isinstance(strict_item_count, bool):
                errors.append(
                    f"{prefix}.selection.strict_item_count must be boolean when present"
                )
            density = selection.get("content_density")
            if density not in CONTENT_DENSITIES:
                errors.append(
                    f"{prefix}.selection.content_density must be low, medium, or high"
                )
            variant_profile = selection.get("variant_profile")
            if variant_profile is not None:
                if not isinstance(variant_profile, dict):
                    errors.append(
                        f"{prefix}.selection.variant_profile must be an object"
                    )
                else:
                    for key in ("topology", "emphasis", "visual_weight"):
                        value = variant_profile.get(key)
                        if value is not None and (
                            not isinstance(value, str) or not value.strip()
                        ):
                            errors.append(
                                f"{prefix}.selection.variant_profile.{key} "
                                "must be a non-empty string when present"
                            )

    for collision in sorted(aliases & references):
        errors.append(f"alias collides with canonical reference: {collision}")

    missing = sorted(catalog_files - disk_files)
    orphan = sorted(disk_files - catalog_files)
    for file_name in missing:
        errors.append(f"catalog file missing on disk: {file_name}")
    for file_name in orphan:
        errors.append(f"SVG missing from page catalog: {file_name}")
    if (template_dir / CAPABILITY_FILE).exists():
        errors.extend(
            f"template capabilities: {error}"
            for error in validate_capabilities(template_dir)
        )
    return errors


def validate_project(project_dir: Path) -> list[str]:
    """Validate ``spec_lock.page_layouts`` before Executor starts."""
    errors: list[str] = []
    template_dir = project_dir / "templates"
    lock_path = project_dir / "spec_lock.md"
    if not template_dir.is_dir():
        return []
    if not lock_path.exists():
        return [f"missing spec_lock.md in {project_dir}"]

    catalog: dict[str, Any] | None = None
    catalog_path = template_dir / "page_catalog.json"
    if catalog_path.exists():
        errors.extend(validate_catalog(template_dir))
        try:
            catalog = load_catalog(template_dir)
        except CatalogError as exc:
            errors.append(str(exc))
    elif (template_dir / CAPABILITY_FILE).exists():
        errors.extend(
            f"template capabilities: {error}"
            for error in validate_capabilities(template_dir)
        )

    sections = parse_lock(lock_path)
    page_layouts = sections.get("page_layouts", {})
    if not page_layouts:
        return errors

    disk_references = {path.stem for path in template_dir.glob("*.svg")}
    for page_id, reference in page_layouts.items():
        if reference in disk_references:
            if catalog is not None:
                try:
                    page = resolve_reference(catalog, reference)
                except CatalogError as exc:
                    errors.append(f"page_layouts {page_id}: {exc}")
                else:
                    if page.get("reference") != reference:
                        errors.append(
                            f"page_layouts {page_id}: use canonical reference "
                            f"{page.get('reference')!r}, not alias {reference!r}"
                        )
            continue

        if catalog is not None:
            try:
                page = resolve_reference(catalog, reference)
            except CatalogError:
                page = None
            if page is not None:
                errors.append(
                    f"page_layouts {page_id}: {reference!r} is an alias; replace it "
                    f"with canonical reference {page.get('reference')!r}"
                )
                continue
        errors.append(
            f"page_layouts {page_id}: missing template SVG {reference}.svg"
        )
    return errors


def _compact_result(page: dict[str, Any], *, slim: bool = False) -> dict[str, Any]:
    result = {
        "reference": page.get("reference"),
        "file": page.get("file"),
        "page_type": page.get("page_type"),
        "layout_id": page.get("layout_id"),
        "label": page.get("label"),
        "usage": page.get("usage", "output"),
    }
    selection = page.get("selection") or {}
    variant_profile = infer_variant_profile(
        str(page.get("file") or page.get("reference") or ""),
        selection=selection,
    )
    if slim:
        result["selection"] = {
            key: selection.get(key)
            for key in (
                "content_forms",
                "item_count",
                "content_density",
                "structure",
                "image_requirements",
            )
            if selection.get(key) is not None
        }
        result["selection"]["variant_profile"] = variant_profile
    else:
        result["selection"] = {**selection, "variant_profile": variant_profile}
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("validate")
    subparsers.add_parser("validate-project")
    resolve_parser = subparsers.add_parser("resolve")
    resolve_parser.add_argument("reference")
    resolve_parser.add_argument("--compact", action="store_true")
    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("query")
    search_parser.add_argument("--page-type", choices=sorted(CANONICAL_PAGE_TYPES))
    search_parser.add_argument("--content-form")
    search_parser.add_argument("--item-count", type=int)
    search_parser.add_argument(
        "--image-need", choices=("none", "optional", "required"),
    )
    search_parser.add_argument(
        "--precise-only", action="store_true",
        help="Exclude local pages supported only by a broad content-form tag.",
    )
    search_parser.add_argument(
        "--density",
        choices=sorted(CONTENT_DENSITIES),
    )
    search_parser.add_argument(
        "--topology",
        type=normalize_topology,
        help="Generic composition topology, for example split/radial/grid/sequence.",
    )
    search_parser.add_argument(
        "--emphasis",
        type=normalize_emphasis,
        help="Generic emphasis, for example center/balanced/directional.",
    )
    search_parser.add_argument("--limit", type=int, default=5)
    search_parser.add_argument("--compact", action="store_true")
    search_parser.add_argument("--include-reference", action="store_true")
    args = parser.parse_args()

    if args.command == "validate":
        errors = validate_catalog(args.path)
        if errors:
            for error in errors:
                print(f"[ERROR] {error}")
            return 1
        catalog = load_catalog(args.path)
        print(f"[OK] {len(catalog.get('pages', []))} catalog pages validated")
        return 0

    if args.command == "validate-project":
        errors = validate_project(args.path)
        if errors:
            for error in errors:
                print(f"[ERROR] {error}")
            return 1
        print(f"[OK] project template mappings validated: {args.path}")
        return 0

    try:
        catalog = load_catalog(args.path)
        if args.command == "resolve":
            print(json.dumps(
                _compact_result(
                    resolve_reference(catalog, args.reference),
                    slim=args.compact,
                ),
                ensure_ascii=False,
                indent=2,
            ))
        else:
            matches = search_catalog(
                catalog,
                args.query,
                page_type=args.page_type,
                content_form=args.content_form,
                item_count=args.item_count,
                density=args.density,
                topology=args.topology,
                emphasis=args.emphasis,
                image_need=args.image_need,
                precise_only=args.precise_only,
                limit=args.limit,
                include_reference=args.include_reference,
            )
            print(json.dumps(
                [_compact_result(page, slim=args.compact) for page in matches],
                ensure_ascii=False,
                indent=2,
            ))
    except CatalogError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
