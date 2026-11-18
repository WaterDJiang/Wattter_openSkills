# Zhihu Platform / 知乎平台

知乎平台目录用于将本地 Markdown 文章自动填充到知乎专栏编辑器，适合技术文章、长文笔记和结构化内容发布。

## 核心能力

- 持久化登录：浏览器会话保存在 `~/.auto-poster/browser_data/zhihu`
- Markdown 转 HTML：保留代码块、表格和常见排版结构
- Mac 风格代码块：自动为代码块补充窗口控制点样式
- 图片处理：自动下载远程图片，并在可用时协助上传到编辑器
- 本地运行：基于 Playwright 调用本机 Chrome，不依赖远端服务

## 环境要求

- Python 3.8+
- Google Chrome
- Playwright Chromium 驱动

## 安装

```bash
cd skills/wtt-post-multi-platform
pip install -r requirements.txt
playwright install chromium
```

## 使用

统一入口：

```bash
python scripts/post.py --platform zhihu -m /path/to/article.md
```

直接调用平台脚本：

```bash
python platforms/zhihu/scripts/zhihu_poster.py -m /path/to/article.md
```

首次运行时需要在打开的浏览器里完成登录。脚本会自动填写标题和正文，完成后请人工检查内容并手动点击知乎的发布按钮。

## 配置

- 统一配置文件：`config/config.json`
- 样式文件：`scripts/assets/article.css`
- 登录目录：`~/.auto-poster/browser_data/zhihu`

## 说明

- 脚本执行期间不要关闭浏览器窗口
- 如果页面结构变更导致定位失败，需要更新 `scripts/zhihu_poster.py` 中的选择器
- 如需重置登录状态，删除 `~/.auto-poster/browser_data/zhihu`
