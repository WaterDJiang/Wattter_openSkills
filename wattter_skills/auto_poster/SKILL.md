---
name: auto-poster
description: 自动化内容发布助手。支持将 Markdown 文章自动发布到知乎和微信公众号，具备 Mac 风格代码块渲染、图片自动上传和自定义样式功能。
---

# 自动发布助手 (Auto Poster)

本技能用于自动化将本地 Markdown 内容发布到 **知乎** 和 **微信公众号** 等媒体平台。

> 详细文档请参考 [README.md](README.md)

## 核心特性

1.  **持久化登录**：一次登录，长期有效（数据存储在 `~/.auto-poster/browser_data`）。
2.  **高级渲染**：支持 **Mac 风格代码块** 和自定义 CSS 样式（内置 `wechat.css`）。
3.  **智能图片处理**：自动下载远程图片，并通过剪贴板自动上传本地图片到编辑器。
4.  **轻量启动**：复用本地 Chrome 浏览器。

## 快速开始

### 1. 环境配置

```bash
cd skills/auto-poster
pip install -r requirements.txt
playwright install chromium
```

### 2. 发布命令

**发布到微信公众号 (WeChat):**
```bash
python scripts/wechat_poster.py -m /path/to/your/article.md
```
*   自动渲染样式、粘贴内容并上传图片。

**发布到知乎 (Zhihu):**
```bash
python scripts/zhihu_poster.py -m /path/to/your/article.md
```

## 注意事项

- 脚本会打开本地 Chrome 浏览器，请勿关闭窗口。
- **微信发布**：脚本会自动控制剪贴板进行内容和图片粘贴，请勿干扰。
- 内容填充后，请务必人工检查格式，并手动点击最终的“发布”按钮。
