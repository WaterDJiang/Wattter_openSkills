# 微信公众号草稿箱 API 文档

## 接口信息

- **接口地址**: `POST https://api.weixin.qq.com/cgi-bin/draft/add?access_token=ACCESS_TOKEN`
- **接口名称**: 新增草稿 (draft_add)
- **适用范围**: 公众号、服务号

## 请求参数

### Query Parameters

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| access_token | string | 是 | 接口调用凭证 |

### Body Parameters (articles Array)

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| article_type | string | 否 | 文章类型: `news`(图文消息，默认), `newspic`(图片消息) |
| title | string | 是 | 标题，总长度不超过32个字 |
| author | string | 否 | 作者，总长度不超过16个字 |
| digest | string | 否 | 摘要，总长度不超过128个字 |
| content | string | 是 | 图文消息内容，支持HTML标签，少于2万字符，小于1M |
| content_source_url | string | 否 | 原文地址，点击"阅读原文"的URL |
| thumb_media_id | string | 条件必填 | 封面图片素材id (article_type为news时必填) |
| need_open_comment | number | 否 | 是否打开评论: 0不打开(默认), 1打开 |
| only_fans_can_comment | number | 否 | 是否粉丝才可评论: 0所有人(默认), 1粉丝 |
| pic_crop_235_1 | string | 否 | 封面裁剪2.35:1规格坐标 |
| pic_crop_1_1 | string | 否 | 封面裁剪1:1规格坐标 |
| image_info | object | 条件 | 图片消息的图片信息 (article_type为newspic时) |
| cover_info | object | 否 | 图片消息的封面信息 |
| product_info | object | 否 | 商品信息 |

## 返回参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| media_id | string | 上传后的获取标志 (不超过128字符) |

## 错误码

| 错误码 | 描述 | 解决方案 |
|--------|------|----------|
| 53404 | 账号已被限制带货能力 | 请删除商品后重试 |
| 53405 | 插入商品信息有误 | 检查参数及商品状态 |
| 53406 | 请先开通带货能力 | - |

## 调用示例

### 请求体 (图文消息)

```json
{
    "articles": [
        {
            "article_type": "news",
            "title": "文章标题",
            "author": "作者名",
            "digest": "文章摘要...",
            "content": "<p>HTML内容...</p>",
            "content_source_url": "https://example.com/original",
            "thumb_media_id": "永久素材media_id",
            "need_open_comment": 0,
            "only_fans_can_comment": 0
        }
    ]
}
```

### 请求体 (图片消息)

```json
{
    "articles": [
        {
            "article_type": "newspic",
            "title": "图片消息标题",
            "content": "<p>内容...</p>",
            "need_open_comment": 0,
            "only_fans_can_comment": 0,
            "image_info": {
                "image_list": [
                    {
                        "image_media_id": "图片素材media_id"
                    }
                ]
            },
            "cover_info": {
                "crop_percent_list": [
                    {
                        "ratio": "1_1",
                        "x1": "0.166454",
                        "y1": "0",
                        "x2": "0.833545",
                        "y2": "1"
                    }
                ]
            }
        }
    ]
}
```

### 返回示例

```json
{
  "media_id": "MEDIA_ID"
}
```

## 获取 access_token

access_token 是公众号的全局唯一接口调用凭据。

### 请求地址

```
GET https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=APPID&secret=APPSECRET
```

### 返回参数

```json
{
    "access_token": "ACCESS_TOKEN",
    "expires_in": 7200
}
```

## 永久素材上传 (获取 thumb_media_id)

如需要封面图片，需要先上传为永久素材:

```
POST https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=ACCESS_TOKEN&type=image
```

图片大小不超过 2M，支持 jpg/png 格式。

返回:
```json
{
    "media_id": "永久素材media_id",
    "url": "图片URL"
}
```
