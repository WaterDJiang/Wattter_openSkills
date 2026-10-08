# 素材审阅与版本锁定

只有一套审阅机制，没有素材管理档位，也不增加开场模式选择。首次制作可自主检索、下载、选择；已有锁后，只对真实素材或导流变化审阅。用户明确指定本次替换对象与目标即为授权，仍展示 diff，不重复询问。其他未授权变化先展示 diff，等待确认；“继续制作”不等于授权任意替换。

## 首次制作

先完成选材、配音和本地化，填写项目 `assets.json`，再锁定。自制素材 `sourceUrl` 可为 null，许可写实际授权范围；来源不明不得编造许可证，标为“待核实”并说明依据，发布前处理使用权。哈希由脚本计算，不接受填写的 SHA256 作为基准。

```json
{
  "schema": "code-animation-assets/v1",
  "assets": [{
    "id": "brand-logo",
    "path": "media/logo.svg",
    "sourceUrl": "https://example.org/logo.svg",
    "license": "CC0-1.0",
    "useBasis": "用作片尾项目标识；已核对原页面授权",
    "landingUrl": "https://example.org/project"
  }],
  "links": [{"id": "project-home", "url": "https://example.org/project", "purpose": "片尾网页入口"}]
}
```

图片、字体、音效、旁白、配乐、下载的第三方库和许可证文件均逐项登记。生成旁白的 `.wav.json` 旁车也登记，避免文字/音色依据变化未纳入审阅。`path` 为项目内真实文件相对路径，不允许软链、越界或控制文件路径。无外部素材的纯代码片也使用空的 assets/links 数组。

自编的 HTML/JS/CSS 属实现代码，不作为素材登记；外部库放 `vendor/` 登记，不挪入 `code/` 绕过校验。程序生成的即时图形属于代码；固定图像或声音文件属于素材。私有模型/参考录音继续由声音配置管理，不复制到公开素材历史；最终用于影片的音频属于锁定素材。

```sh
python3 tools/asset_review.py seal .
python3 tools/asset_review.py check .
python3 tools/pipeline.py timeline . --lock
python3 tools/pipeline.py mix .
node tools/render.cjs . --preview
node tools/render.cjs . --render
python3 tools/pipeline.py finish .
```

`seal` 创建 v0001，保存每个素材的 ID、路径、出处、许可、使用依据、SHA256、导流 URL。只执行一次；再次 seal、丢失锁后重建均拒绝。先前生成了估时时间轴或旧作品产物时，首次纳管须使用 `seal . --migration-note '已逐项核对现有素材与出处；首次纳管依据……'`。这不是修改已有锁的入口。不要在尚未完成首次选材/声音时过早锁定后再直接补文件。

## 重跑与代码修改

每次执行先 `check .`；未变直接继续，不提问、不生成新版。锁时、混音、预览、渲染、合成和验收都内置校验，不能跳过 check 命令来绕过。仅场景代码变化不触发素材授权，仍须重渲染/合成并检查代码指纹。

网页所有外链登记在 links 或对应素材 landingUrl；模板可用 `window.assetLink('project-home')` 获取目标。更换声明里的 URL 会产生旧值/新值 diff。静态 href/action/location/window.open 和浏览器每个检查帧可见的链接/表单也核对；动态发现的未登记外链先留候选 diff 再阻断。复杂点击处理、二维码及绘入画面的链接须执行者登记并人工核对，当前工具不证明覆盖所有 JavaScript 行为或识别二维码。禁止以将导流藏入代码替代登记。

浏览器只读取锁定的本地媒体；阻断远程素材请求、候选目录访问与未登记资源。素材变动或删除先生成候选副本、Markdown/JSON diff 并失败退出，不能生成本次通过报告。旧 `delivery-check.json` 是旧版本历史结果；只有重新运行 validate 成功且版本一致才是本次验收通过。

## 提议更换：只写候选目录

锁定后新下载、重新配音、编辑固定素材都在 `.asset-review/candidates/<批次>/` 完成。不要直接改当前 assets.json 或覆盖 media/audio。复制当前声明为候选 proposal.json，保留全部未变条目；替换条目增加 candidatePath。新增条目使用新 ID，删除则从候选声明移除；改变来源/许可/导流只改候选声明字段。

