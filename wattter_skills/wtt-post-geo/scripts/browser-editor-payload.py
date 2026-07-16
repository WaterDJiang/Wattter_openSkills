#!/usr/bin/env python3
"""Build a self-contained, verifiable browser-editor write script."""

from __future__ import annotations

import argparse
import base64
import json
import sys
from html.parser import HTMLParser
from pathlib import Path


ENGINES = ("codemirror5", "iframe-html", "textarea", "contenteditable-text")


def fnv1a(text: str) -> str:
    value = 2166136261
    for char in text:
        value ^= ord(char)
        value = (value * 16777619) & 0xFFFFFFFF
    return f"{value:08x}"


def squash_whitespace(text: str) -> str:
    return "".join(char for char in text if not char.isspace())


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.hidden_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"script", "style", "template"}:
            self.hidden_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "template"} and self.hidden_depth:
            self.hidden_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.hidden_depth:
            self.parts.append(data)

    def text(self) -> str:
        return "".join(self.parts)


def html_visible_text(value: str) -> str:
    parser = VisibleTextParser()
    parser.feed(value)
    parser.close()
    return parser.text()


def encode(value: str) -> str:
    return base64.b64encode(value.encode("utf-8")).decode("ascii")


def build_script(source: str, engine: str, selector: str) -> tuple[str, dict[str, object]]:
    is_html = engine == "iframe-html"
    expected = html_visible_text(source) if is_html else source
    basis = "visible_text_without_whitespace" if is_html else "exact_text"
    expected_for_hash = squash_whitespace(expected) if is_html else expected

    source_b64 = encode(source)
    expected_b64 = encode(expected)
    engine_json = json.dumps(engine, ensure_ascii=False)
    selector_json = json.dumps(selector, ensure_ascii=False)

    script = f"""(() => {{
  const engine = {engine_json};
  const selector = {selector_json};
  const decode = (value) => new TextDecoder().decode(Uint8Array.from(atob(value), c => c.charCodeAt(0)));
  const source = decode('{source_b64}');
  const expected = decode('{expected_b64}');
  const squash = (value) => Array.from(value || '').filter(c => !/\\s/u.test(c)).join('');
  const hash = (value) => {{
    let result = 2166136261;
    for (const char of value || '') {{
      result ^= char.codePointAt(0);
      result = Math.imul(result, 16777619);
    }}
    return (result >>> 0).toString(16).padStart(8, '0');
  }};
  const dispatch = (element) => {{
    try {{ element.dispatchEvent(new InputEvent('input', {{ bubbles: true, inputType: 'insertText', data: null }})); }}
    catch {{ element.dispatchEvent(new Event('input', {{ bubbles: true }})); }}
    element.dispatchEvent(new Event('change', {{ bubbles: true }}));
  }};

  let actual = '';
  if (engine === 'codemirror5') {{
    const root = document.querySelector(selector);
    const cm = root?.CodeMirror || root?.closest?.('.CodeMirror')?.CodeMirror;
    if (!cm?.setValue || !cm?.getValue) return {{ written: false, engine, selector, reason: 'codemirror_not_found' }};
    cm.setValue(source);
    actual = cm.getValue();
  }} else if (engine === 'iframe-html') {{
    const frame = document.querySelector(selector);
    const body = frame?.contentDocument?.body;
    if (!body) return {{ written: false, engine, selector, reason: 'iframe_body_not_found' }};
    body.innerHTML = source;
    dispatch(body);
    actual = body.innerText || body.textContent || '';
  }} else if (engine === 'textarea') {{
    const element = document.querySelector(selector);
    if (!element) return {{ written: false, engine, selector, reason: 'textarea_not_found' }};
    const prototype = element instanceof HTMLTextAreaElement ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
    const setter = Object.getOwnPropertyDescriptor(prototype, 'value')?.set;
    setter ? setter.call(element, source) : (element.value = source);
    dispatch(element);
    actual = element.value || '';
  }} else if (engine === 'contenteditable-text') {{
    const element = document.querySelector(selector);
    if (!element) return {{ written: false, engine, selector, reason: 'contenteditable_not_found' }};
    element.focus();
    element.textContent = source;
    dispatch(element);
    actual = element.innerText || element.textContent || '';
  }} else {{
    return {{ written: false, engine, selector, reason: 'unsupported_engine' }};
  }}

  const expectedComparable = engine === 'iframe-html' ? squash(expected) : expected;
  const actualComparable = engine === 'iframe-html' ? squash(actual) : actual;
  return {{
    written: true,
    engine,
    selector,
    verificationBasis: engine === 'iframe-html' ? 'visible_text_without_whitespace' : 'exact_text',
    sourceLength: source.length,
    expectedLength: expectedComparable.length,
    actualLength: actualComparable.length,
    expectedHash: hash(expectedComparable),
    actualHash: hash(actualComparable),
    matches: expectedComparable.length === actualComparable.length && hash(expectedComparable) === hash(actualComparable),
    start: actual.slice(0, 80),
    end: actual.slice(-120)
  }};
}})()"""

    manifest: dict[str, object] = {
        "engine": engine,
        "selector": selector,
        "verification_basis": basis,
        "source_length": len(source),
        "source_hash": fnv1a(source),
        "expected_length": len(expected_for_hash),
        "expected_hash": fnv1a(expected_for_hash),
    }
    return script, manifest


def main() -> int:
    parser = argparse.ArgumentParser(
        description="为 OpenCLI browser eval 生成可校验的编辑器写入脚本"
    )
    parser.add_argument("source", type=Path, help="独立正文文件")
    parser.add_argument("--engine", choices=ENGINES, required=True)
    parser.add_argument("--selector", required=True, help="编辑器根节点或 iframe CSS selector")
    parser.add_argument("--output-js", type=Path, required=True, help="生成的自包含 JS 文件")
    args = parser.parse_args()

    try:
        if not args.source.is_file():
            raise ValueError(f"源文件不存在：{args.source}")
        source = args.source.read_text(encoding="utf-8-sig")
        if not source:
            raise ValueError("源文件不能为空")
        script, manifest = build_script(source, args.engine, args.selector)
        args.output_js.parent.mkdir(parents=True, exist_ok=True)
        args.output_js.write_text(script + "\n", encoding="utf-8")
        manifest.update(
            {
                "source": str(args.source.resolve()),
                "output_js": str(args.output_js.resolve()),
            }
        )
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"browser-editor-payload: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
