#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const [imagePath, placeholder = ""] = process.argv.slice(2);

if (!imagePath) {
  console.error("Usage: node scripts/weixin-image-clipboard-js.mjs <image-path> [placeholder-text]");
  process.exit(2);
}

const absImagePath = path.resolve(imagePath);
const image = fs.readFileSync(absImagePath);
const ext = path.extname(absImagePath).toLowerCase();
const mimeByExt = {
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
  ".gif": "image/gif",
};
const mime = mimeByExt[ext] || "image/png";
const imageB64 = image.toString("base64");
const placeholderB64 = Buffer.from(placeholder, "utf8").toString("base64");

const js = `(async () => {
  const decodeText = (b64) => {
    const binary = atob(b64);
    const bytes = Uint8Array.from(binary, (char) => char.charCodeAt(0));
    return new TextDecoder().decode(bytes);
  };
  const decodeBytes = (b64) => {
    const binary = atob(b64);
    return Uint8Array.from(binary, (char) => char.charCodeAt(0));
  };
  const placeholder = decodeText("${placeholderB64}");
  const bytes = decodeBytes("${imageB64}");
  const mime = "${mime}";

  const candidates = [
    ...document.querySelectorAll(".ProseMirror, [contenteditable=true], [role='textbox']")
  ].filter((el) => {
    const rect = el.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0;
  });
  const editor =
    (placeholder && candidates.find((el) => (el.innerText || "").includes(placeholder))) ||
    candidates.find((el) => (el.innerText || "").includes("从这里开始写正文")) ||
    candidates[candidates.length - 1] ||
    document.querySelector(".ProseMirror") ||
    document.querySelector("[contenteditable=true]") ||
    document.querySelector('[role="textbox"]');

  if (!editor) {
    return { ok: false, reason: "missing_editor" };
  }

  editor.focus();
  let placeholderMatched = false;
  if (placeholder) {
    const walker = document.createTreeWalker(editor, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      const offset = node.nodeValue.indexOf(placeholder);
      if (offset >= 0) {
        const range = document.createRange();
        range.setStart(node, offset);
        range.setEnd(node, offset + placeholder.length);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        placeholderMatched = true;
        break;
      }
    }
  }

  if (!navigator.clipboard || !window.ClipboardItem) {
    return { ok: false, reason: "clipboard_api_unavailable", placeholderMatched };
  }

  const blob = new Blob([bytes], { type: mime });
  const item = new ClipboardItem({ [mime]: blob });
  const timeout = new Promise((resolve) => {
    setTimeout(() => resolve({ ok: false, reason: "clipboard_write_timeout" }), 3500);
  });
  const write = navigator.clipboard.write([item]).then(
    () => ({ ok: true }),
    (error) => ({ ok: false, reason: error && (error.name || error.message) || "clipboard_write_failed" })
  );
  const result = await Promise.race([write, timeout]);
  return {
    ...result,
    mime,
    bytes: bytes.length,
    placeholder,
    placeholderMatched,
    editorTextLength: (editor.innerText || "").length,
  };
})()`;

process.stdout.write(js);
