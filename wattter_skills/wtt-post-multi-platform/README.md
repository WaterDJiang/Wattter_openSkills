# wtt-post-multi-platform

`wtt-post-multi-platform` 是一个统一的多平台发布 skill，用同一个入口管理多个内容渠道，但每个平台都保留各自独立的实现、配置与资源目录。

## 当前支持的平台

- `wechat`：微信公众号草稿箱 API 发布
- `zhihu`：知乎专栏浏览器自动化发布

## 设计目标

- skill 名称稳定，不因新增平台频繁改名
- 平台实现独立，避免 API 链路和浏览器自动化链路互相污染
- 统一入口清晰，方便后续扩展到微博、X、小红书、B 站等渠道

## 安装

```bash
cd skills/wtt-post-multi-platform
pip install -r requirements.txt
playwright install chromium
```

## 统一配置

- 真实配置文件：`config/config.json`
- 示例配置文件：`config/config.example.json`
- 每个平台在同一个配置文件里使用独立节点管理，例如 `wechat`、`zhihu`

## 统一入口

```bash
python scripts/post.py --platform wechat -m /path/to/article.md
python scripts/post.py --platform zhihu -m /path/to/article.md
```

## 透传平台参数

统一入口会把额外参数继续透传给对应平台脚本。

```bash
python scripts/post.py --platform wechat -m /path/to/article.md --enable-posters
python scripts/post.py --platform zhihu -m /path/to/article.md --use-existing-chrome
```

## 目录说明

```text
skills/wtt-post-multi-platform/
├── SKILL.md
├── README.md
├── requirements.txt
├── scripts/
│   └── post.py                 # 统一入口，只做平台路由
└── platforms/
    ├── wechat/
    │   ├── README.md           # 微信平台说明
    │   ├── references/         # API 文档
    │   ├── templates/          # 海报模板
    │   └── scripts/            # 微信 API 发布链路
    └── zhihu/
        ├── README.md           # 知乎平台说明
        └── scripts/            # 浏览器自动化发布链路
```

## 平台独立性约束

- 微信平台继续使用 `config.py` 和草稿箱 API
- 知乎平台继续使用 Playwright 和本地浏览器登录态
- 根目录不下沉平台内部依赖，只负责入口路由与统一说明
- 平台间不共用发布逻辑，避免一个平台变更影响另一个平台
- 平台配置统一放在根级 `config/config.json`，各平台只读取自己的配置节点
