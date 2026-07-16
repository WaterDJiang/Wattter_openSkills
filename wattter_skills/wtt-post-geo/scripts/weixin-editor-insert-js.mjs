#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const [htmlPath, plainPath] = process.argv.slice(2);

if (!htmlPath) {
  console.error("Usage: node scripts/weixin-editor-insert-js.mjs <article.html> [article.txt]");
  process.exit(2);
}

const html = fs.readFileSync(path.resolve(htmlPath), "utf8");
const plain = plainPath
  ? fs.readFileSync(path.resolve(plainPath), "utf8")
  : html
      .replace(/<style[\s\S]*?<\/style>/gi, "")
      .replace(/<script[\s\S]*?<\/script>/gi, "")
      .replace(/<[^>]+>/g, " ")
      .replace(/\s+/g, " ")
      .trim();

const htmlB64 = Buffer.from(html, "utf8").toString("base64");
const plainB64 = Buffer.from(plain, "utf8").toString("base64");

const js = `(() => {
  const decode = (b64) => {
    const binary = atob(b64);
    const bytes = Uint8Array.from(binary, (char) => char.charCodeAt(0));
    return new TextDecoder().decode(bytes);
  };
  const html = decode("${htmlB64}");
  const plain = decode("${plainB64}");
  const editorCandidates = [
    ...document.querySelectorAll(".ProseMirror, [contenteditable=true], [role='textbox']")
  ].filter((el) => {
    const rect = el.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0;
  });
  const editor =
    editorCandidates.find((el) => (el.innerText || "").includes("从这里开始写正文")) ||
    editorCandidates[editorCandidates.length - 1] ||
    document.querySelector(".ProseMirror") ||
    document.querySelector("[contenteditable=true]") ||
    document.querySelector('[role="textbox"]');
  if (!editor) {
    return { ok: false, reason: "missing_editor" };
  }

  editor.focus();
  const selection = window.getSelection();
  const range = document.createRange();
  range.selectNodeContents(editor);
  range.deleteContents();
  selection.removeAllRanges();
  selection.addRange(range);

  let insertedByCommand = false;
  try {
    insertedByCommand = document.execCommand("insertHTML", false, html);
  } catch (error) {
    insertedByCommand = false;
  }

  if (!insertedByCommand || editor.innerText.trim().length < Math.min(120, plain.length / 3)) {
    editor.innerHTML = html;
  }

  editor.dispatchEvent(new InputEvent("input", {
    bubbles: true,
    inputType: "insertFromPaste",
    data: plain.slice(0, 1000)
  }));
  editor.dispatchEvent(new Event("change", { bubbles: true }));

  const text = editor.innerText || "";
  return {
    ok: text.trim().length > 0,
    insertedByCommand,
    textLength: text.trim().length,
    h2Count: editor.querySelectorAll("h2").length,
    h3Count: editor.querySelectorAll("h3").length,
    blockquoteCount: editor.querySelectorAll("blockquote").length,
    imgCount: editor.querySelectorAll("img").length,
    placeholderCount: (text.match(/【图\\s*\\d+：/g) || []).length,
    markdownLeak: /(^|\\n)#{1,6}\\s|\\*\\*/.test(text) || text.includes("\\x60\\x60\\x60")
  };
})()`;

process.stdout.write(js);
