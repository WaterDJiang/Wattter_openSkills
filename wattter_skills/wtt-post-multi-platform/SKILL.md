---
name: wtt-post-multi-platform
description: 多平台内容发布助手。统一封装微信公众号 API 发布与知乎浏览器自动发布；当用户需要把 Markdown 发布到不同内容平台时调用。
---

# 多平台内容发布助手

`wtt-post-multi-platform` 用于把本地 Markdown 内容发布到多个内容平台，同时保持每个平台的发布链路、配置和依赖相互独立。

## 适用场景

- 用户需要把同一篇 Markdown 发布到不同平台
- 平台前置条件类似，但发布实现不同
- 需要复用统一 skill 名称，同时保留平台级隔离

## 当前支持

- `wechat`：微信公众号草稿箱 API 发布
- `zhihu`：知乎专栏浏览器自动填充

## 使用方式

### 统一入口

```bash
cd skills/wtt-post-multi-platform
pip install -r requirements.txt
python scripts/post.py --platform wechat -m /path/to/article.md
python scripts/post.py --platform zhihu -m /path/to/article.md
```

### 平台附加参数

微信可以继续透传海报相关参数：

```bash
python scripts/post.py --platform wechat -m /path/to/article.md --enable-posters
```

知乎可以继续透传浏览器相关参数：

```bash
python scripts/post.py --platform zhihu -m /path/to/article.md --use-existing-chrome
```

## 配置方式

- 统一配置文件：`config/config.json`
- 示例配置文件：`config/config.example.json`
- 各平台在同一配置文件中使用独立节点，例如 `wechat`、`zhihu`

## 目录结构

```text
wtt-post-multi-platform/
├── SKILL.md
├── README.md
├── requirements.txt
├── scripts/
│   └── post.py
└── platforms/
    ├── wechat/
    │   ├── README.md
    │   ├── references/
    │   ├── templates/
    │   └── scripts/
    └── zhihu/
        ├── README.md
        └── scripts/
```

## 设计原则

1. 平台独立：每个平台保留自己的脚本、素材和发布链路
2. 统一入口：根目录只负责路由，不混合平台内部逻辑
3. 配置统一：所有平台共用根级配置中心，但只读取各自配置节点
4. 可扩展：后续新增微博、X、小红书时只增加新的平台目录与配置节点
