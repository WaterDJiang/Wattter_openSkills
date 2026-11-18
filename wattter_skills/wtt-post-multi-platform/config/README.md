# 配置说明

本目录集中管理 `wtt-post-multi-platform` 的平台配置。

## 文件

- `config.json`：真实配置
- `config.example.json`：参考模板

## 规则

- 所有平台共用一个配置文件
- 每个平台使用一个顶层节点
- 各平台脚本只读取自己的节点

## 当前字段

### `wechat`

- `appid`：公众号应用 ID
- `appsecret`：公众号应用密钥
- `thumb_media_id`：默认封面素材 ID

补充：

- `appid` + `appsecret` 用于获取 `access_token`
- `thumb_media_id` 只在没有命令行封面、也没有自动生成封面时兜底使用

### `zhihu`

- `user_data_dir`：浏览器登录态目录
- `cdp_url`：连接已有 Chrome 的调试地址

补充：

- 这两个字段目前主要作为统一配置预留

## 扩展

- 后续新增 `weibo`、`x`、`xiaohongshu`、`douyin`、`bilibili` 时，直接增加对应顶层节点
- `config.example.json` 里的其他社交平台字段目前仅作参考，不代表已经接入

## 注意

- `config.json` 是标准 JSON，不能写注释
- 配置说明统一写在本 README
- 对外分享时优先使用 `config.example.json`
