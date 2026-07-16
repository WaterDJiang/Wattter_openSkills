# 博客园草稿流程

> 仅在用户明确点名「博客园 / cnblogs」或要求「全平台」时加载。

## 当前能力基线（2026-07-16）

- OpenCLI `1.8.6` 内置注册表没有博客园 adapter；本 skill 随附 `cnblogs article-draft`。
- adapter 使用 OpenCLI 已有登录 Cookie 和 XSRF token 创建 Markdown 草稿，不需要 CSDN 插件。
- 当前 adapter 支持摘要和标签，不上传本地图片，标记 `experimental`。
- 默认创建 Markdown 草稿，不自动公开发布或投递首页候选。

## 内容 payload

```yaml
title: 博客园文章标题
body: 独立 Markdown 正文
summary: 可选摘要
media:
  images: []
  videos: []
  posters: []
tags: []
render_mode: markdown
mode: draft|fill_and_confirm|format_only
platform_options:
  access_permission: public
  allow_comments: true
  display_on_home_page: false
  include_in_main_syndication: false
execution:
  fallback_chain: [opencli_login_adapter, opencli_ui, manual_confirm]
  write_state: not_started
```

适配要求：

- 标题与正文分离，剥掉同名 H1。
- 保留 Markdown 层级、代码块、表格、引用和链接；删除 CSDN 编辑器控件、iframe、注释和不可复用脚本。
- `display_on_home_page`、首页候选、站点分类、团队、可见性和评论设置属于平台专属选项，不自动开启。
- 本地图片必须转存到博客园图床或由用户在编辑器中上传；正文不能保留本地绝对路径、`file://` 或临时目录。
- 视频自动化未验证，默认人工处理。

## 分层 Provider 路由

### 主路径：OpenCLI 登录态 adapter

按 [login-state-adapters.md](login-state-adapters.md) 执行：

1. 预检 `cnblogs/article-draft`、OpenCLI 桥接和图片能力。
2. 传入独立 Markdown、标题、摘要和标签。
3. 记录 adapter 返回的 `draft_id/draft_url`，先记为 `created_unverified`。
4. 打开博客园编辑链接，核对标题、正文首尾、代码块、关键链接、摘要/标签和图片。
5. 验证通过后设置 `created_verified`。

草稿已存在但图片或格式异常时，修复原草稿，不创建第二份。

### 回退：OpenCLI 浏览器编辑器

```bash
opencli doctor
opencli browser cnblogs open https://i.cnblogs.com/posts/edit --window foreground
opencli browser cnblogs state
opencli browser cnblogs find --css 'input,textarea,[contenteditable=true],button,input[type=file]' --limit 100 --text-max 100
```

- 页面出现 `cnb-no-blog` 或「您的账号未开通博客」时，直接设为 `blocked/confirmed_not_created`，报告 `未完成：账号未开通博客`；不要继续找编辑器或重复调用 adapter。
- 页面未登录时停止，让用户完成登录。
- 识别当前 Markdown 编辑器和保存草稿控件，不按固定序号操作。
- 写入标题和正文后，回读开头、结尾、代码块和链接；多段 Markdown 结构损坏时停在 `fill_and_confirm`。
- 图片上传后必须确认正文得到博客园托管 URL。
- 默认保存草稿；不要自动勾选首页、候选区、团队或公开发布选项。

## 校验与回报

- 草稿后台/编辑 URL 存在且内容匹配：`已创建草稿`。
- 已填编辑器但保存、图片或选项未确认：`已填写待确认`。
- 登录、XSRF、上传、保存或回读失败：`未完成`。
- 账号未开通博客：`未完成`，链接可给申请页，但不能把申请页当草稿链接。
- 状态未知时先对账，不进入下一 provider。