```json
{
  "id": "brand-logo",
  "path": "media/logo.svg",
  "candidatePath": ".asset-review/candidates/logo-update/logo.svg",
  "sourceUrl": "https://example.org/new-logo.svg",
  "license": "CC0-1.0",
  "useBasis": "采用用户明确指定的新版标识",
  "landingUrl": "https://example.org/project"
}
```

以上是 proposal.json 中单条素材示例，完整文件仍有 schema、assets、links。元数据变更可省略 candidatePath，沿用当前字节。新配音可用 `voice.py synthesize --text-file 文案文件 --out .asset-review/candidates/批次/voice.wav`；音频与生成的旁车一起列入提议。锁后项目批量配音不得直接写当前 audio，脚本会拒绝；先走候选输出。

```sh
python3 tools/asset_review.py propose . \
  --proposal .asset-review/candidates/logo-update/proposal.json \
  --reason '替换为用户指定新版标识' --impact '片尾标识变化，重渲染并验收'
```

输出候选 ID、reviewSha256、变更项列表，并展示“变更项 / 旧值 / 新值 / 原因 / 影响”。proposal 不改当前素材或锁；候选只是一项建议，不能作为新版验收。自动检测的 diff 不知道业务原因，会明确写待说明；正式提交前用 propose 补齐实际原因和影响。

## 授权并提交

向用户展示实际 diff；获得确认后才记录授权。若用户已明确说“把 brand-logo 换成这份新版 SVG”，可直接记录该原始指令，不再询问。执行者不得自行编造确认。授权文件使用刚输出的 reviewSha256 和**完整**变更键：

```json
{
  "kind": "explicit-request",
  "statement": "用户本次原始指令：将 brand-logo 替换为已提供的新版 SVG",
  "reviewSha256": "填入 propose 返回的实际哈希",
  "changes": ["assets.brand-logo.sha256", "assets.brand-logo.sourceUrl", "assets.brand-logo.useBasis"]
}
```

事后确认使用 `kind: confirmed`，statement 保存实际确认内容；上例 changes 仅为示例，必须使用实际 diff 的所有键。授权记录放候选目录，不作为当前素材。

```sh
python3 tools/asset_review.py accept . --candidate review-实际候选ID \
  --authorization .asset-review/candidates/logo-update/authorization.json
python3 tools/pipeline.py timeline . --lock
python3 tools/pipeline.py mix .
node tools/render.cjs . --preview
node tools/render.cjs . --render
python3 tools/pipeline.py finish .
```

accept 再次输出 diff，核对候选哈希、授权范围、当前基准、文件内容和未纳入的工作区变化；通过才保存 v0002、新文件、新声明和锚点。旧素材及旧清单不删除，移除当前素材也保留历史。候选确认后又变化、重复使用旧授权、覆盖已有未纳管文件均拒绝。

新版清单不等于新版成片验收。时间轴、混音、渲染报告、合成回执和最终验收均绑定素材版本/哈希；提交新版会使旧管线产物失效，必须完成上面的受影响流程。当前实现重建全片，不宣称增量渲染。

## 历史、迁移与边界

- `.asset-review/versions/v0001/` 保存 manifest.json、原素材 files/、diff.json/md、authorization.json、commit.json；后续版本有父清单哈希。current.json 与 film.json 的 assetReview 双重记录当前版本。
- candidates/ 为追加候选。不能用同名重下、覆盖哈希报告、删锁/重建清单改变基准。没有 reset/force/reseal 开关；历史文件、清单、授权摘要或版本链损坏会阻断。
- 发生中断时 transaction.json 留存并阻断。保留整项目证据，从已验证的完整备份恢复该事务前一致状态，核对历史后重新提议；不要只删 transaction.json 或重新 seal。当前不提供自动事务恢复命令。
- 升级旧工程先完整备份，更新四个 tools 脚本；补 assets.json（及所需 assetLink helper），核对原素材后首次 seal。不要只替换 render.cjs 而遗漏 Python 门禁。旧作品不会自动升级或自动重渲染。
- 分享/备份时保留完整素材历史才可复跑；历史中可能有有许可限制的素材或个人声音，分享前核对范围。公开 Skill 模板不包含任何人的录音或项目素材。
- 此机制防止管线误操作、未授权候选提交和报告覆盖造成的误验收；它不是不可篡改存储，也不能验证一段授权文字是否真来自用户。具备任意文件/代码写权限者仍能改程序，不能声称密码学意义的防篡改或授权认证。
