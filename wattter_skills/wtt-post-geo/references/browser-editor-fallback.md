# 浏览器编辑器可靠写入

> 平台没有写 adapter、文件上传返回 `Not allowed`、或编辑器 `fill` 结果不可信时加载。

## 原则

- 编辑器写入和保存/发布分成两个动作。脚本只写正文，不点击保存或发布。
- `fill.verified: false` 不等于没有写入。先读取编辑器内部值，再决定是否回退。
- 禁止在未清空、未回读的编辑器上连续执行 `fill`、`type`、JS 注入；这会造成重复正文。
- 写入后比较长度和指纹；保存后重载同一草稿 URL，再比较一次。
- 页面控件漂移时重新 `state/find`，保存按钮使用 role/name/testid 等语义定位，不用历史数字 ref。

## 通用写入器

先把平台独立正文保存成文件，再生成自包含 JS：

```bash
python3 scripts/browser-editor-payload.py /abs/body.md \
  --engine codemirror5 \
  --selector '.CodeMirror' \
  --output-js /abs/browser-write.js

opencli browser <session> eval "$(</abs/browser-write.js)"
```

支持的 engine：

| engine | 用途 | 校验 |
|---|---|---|
| `codemirror5` | 掘金等 CodeMirror 5 编辑器 | `getValue()` 精确长度与指纹 |
| `iframe-html` | 百家号 UEditor iframe | 可见文本去空白后的长度与指纹 |
| `textarea` | 原生 textarea/input | 原生 value setter 后精确校验 |
| `contenteditable-text` | CSDN `pre[contenteditable]` 等纯文本编辑器 | `innerText/textContent` 精确校验 |

返回 `matches: true` 只证明当前编辑器值一致，不证明已经保存。`matches: false` 时不要追加写入；先回读实际正文、清空错误内容，再重新执行一次。

## CodeMirror 5

`opencli browser fill` 可能把正文写进 CodeMirror，却因为隐藏 textarea 的 `value` 为空而返回 `verified: false`。处理顺序：

1. 读取 `document.querySelector('.CodeMirror')?.CodeMirror?.getValue()`。
2. 已经匹配则停止写入，等待自动保存。
3. 不匹配则用通用写入器的 `codemirror5` 一次性 `setValue()`；它会覆盖旧值，不追加。
4. 保存后重载同一 `/drafts/<id>`，再次比较长度与指纹。

不得在 `fill` 后直接调用 `type`。真实测试中这会把全文重复 2～3 次。

## iframe HTML

百家号正文位于 `#ueditor_0` 的同源 iframe。使用清洗后的 HTML fragment：

```bash
python3 scripts/browser-editor-payload.py /abs/article.html \
  --engine iframe-html \
  --selector '#ueditor_0' \
  --output-js /abs/baijiahao-write.js
```

写入器会设置 iframe `body.innerHTML` 并触发 `input/change`。保存时使用明确语义：

```bash
opencli browser baijiahao click --role button --name '存草稿'
```

保存成功后 URL 应含 `article_id=<id>`；重载该 URL，再检查标题、正文首尾和中段关键句。

## contenteditable 探测

CSDN 多段 Markdown 可以对 `pre[contenteditable=true]` 做一次受控探测：

```bash
python3 scripts/browser-editor-payload.py /abs/article.csdn.md \
  --engine contenteditable-text \
  --selector 'pre[contenteditable=true]' \
  --output-js /abs/csdn-write.js
```

只有同时满足以下条件才继续保存/发布：

- 写入器返回 `matches: true`。
- 编辑器预览仍保留段落、标题、列表、引用和代码块。
- 等待自动保存后回读内容仍匹配。

任一条件失败时清空错误内容，切换人工导入，不再重复注入。

## 未知状态

浏览器点击后未跳转、命令超时或页面断连时：

1. 不再次点击。
2. 记录当前 URL、标题指纹、执行时间和可能的草稿 ID。
3. 查草稿/帖子列表。
4. 找到同标题写入但正文无法核对时，报告 `已填写待确认`。
5. 明确不存在新写入时，才允许下一个 provider。
