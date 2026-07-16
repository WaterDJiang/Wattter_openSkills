#!/usr/bin/env python3
import argparse
import base64
import json
import mimetypes
import re
import secrets
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path


API_BASE = "https://api.weixin.qq.com/cgi-bin"


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"config not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json config {path}: {exc}")


def api_json(url: str, data: dict | None = None) -> dict:
    body = None
    headers = {}
    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    req = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    if payload.get("errcode"):
        raise RuntimeError(json.dumps(payload, ensure_ascii=False))
    return payload


def multipart_upload(url: str, file_path: Path, field_name: str = "media") -> dict:
    boundary = "----wttBoundary" + secrets.token_hex(12)
    mime = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    file_bytes = file_path.read_bytes()
    parts = [
        f"--{boundary}\r\n".encode(),
        (
            f'Content-Disposition: form-data; name="{field_name}"; '
            f'filename="{file_path.name}"\r\n'
        ).encode(),
        f"Content-Type: {mime}\r\n\r\n".encode(),
        file_bytes,
        b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ]
    req = urllib.request.Request(
        url,
        data=b"".join(parts),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    if payload.get("errcode"):
        raise RuntimeError(json.dumps(payload, ensure_ascii=False))
    return payload


def get_access_token(config: dict) -> str:
    if config.get("access_token"):
        return config["access_token"]
    appid = config.get("appid")
    appsecret = config.get("appsecret")
    if not appid or not appsecret:
        raise SystemExit("config must include access_token or appid/appsecret")
    query = urllib.parse.urlencode(
        {"grant_type": "client_credential", "appid": appid, "secret": appsecret}
    )
    payload = api_json(f"{API_BASE}/token?{query}")
    token = payload.get("access_token")
    if not token:
        raise RuntimeError(f"missing access_token in response: {payload}")
    return token


def parse_manifest(path: Path | None) -> list[dict]:
    if not path:
        return []
    if path.suffix == ".json":
        payload = load_json(path)
        images = payload.get("body_images") or payload.get("posters") or []
        return [image for image in images if isinstance(image, dict)]
    posters: list[dict] = []
    current: dict | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if line.startswith("  - index:"):
            if current:
                posters.append(current)
            current = {"index": line.split(":", 1)[1].strip()}
        elif current and line.startswith("    "):
            key, _, value = line.strip().partition(":")
            if key in {"type", "title", "path", "placeholder"}:
                current[key] = value.strip()
    if current:
        posters.append(current)
    return posters


def is_remote_src(src: str) -> bool:
    return src.startswith("https://") or src.startswith("http://")


def src_to_local_path(src: str) -> Path | None:
    if is_remote_src(src):
        return None
    if src.startswith("file://"):
        return Path(urllib.parse.unquote(urllib.parse.urlparse(src).path))
    path = Path(src)
    if path.is_absolute():
        return path
    return None


def data_uri_to_temp_file(src: str) -> Path | None:
    match = re.match(r"data:(image/[-+.\w]+);base64,(.+)", src, re.S)
    if not match:
        return None
    mime, data = match.groups()
    suffix = mimetypes.guess_extension(mime) or ".png"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(base64.b64decode(data))
    tmp.close()
    return Path(tmp.name)


def replace_placeholder_paragraph(html: str, placeholder: str, image_url: str, title: str) -> str:
    escaped = re.escape(placeholder)
    image_html = (
        '<p style="margin:1.6em 8px;text-align:center;">'
        f'<img src="{image_url}" alt="{title}" '
        'style="max-width:100%;height:auto;display:block;margin:0 auto;"/>'
        "</p>"
    )
    pattern = re.compile(r"<p[^>]*>\s*" + escaped + r"\s*</p>")
    updated, count = pattern.subn(image_html, html, count=1)
    if count:
        return updated
    return html.replace(placeholder, image_html, 1)


def replace_local_html_images(access_token: str, html: str) -> tuple[str, list[dict]]:
    uploaded: list[dict] = []

    def replace_src(match: re.Match) -> str:
        quote = match.group("quote")
        src = match.group("src")
        if is_remote_src(src):
            return match.group(0)

        temp_path: Path | None = None
        if src.startswith("data:image/"):
            image_path = data_uri_to_temp_file(src)
            temp_path = image_path
        else:
            image_path = src_to_local_path(src)

        if not image_path or not image_path.is_file():
            return match.group(0)

        image_url = upload_body_image(access_token, image_path)
        uploaded.append({"path": str(image_path), "url": image_url, "source": "html-img"})
        if temp_path:
            temp_path.unlink(missing_ok=True)
        return f'src={quote}{image_url}{quote}'

    pattern = re.compile(r"src=(?P<quote>['\"])(?P<src>.*?)(?P=quote)", re.I | re.S)
    return pattern.sub(replace_src, html), uploaded


def upload_cover(access_token: str, cover_path: Path) -> str:
    url = f"{API_BASE}/material/add_material?access_token={urllib.parse.quote(access_token)}&type=thumb"
    payload = multipart_upload(url, cover_path)
    media_id = payload.get("media_id")
    if not media_id:
        raise RuntimeError(f"missing cover media_id in response: {payload}")
    return media_id


def upload_body_image(access_token: str, image_path: Path) -> str:
    url = f"{API_BASE}/media/uploadimg?access_token={urllib.parse.quote(access_token)}"
    payload = multipart_upload(url, image_path)
    image_url = payload.get("url")
    if not image_url:
        raise RuntimeError(f"missing body image url in response: {payload}")
    return image_url


def add_draft(access_token: str, article: dict) -> dict:
    url = f"{API_BASE}/draft/add?access_token={urllib.parse.quote(access_token)}"
    return api_json(url, {"articles": [article]})


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a WeChat Official Account draft through the official API."
    )
    parser.add_argument("--config", required=True, help="JSON with access_token or appid/appsecret")
    parser.add_argument("--title", required=True)
    parser.add_argument("--html", required=True)
    parser.add_argument("--cover-image", required=True)
    parser.add_argument("--manifest", help="manifest.json or manifest.yaml from prepare-weixin-rich-html.py")
    parser.add_argument("--author", default="")
    parser.add_argument("--digest", default="")
    parser.add_argument("--source-url", default="")
    parser.add_argument("--need-open-comment", type=int, default=0)
    parser.add_argument("--only-fans-can-comment", type=int, default=0)
    args = parser.parse_args()

    config = load_json(Path(args.config))
    access_token = get_access_token(config)
    html = Path(args.html).read_text(encoding="utf-8")
    cover_path = Path(args.cover_image)
    if not cover_path.is_file():
        raise SystemExit(f"cover image not found: {cover_path}")

    uploaded_images = []
    for poster in parse_manifest(Path(args.manifest) if args.manifest else None):
        image_path = Path(poster.get("path", ""))
        placeholder = poster.get("placeholder", "")
        if not image_path.is_file() or not placeholder:
            continue
        image_url = upload_body_image(access_token, image_path)
        html = replace_placeholder_paragraph(
            html, placeholder, image_url, poster.get("title") or placeholder
        )
        uploaded_images.append({"placeholder": placeholder, "path": str(image_path), "url": image_url})

    html, html_images = replace_local_html_images(access_token, html)
    uploaded_images.extend(html_images)

    thumb_media_id = upload_cover(access_token, cover_path)
    article = {
        "title": args.title,
        "author": args.author or config.get("author", ""),
        "digest": args.digest,
        "content": html,
        "content_source_url": args.source_url,
        "thumb_media_id": thumb_media_id,
        "need_open_comment": args.need_open_comment,
        "only_fans_can_comment": args.only_fans_can_comment,
    }
    result = add_draft(access_token, article)
    print(
        json.dumps(
            {
                "status": "draft_created",
                "media_id": result.get("media_id"),
                "thumb_media_id": thumb_media_id,
                "body_images": uploaded_images,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
