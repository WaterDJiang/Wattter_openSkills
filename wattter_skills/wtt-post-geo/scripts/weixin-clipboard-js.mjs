#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const [htmlPath, plainPath] = process.argv.slice(2);

if (!htmlPath) {
  console.error("Usage: node scripts/weixin-clipboard-js.mjs <article.html> [article.txt]");
  process.exit(2);
}

const absHtmlPath = path.resolve(htmlPath);
const html = fs.readFileSync(absHtmlPath, "utf8");
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

const js = `(async () => {
  const decode = (b64) => {
    const binary = atob(b64);
    const bytes = Uint8Array.from(binary, (char) => char.charCodeAt(0));
    return new TextDecoder().decode(bytes);
  };
  if (!navigator.clipboard || !window.ClipboardItem) {
    return { ok: false, error: "Clipboard API unavailable" };
  }
  const html = decode("${htmlB64}");
  const plain = decode("${plainB64}");
  const item = new ClipboardItem({
    "text/html": new Blob([html], { type: "text/html" }),
    "text/plain": new Blob([plain], { type: "text/plain" })
  });
  await navigator.clipboard.write([item]);
  return { ok: true, htmlLength: html.length, plainLength: plain.length };
})()`;

process.stdout.write(js);
