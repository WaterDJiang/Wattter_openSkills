// 检查留档示例的真实内联模型和 DOM 读数，不是通用 Skill 质量评分。
const fs = require("node:fs");
const vm = require("node:vm");
const assert = require("node:assert/strict");
const html = fs.readFileSync(`${__dirname}/cache-demo.html`, "utf8");
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const elements = {};
for (const [, id] of html.matchAll(/id="([^"]+)"/g)) {
  elements[id] = {textContent:"", addEventListener(event, fn) { this[event] = fn; }};
}
const context = vm.createContext({document:{getElementById(id) {
  assert.ok(elements[id], `页面中缺少 ${id}`);
  return elements[id];
}}});
vm.runInContext(script, context);
const click = id => elements[id].click();
const text = id => elements[id].textContent;
const model = () => JSON.parse(vm.runInContext("JSON.stringify(state)", context));
assert.equal(text("status"), "空缓存");
click("request");
assert.equal(model().version, 1);
assert.equal(model().written, 0);
click("advance");
click("request");
assert.equal(model().version, 1);
assert.equal(model().written, 0, "命中不得续期");
assert.match(text("expiry"), /到期：60 秒 · 剩余 30 秒/);
click("advance");
assert.equal(text("status"), "已到期", "恰好 60 秒应失效");
assert.equal(model().version, 1, "时间推进不得自动请求");
click("request");
assert.equal(model().version, 2);
assert.equal(model().written, 60);
assert.match(text("expiry"), /到期：120 秒 · 剩余 60 秒/);
click("request");
assert.equal(model().version, 2, "连续命中不应重新写入");
click("reset");
assert.equal(text("clock"), "0 秒");
assert.equal(text("status"), "空缓存");
assert.equal(model().version, 0);
console.log("PASS: 首次访问、命中不续期、到期边界、延迟重建、重复请求、重置及 DOM 读数");
