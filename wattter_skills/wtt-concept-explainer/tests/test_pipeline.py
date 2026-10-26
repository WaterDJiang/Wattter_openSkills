"""Behavioral checks for variable runtime and stale media rejection."""
import copy
import importlib.util
import json
import math
import tempfile
import unittest
import wave
from pathlib import Path

spec = importlib.util.spec_from_file_location('pipeline', Path(__file__).parents[1] / 'scripts/pipeline.py')
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


class TimelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.c = {'schema': p.SCHEMA, 'width': 640, 'height': 360, 'fps': 24,
                  'scenes': [{'id': 'one', 'visualSeconds': 2, 'narration': ''}]}
        self.save()

    def tearDown(self):
        self.tmp.cleanup()

    def save(self):
        p.write(self.root / 'film.json', self.c)

    def voice(self, seconds, text='测试语音'):
        folder = self.root / 'audio'
        folder.mkdir(exist_ok=True)
        file = folder / 'one.wav'
        with wave.open(str(file), 'wb') as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(8000)
            f.writeframes(b'\0\0' * round(seconds * 8000))
        self.c['scenes'][0]['narration'] = text
        p.write(file.with_suffix('.wav.json'), {'text': text, 'audioSha256': p.digest(file)})
        self.save()
        return file

    def test_duration_is_content_driven_not_thirty_seconds(self):
        for seconds in (12, 47, 135):
            self.c['scenes'][0]['visualSeconds'] = seconds
            self.save()
            t = p.compile_timeline(self.root, True)
            self.assertEqual(t['totalFrames'], seconds * 24)

    def test_visual_combinations_survive_timeline_compilation(self):
        subject = {'id': 'same-hero', 'type': 'seed-character'}
        self.c['scenes'] = [dict(id=style, visualSeconds=2, narration='', visual={
            'subject': subject, 'style': style,
            'motion': {'action': 'hop', 'effect': 'assemble'}, 'renderer': 'canvas2d'
        }) for style in ('flat', 'sand', 'particles')]
        self.save()
        result = p.compile_timeline(self.root, True)
        for before, after in zip(self.c['scenes'], result['scenes']):
            self.assertEqual(before['visual'], after['visual'])

    def test_measured_speech_extends_scene_and_captions_fit(self):
        self.voice(8.25, '一段比较长的实际配音，会把短镜头延长。')
        t = p.compile_timeline(self.root, True)
        s = t['scenes'][0]
        self.assertGreater(t['durationSeconds'], 8.25)
        self.assertLessEqual(s['voiceStartFrame'] + s['voiceFrames'], s['endFrame'])
        self.assertTrue(all(0 <= c['startFrame'] < c['endFrame'] <= s['endFrame'] for c in t['captions']))

    def test_missing_voice_fails_only_on_lock(self):
        self.c['scenes'][0]['narration'] = '缺配音'
        self.save()
        self.assertFalse(p.compile_timeline(self.root)['locked'])
        with self.assertRaisesRegex(ValueError, '缺少旁白'):
            p.compile_timeline(self.root, True)

    def test_changed_text_rejects_cached_voice(self):
        self.voice(2)
        self.c['scenes'][0]['narration'] = '另一段台词'
        self.save()
        with self.assertRaisesRegex(ValueError, '缓存'):
            p.compile_timeline(self.root, True)

    def test_changed_audio_rejects_cache(self):
        file = self.voice(2)
        file.write_bytes(file.read_bytes() + b'changed')
        with self.assertRaisesRegex(ValueError, '缓存'):
            p.compile_timeline(self.root, True)

    def test_limit_rejects_instead_of_truncating(self):
        self.voice(8)
        self.c['maxSeconds'] = 5
        self.save()
        with self.assertRaisesRegex(ValueError, '不能裁切'):
            p.compile_timeline(self.root, True)

    def test_stale_timeline_is_rejected(self):
        p.write(self.root / 'assets.json', {'schema': 'code-animation-assets/v1', 'assets': [], 'links': []})
        p.asset_review.seal(self.root)
        self.c = p.read(self.root / 'film.json')
        p.write(self.root / 'timeline.json', p.compile_timeline(self.root, True))
        self.c['scenes'][0]['visualSeconds'] = 6
        self.save()
        with self.assertRaisesRegex(ValueError, '过期'):
            p.locked(self.root)

    def test_scene_ids_and_dimensions_validated(self):
        original = copy.deepcopy(self.c)
        self.c['scenes'] *= 2
        self.save()
        with self.assertRaises(ValueError): p.compile_timeline(self.root)
        self.c = original
        self.c['width'] = 641
        self.save()
        with self.assertRaises(ValueError): p.compile_timeline(self.root)

    def test_frame_boundaries_contiguous_at_fractional_seconds(self):
        self.c['scenes'] = [{'id': f'shot-{i}', 'visualSeconds': v, 'narration': ''}
                            for i, v in enumerate([1.234, 3.456, 7.891])]
        self.save()
        t = p.compile_timeline(self.root, True)
        self.assertEqual(t['scenes'][-1]['endFrame'], t['totalFrames'])
        for a, b in zip(t['scenes'], t['scenes'][1:]): self.assertEqual(a['endFrame'], b['startFrame'])

    def test_music_cannot_cross_end_of_video(self):
        self.voice(4)
        self.c['scenes'][0]['narration'] = ''
        self.c['audioTracks'] = [{'file': 'audio/one.wav', 'startSeconds': 1}]
        self.save()
        with self.assertRaisesRegex(ValueError, '片尾'):
            p.compile_timeline(self.root, True)

    def test_external_voice_requires_content_review(self):
        file = self.voice(2)
        file.with_suffix('.wav.json').unlink()
        with self.assertRaisesRegex(ValueError, '核对台词'):
            p.compile_timeline(self.root, True)
        self.c['scenes'][0]['externalVoiceVerified'] = True
        self.save()
        self.assertTrue(p.compile_timeline(self.root, True)['locked'])

    def test_nan_and_outside_asset_paths_are_rejected(self):
        self.c['scenes'][0]['visualSeconds'] = math.nan
        self.save()
        with self.assertRaises(ValueError): p.compile_timeline(self.root)
        with self.assertRaises(ValueError): p.local(self.root, '../outside.wav')


if __name__ == '__main__': unittest.main()
