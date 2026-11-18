# WeChat Platform / 微信公众号平台

微信平台目录用于通过微信公众号草稿箱 API 把 Markdown 内容发布到公众号后台，适合已经具备公众号配置、白名单和素材管理能力的场景。

## 核心能力

- 使用统一配置中心中的 `wechat` 节点和 `config.py` 管理公众号凭证
- 通过微信草稿箱 API 发布文章
- 支持标题、作者、摘要自动提取
- 支持海报标记、海报生成和素材上传
- 保留微信公众号专用样式与模板资源

## 环境要求

- Python 3.8+
- 微信公众号 `appid` 与 `appsecret`
- 调用服务器 IP 已加入微信公众平台白名单

## 安装

```bash
cd skills/wtt-post-multi-platform
pip install -r requirements.txt
playwright install chromium
```

## 配置

1. 编辑根目录的 `config/config.json`
2. 填入 `wechat.appid` 和 `wechat.appsecret`
3. 根据需要填写 `wechat.thumb_media_id`

## 使用

统一入口：

```bash
python scripts/post.py --platform wechat -m /path/to/article.md
```

带海报参数：

```bash
python scripts/post.py --platform wechat -m /path/to/article.md --enable-posters
```

直接调用平台脚本：

```bash
python platforms/wechat/scripts/wechat_draft_poster.py -m /path/to/article.md
```

## 平台资源

- API 文档：`references/api_docs.md`
- 海报模板：`templates/poster-templates.html`
- 模板说明：`templates/README.md`

## 说明

- 微信平台采用“统一配置中心 + token + API”链路，不依赖浏览器自动化登录
- 发布逻辑保持在 `platforms/wechat/` 内，避免和其他平台耦合
