#!/usr/bin/env python3
"""视频台词声明协议；不加载模型、不读取私人配置、不生成声音。"""
import hashlib
import json
import math
import re

IDENTIFIER = re.compile(r'[a-z][a-z0-9-]*')
CAST_FIELDS = {'voiceId', 'label', 'description'}
UTTERANCE_FIELDS = {'id', 'speakerId', 'text', 'voice', 'performance',
                    'pauseAfterSeconds', 'externalVoiceVerified'}
PERFORMANCE_FIELDS = {'instruct', 'intent'}


def _identifier(value, label):
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise ValueError(f'{label} 必须为 kebab-case：{value}')
    return value


def _cast(film):
    cast = film.get('cast', {})
    if not isinstance(cast, dict):
        raise ValueError('cast 必须为角色映射对象')
    for speaker, entry in cast.items():
        _identifier(speaker, 'speakerId')
        if not isinstance(entry, dict) or set(entry) - CAST_FIELDS:
            raise ValueError(f'cast.{speaker} 只支持 voiceId、label、description')
        voice_id = entry.get('voiceId')
        if voice_id is None:
            if speaker != 'narrator':
                raise ValueError(f'角色 {speaker} 缺少 voiceId；只有 narrator 可沿用默认音色')
        elif not isinstance(voice_id, str) or not voice_id.strip():
            raise ValueError(f'cast.{speaker}.voiceId 必须为非空音色ID')
        for key in ('label', 'description'):
            if key in entry and not isinstance(entry[key], str):
                raise ValueError(f'cast.{speaker}.{key} 必须为字符串')
    return cast


def performance(value=None):
    if value is None:
        value = {}
    if not isinstance(value, dict) or set(value) - PERFORMANCE_FIELDS:
        raise ValueError('performance 只支持 instruct、intent；表演提示与正文分开')
    result = {'instruct': '', 'intent': ''}
    for key, text in value.items():
        if not isinstance(text, str):
            raise ValueError(f'performance.{key} 必须为字符串')
        result[key] = text.strip()
    return result


def _scene_jobs(scene, cast):
    sid = _identifier(scene.get('id'), '镜头 id')
    text = scene.get('narration', '')
    if not isinstance(text, str):
        raise ValueError(f'{sid}.narration 必须为字符串')
    if 'utterances' not in scene:
        if not text.strip():
            return []
        return [dict(id=sid, speakerId='narrator', text=text.strip(),
                     voiceId=cast.get('narrator', {}).get('voiceId'),
                     voice=scene.get('voice', f'audio/{sid}.wav'),
                     performance=performance(), pauseAfterSeconds=0,
                     externalVoiceVerified=bool(scene.get('externalVoiceVerified', False)),
                     legacy=True)]
    if text.strip() or scene.get('voice') not in (None, ''):
        raise ValueError(f'{sid} 的 utterances 不能与非空 narration/voice 同时使用')
    values = scene['utterances']
    if not isinstance(values, list) or not values:
        raise ValueError(f'{sid}.utterances 必须为非空数组；无台词镜头请省略该字段')
    result = []
    for value in values:
        if not isinstance(value, dict) or set(value) - UTTERANCE_FIELDS:
            raise ValueError(f'{sid}.utterances 含不支持字段')
        uid = _identifier(value.get('id'), 'utterance id')
        speaker = _identifier(value.get('speakerId'), 'speakerId')
        if speaker not in cast and speaker != 'narrator':
            raise ValueError(f'未知角色：{speaker}；先在 cast 配置 voiceId')
        words = value.get('text')
        if not isinstance(words, str) or not words.strip():
            raise ValueError(f'{uid}.text 必须为非空台词')
        voice = value.get('voice', f'audio/{sid}-{uid}.wav')
        if not isinstance(voice, str) or not voice.strip() or '://' in voice:
            raise ValueError(f'{uid}.voice 必须为本地WAV路径')
        if not voice.lower().endswith('.wav'):
            raise ValueError(f'{uid}.voice 必须为WAV路径')
        pause = value.get('pauseAfterSeconds', 0)
        if isinstance(pause, bool) or not isinstance(pause, (int, float)) or not math.isfinite(pause) or pause < 0:
            raise ValueError(f'{uid}.pauseAfterSeconds 必须为非负有限秒数')
        verified = value.get('externalVoiceVerified', False)
        if type(verified) is not bool:
            raise ValueError(f'{uid}.externalVoiceVerified 必须为布尔值')
        result.append(dict(id=uid, speakerId=speaker, text=words.strip(),
                           voiceId=cast.get(speaker, {}).get('voiceId'), voice=voice,
                           performance=performance(value.get('performance')),
                           pauseAfterSeconds=pause, externalVoiceVerified=verified,
                           legacy=False))
    return result


def has_utterances(film):
    return any('utterances' in s for s in film.get('scenes', []) if isinstance(s, dict))


def scene_utterances(film, scene):
    """Return declared jobs, keeping unresolved default voiceId as None."""
    cast = _cast(film)
    scenes = film.get('scenes', [])
    if not isinstance(scenes, list):
        raise ValueError('scenes 必须为数组')
    seen, wanted = set(), None
    for current in scenes:
        if not isinstance(current, dict):
            raise ValueError('scene 必须为对象')
        jobs = _scene_jobs(current, cast)
        for job in jobs:
            if job['id'] in seen:
                raise ValueError(f'台词 id 在项目内必须唯一：{job["id"]}')
            seen.add(job['id'])
        if current is scene or current == scene:
            wanted = jobs
    if wanted is None:
        raise ValueError('镜头不在当前film.scenes中')
    return wanted


def request_fingerprint(job):
    request = {key: job.get(key) for key in ('id', 'speakerId', 'voiceId', 'text')}
    request['performance'] = performance(job.get('performance'))
    raw = json.dumps(request, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(raw).hexdigest()


def utterance_seed(seed, utterance_id):
    if type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError('seed 必须为0至2^32-1整数')
    _identifier(utterance_id, 'utterance id')
    return int.from_bytes(hashlib.sha256(f'{seed}:{utterance_id}'.encode()).digest()[:4], 'big')
