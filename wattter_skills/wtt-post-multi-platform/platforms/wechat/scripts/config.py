"""微信公众号平台配置读取工具。"""

import json
from pathlib import Path


ROOT_CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "config.json"
ROOT_CONFIG_EXAMPLE_PATH = Path(__file__).resolve().parents[3] / "config" / "config.example.json"
WECHAT_CONFIG_KEY = "wechat"


def get_root_config():
    """读取多平台统一配置文件。"""
    if ROOT_CONFIG_PATH.exists():
        with open(ROOT_CONFIG_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}


def save_root_config(config):
    """保存多平台统一配置文件。"""
    ROOT_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(ROOT_CONFIG_PATH, "w", encoding="utf-8") as file:
        json.dump(config, file, ensure_ascii=False, indent=2)


def get_config():
    """获取微信公众号平台配置。"""
    root_config = get_root_config()
    platform_config = root_config.get(WECHAT_CONFIG_KEY, {})
    return platform_config if isinstance(platform_config, dict) else {}


def get_access_token():
    """使用微信公众号配置自动刷新 access_token。"""
    config = get_config()
    appid = config.get("appid", "")
    appsecret = config.get("appsecret", "")

    if not appid or not appsecret:
        return None

    import requests

    url = (
        "https://api.weixin.qq.com/cgi-bin/token"
        f"?grant_type=client_credential&appid={appid}&secret={appsecret}"
    )
    response = requests.get(url)
    result = response.json()

    if "access_token" in result:
        return result["access_token"]

    print(f"❌ 获取 access_token 失败: {result}")
    return None


def get_thumb_media_id():
    """获取默认封面图 media_id。"""
    config = get_config()
    return config.get("thumb_media_id", "")


def init_config():
    """初始化统一配置文件中的微信公众号配置。"""
    root_config = get_root_config()
    if WECHAT_CONFIG_KEY not in root_config:
        root_config[WECHAT_CONFIG_KEY] = {
            "appid": "YOUR_APPID_HERE",
            "appsecret": "YOUR_APPSECRET_HERE",
            "thumb_media_id": "",
        }
        save_root_config(root_config)
        print(f"📝 配置文件已创建: {ROOT_CONFIG_PATH}")
        print(f"📄 可参考示例文件: {ROOT_CONFIG_EXAMPLE_PATH}")
        print("⚠️  请编辑 wechat 配置填入你的 appid 和 appsecret")
        return

    print(f"📁 配置文件已存在: {ROOT_CONFIG_PATH}")
    config = get_config()
    if config.get("appid") == "YOUR_APPID_HERE":
        print("⚠️  请编辑 wechat 配置填入你的 appid 和 appsecret")


if __name__ == "__main__":
    init_config()
