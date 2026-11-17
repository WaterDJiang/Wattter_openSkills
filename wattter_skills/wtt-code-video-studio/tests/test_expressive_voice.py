"""声音身份/表演能力/缓存边界，不用假合成替代真实听样。"""
import argparse
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / 'scripts'))
import voice as v
import speech


class ExpressiveVoiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        self.file = self.root / 'voice.local.json'
        self.config = {
            'schema': 'code-animation-voice/v1', 'defaultVoice': 'mine',
            'models': {
                'qwen3-tts-1.7b-base-mlx': {'path': 'base', 'manifest': 'base-manifest.json'},
                'qwen3-tts-1.7b-customvoice-mlx': {'path': 'custom', 'manifest': 'custom-manifest.json'}},
            'voices': {
                'mine': {'model': 'qwen3-tts-1.7b-base-mlx', 'referenceAudio': 'ref.wav',
                         'referenceTextFile': 'ref.txt', 'referenceTextVerified': True},
                'girl': {'model': 'qwen3-tts-1.7b-customvoice-mlx', 'speaker': 'Vivian'},
                'man': {'model': 'qwen3-tts-1.7b-customvoice-mlx', 'speaker': 'uncle_fu'}},
            'generation': {'seed': 42, 'temperature': .7, 'maxTokens': 1200}}
        for name in ['base-manifest.json', 'custom-manifest.json']:
            (self.root/name).write_text('{}')
        self.save()
        self.verified = {'referenceAudioSha256': None, 'referenceTextSha256': None}
        self.job = dict(id='girl-ask', speakerId='girl', voiceId='girl', text='是你吗？',
                        voice='audio/girl.wav', out=self.root/'girl.wav', projectRoot=None,
                        performance={'instruct': '轻声疑问', 'intent': '确认'},
                        pauseAfterSeconds=.2, externalVoiceVerified=False, legacy=False)

    def tearDown(self):
        self.tmp.cleanup()

    def save(self):
        self.file.write_text(json.dumps(self.config))

    def request(self, job=None):
        return v.prepare_job(v.load_config(self.file, 'girl'), job or self.job, self.verified)

    def test_custom_voice_uses_preset_without_private_reference(self):
        c = v.load_config(self.file, 'girl')
        self.assertEqual(c['variant'], 'custom_voice')
        self.assertEqual(c['speaker'], 'vivian')
        self.assertNotIn('referenceAudio', c)
        self.assertNotIn('referenceTextFile', c)

    def test_unknown_preset_and_mixed_reference_fields_fail(self):
        self.config['voices']['girl']['speaker'] = 'made-up'
        self.save()
        with self.assertRaisesRegex(ValueError, 'speaker'):
            v.load_config(self.file, 'girl')
        self.config['voices']['girl']['speaker'] = 'vivian'
        self.config['voices']['girl']['referenceAudio'] = 'ref.wav'
        self.save()
        with self.assertRaisesRegex(ValueError, '不支持'):
            v.load_config(self.file, 'girl')

    def test_base_cannot_silently_ignore_instruct(self):
        c = v.load_config(self.file)
        with self.assertRaisesRegex(ValueError, '不支持 instruct'):
            v.prepare_job(c, self.job, self.verified)

    def test_default_personal_voice_remains_base(self):
        c = v.load_config(self.file)
        self.assertEqual(c['voiceId'], 'mine')
        self.assertEqual(c['variant'], 'base')
        self.assertEqual(c['referenceAudio'], self.root/'ref.wav')

    def test_performance_and_identity_change_request_fingerprint(self):
        _, original = self.request()
        for field, value in [('performance', {'instruct': '开心地回答'}),
                             ('text', '太好了！'), ('speakerId', 'other'), ('voiceId', 'man')]:
            changed = copy.deepcopy(self.job); changed[field] = value
            with self.subTest(field=field):
                self.assertNotEqual(self.request(changed)[1], original)

    def test_pause_and_output_path_do_not_regenerate_spoken_audio(self):
        changed = dict(self.job, pauseAfterSeconds=2, voice='elsewhere.wav', out=self.root/'elsewhere.wav')
        self.assertEqual(self.request()[1], self.request(changed)[1])

    def test_stable_utterance_id_seed_is_independent_of_list_position(self):
        first = self.request()[0]['generation']['seed']
        self.assertEqual(first, speech.utterance_seed(42, 'girl-ask'))
        other = dict(self.job, id='inserted')
        self.request(other)
        self.assertEqual(first, self.request()[0]['generation']['seed'])

    def test_declared_default_voice_stays_none_in_speech_fingerprint(self):
        job = dict(self.job, voiceId=None)
        request, _ = self.request(job)
        self.assertEqual(request['speechRequestSha256'], speech.request_fingerprint(job))
        self.assertEqual(request['voiceId'], 'girl')

    def test_reuse_requires_full_request_and_actual_file_hash(self):
        _, fingerprint = self.request()
        out = self.job['out']; out.write_bytes(b'existing-original')
        v.write(out.with_suffix('.wav.json'), {'synthesisRequestSha256': fingerprint,
                                              'audioSha256': v.sha(out), 'durationSeconds': 1})
        self.assertTrue(v.reusable(self.job, fingerprint))
        with self.assertRaisesRegex(ValueError, '指纹'):
            v.reusable(self.job, '0'*64)
        out.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, '指纹'):
            v.reusable(self.job, fingerprint)

    def test_v1_record_is_not_falsely_accepted_as_full_new_request(self):
        self.job['out'].write_bytes(b'old')
        v.write(self.job['out'].with_suffix('.wav.json'), {'text': self.job['text'],
                                                        'audioSha256': v.sha(self.job['out'])})
        with self.assertRaisesRegex(ValueError, '旧记录'):
            v.reusable(self.job, self.request()[1])

    def test_reused_jobs_do_not_load_gpu_models(self):
        c = v.load_config(self.file, 'girl')
        _, fingerprint = self.request()
        self.job['out'].write_bytes(b'cached-audio')
        v.write(self.job['out'].with_suffix('.wav.json'), {'synthesisRequestSha256': fingerprint,
                'audioSha256': v.sha(self.job['out']), 'durationSeconds': 1.2})
        with patch.object(v, 'check', return_value=self.verified):
            result = v.synthesize(c, [self.job])
        self.assertTrue(result[0]['reused'])

    def test_custom_doctor_does_not_ask_for_unnecessary_recording(self):
        self.config['defaultVoice'] = 'girl'; self.save()
        with patch.object(v, 'verify_model', return_value=14):
            report = v.doctor(self.root, self.file)
        self.assertEqual(report['status'], 'configured-unverified')
        self.assertTrue(report['presetSpeakerPresent'])
        self.assertFalse(report['referenceRequired'])
        self.assertFalse(report['issues'])

    def test_custom_actual_model_type_is_checked(self):
        c = v.load_config(self.file, 'girl'); c['modelPath'].mkdir()
        v.write(c['modelPath']/'config.json', {'tts_model_type': 'base', 'tts_model_size': '1b7'})
        with patch.object(v.platform, 'system', return_value='Darwin'), \
             patch.object(v.platform, 'machine', return_value='arm64'), \
             patch.object(v, 'verify_model', return_value=14):
            with self.assertRaisesRegex(ValueError, '实际1.7B'):
                v.check(c)


if __name__ == '__main__':
    unittest.main()
