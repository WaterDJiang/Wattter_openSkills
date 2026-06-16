# Auto Poster / 自动发布助手

[English](#english) | [中文](#chinese)

---

<a name="english"></a>
## English

**Auto Poster** is a powerful automation tool designed to streamline your content publishing workflow. It transforms local Markdown articles into beautifully formatted HTML and automatically publishes them to **Zhihu** and **WeChat Official Account**.

It solves the common headache of repeated logins, complex API limitations, and style loss by using a persistent browser context and a smart "Render-then-Copy" strategy.

### Key Features

*   **🎨 Advanced Rendering**: 
    *   Converts Markdown to WeChat-compatible HTML.
    *   **Mac-Style Code Blocks**: Automatically adds macOS window controls (🔴🟡🟢) to code blocks for a polished look.
    *   **Custom Themes**: Applies professional styling using `assets/wechat.css`.
*   **🖼️ Smart Image Handling**:
    *   **Auto Upload**: Automatically uploads local images to the editor by simulating clipboard operations (Copy & Paste).
    *   **Remote Download**: Automatically downloads remote images (HTTP/HTTPS) to a temporary directory for seamless uploading.
*   **🔐 Persistent Login**: Browser cookies and session data are stored in `~/.wtt-auto-poster/browser_data`. Log in once, and it stays valid for a long time.
*   **🚀 Lightweight & Privacy**: Built on Python Playwright Core using your local Chrome. All data stays on your machine.

### Prerequisites

*   Python 3.8+
*   Google Chrome Browser
*   **Clipboard Tools** (for image uploading):
    *   **macOS**: Built-in (uses Swift script).
    *   **Windows**: PowerShell (pre-installed).
    *   **Linux**: `wl-clipboard` (Wayland) or `xclip` (X11).

### Installation

1.  Navigate to the skill directory:
    ```bash
    cd skills/wtt-auto-poster
    ```

2.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  Install Playwright driver (only needed once):
    ```bash
    playwright install chromium
    ```

### Usage

#### 1. Publish to WeChat Official Account

```bash
python scripts/wechat_poster.py -m /path/to/your/article.md
```
*   **Workflow**:
    1.  **Render**: Opens a local tab to render Markdown into styled HTML.
    2.  **Copy**: Copies the rendered content to the clipboard.
    3.  **Paste**: Navigates to WeChat "New Article" page and pastes the content.
    4.  **Images**: Scans for image placeholders and automatically uploads images one by one.
*   **First Run**: Scan the QR code to log in.
*   **Action Required**: Verify the content and click "Save" or "Publish" manually.

#### 2. Publish to Zhihu

```bash
python scripts/zhihu_poster.py -m /path/to/your/article.md
```
*   Automatically fills title and content.
*   **Action Required**: Verify and click "Publish".

### Configuration

*   **Styles**: Edit `scripts/assets/wechat.css` to customize the appearance of your articles.
*   **User Data**: Login sessions are stored in `~/.wtt-auto-poster/browser_data/`. Delete this folder to reset login state.

---

<a name="chinese"></a>
## 中文

**Auto Poster (自动发布助手)** 是一个强大的内容发布自动化工具。它能将本地 Markdown 文章转换为格式精美的 HTML，并自动发布到 **知乎** 和 **微信公众号**。

通过“本地渲染+模拟粘贴”的策略，它完美解决了样式丢失、图片上传繁琐以及 API 限制等痛点。

### 核心特性

*   **🎨 高级渲染引擎**：
    *   **Mac 风格代码块**：自动为代码块添加 macOS 窗口控制点（🔴🟡🟢），提升技术文章颜值。
    *   **自定义主题**：内置 `assets/wechat.css` 样式表，支持自定义排版。
*   **🖼️ 智能图片处理**：
    *   **自动上传**：通过模拟剪贴板操作（复制/粘贴），自动将本地图片上传到编辑器中替换占位符。
    *   **远程下载**：自动检测 Markdown 中的网络图片链接，下载到临时目录后上传，确保图片稳定显示。
*   **🔐 持久化登录**：Cookie 和 Session 存储在 `~/.wtt-auto-poster/browser_data`。一次登录，长期有效。
*   **🚀 轻量安全**：基于 Playwright 复用本地 Chrome，数据完全掌握在自己手中。

### 前置要求

*   Python 3.8+
*   Google Chrome 浏览器
*   **剪贴板工具** (用于图片自动上传):
    *   **macOS**: 内置支持 (使用 Swift 脚本)。
    *   **Windows**: PowerShell (系统自带)。
    *   **Linux**: 需安装 `wl-clipboard` (Wayland) 或 `xclip` (X11)。

### 安装指南

1.  进入技能目录：
    ```bash
    cd skills/wtt-auto-poster
    ```

2.  安装依赖：
    ```bash
    pip install -r requirements.txt
    ```

3.  安装 Playwright 驱动（仅需一次）：
    ```bash
    playwright install chromium
    ```

### 使用方法

#### 1. 发布到微信公众号 (WeChat)

```bash
python scripts/wechat_poster.py -m /path/to/your/article.md
```
*   **工作流程**：
    1.  **渲染**：在本地浏览器标签页中将 Markdown 渲染为带样式的 HTML。
    2.  **复制**：自动复制渲染后的内容。
    3.  **粘贴**：跳转到微信“写新图文”页面并粘贴正文。
    4.  **图片**：自动扫描文中的图片占位符，逐张上传并替换图片。
*   **首次运行**：需扫码登录。
*   **操作**：脚本完成后，请人工检查排版和图片，最后点击“保存”或“发布”。

#### 2. 发布到知乎 (Zhihu)

```bash
python scripts/zhihu_poster.py -m /path/to/your/article.md
```
*   自动填充标题和内容。
*   **操作**：确认无误后手动点击“发布”。

### 配置说明

*   **样式定制**: 修改 `scripts/assets/wechat.css` 可调整文章样式。
*   **重置登录**: 删除 `~/.wtt-auto-poster/browser_data/` 目录即可退出登录。
