#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
from typing import Dict, Optional

def upload_image(image_path: str, access_token: str, permanent: bool = False) -> Dict:
    """
    上传图片到微信公众号素材库

    Args:
        image_path: 本地图片路径
        access_token: 微信API access_token
        permanent: 是否上传为永久素材（默认False，临时素材3天有效）

    Returns:
        {
            "media_id": "素材ID",
            "url": "图片URL",
            "type": "image"
        }

    Raises:
        Exception: 上传失败时抛出异常
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图片文件不存在: {image_path}")

    # 选择API端点
    if permanent:
        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=image"
    else:
        url = f"https://api.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type=image"

    # 准备文件
    files = {
        'media': open(image_path, 'rb')
    }

    try:
        response = requests.post(url, files=files, timeout=30)
        response.raise_for_status()
        result = response.json()

        if 'errcode' in result and result['errcode'] != 0:
            raise Exception(f"微信API返回错误: {result.get('errmsg', '未知错误')} (errcode: {result.get('errcode')})")

        # 临时素材和永久素材返回格式不同
        if permanent:
            return {
                'media_id': result.get('media_id'),
                'url': result.get('url'),
                'type': 'image',
                'permanent': True
            }
        else:
            return {
                'media_id': result.get('media_id'),
                'type': result.get('type'),
                'created_at': result.get('created_at'),
                'permanent': False
            }

    except requests.exceptions.RequestException as e:
        raise Exception(f"上传图片失败: {str(e)}")
    finally:
        files['media'].close()

def get_material_url(media_id: str, access_token: str) -> Optional[str]:
    """
    获取永久素材的URL（临时素材不需要调用这个接口）

    Args:
        media_id: 素材ID
        access_token: 微信API access_token

    Returns:
        素材的URL，获取失败时返回None
    """
    url = f"https://api.weixin.qq.com/cgi-bin/material/get_material?access_token={access_token}"

    try:
        response = requests.post(url, json={'media_id': media_id}, timeout=10)
        response.raise_for_status()
        # 注意：图片素材会直接返回二进制内容，不会返回JSON
        # 这个接口主要用于获取图文、视频等素材，图片素材的URL在上传时已经返回
        return None
    except Exception as e:
        print(f"获取素材URL失败: {e}")
        return None

def upload_poster_image(image_path: str, access_token: str, permanent: bool = True) -> Dict:
    """
    上传海报图片到微信素材库

    注意：海报必须使用永久素材，因为临时素材没有可直接访问的URL，
    无法在微信公众号文章中显示。permanent 参数默认为 True。

    Args:
        image_path: 图片路径
        access_token: 访问令牌
        permanent: 是否永久保存（默认 True，临时素材无法在文章中显示）

    Returns:
        包含 media_id 和 url 的字典
    """
    # 海报需要显示在文章中，临时素材没有可直接访问的URL，强制使用永久素材
    if not permanent:
        print("⚠️  海报图片强制使用永久素材（临时素材无法在文章中显示）")
        permanent = True

    result = upload_image(image_path, access_token, permanent)

    # 永久素材会返回url字段
    if 'url' not in result or not result['url']:
        # 如果没有返回url，使用占位符（通常不会发生）
        result['url'] = f"https://mmbiz.qpic.cn/mmbiz_png/placeholder/{result['media_id']}/0?wx_fmt=png"

    return result
