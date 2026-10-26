"""配置可迁移性、私人资源排除与模型/输出失败边界；不下载权重。"""
import argparse
import importlib.util
import json
import tempfile
import hashlib
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


v = load('voice', ROOT / 'scripts/voice.py')
p = load('pipeline', ROOT / 'scripts/pipeline.py')


class VoiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        self.file = self.root / 'voice.local.json'
        self.c = v.read(ROOT / 'config/voice.example.json')
        self.c['voices']['my-voice']['referenceTextVerified'] = True
        self.save()

    def tearDown(self):
        self.tmp.cleanup()

    def save(self):
        v.write(self.file, self.c)

    def doctor_fixture(self):
        model, manifest, _ = self.make_model()
        self.c['models']['qwen3-tts-1.7b-base-mlx'] = {'path': str(model), 'manifest': str(manifest)}
        folder=self.root/'voices/my-voice';folder.mkdir(parents=True)
        (folder/'reference.wav').write_bytes(b'fixture-not-decoded-by-doctor')
        (folder/'reference.txt').write_text('PRIVATE REFERENCE CONTENT')
        self.save()
        return model, folder

    def test_doctor_missing_config_prompts_without_creating_files(self):
        with self.discovery_context():
            before=set(self.root.rglob('*'));report=v.doctor(self.root)
            self.assertEqual(report['status'],'missing-config')
            self.assertIn('模板',report['issues'][0]);self.assertEqual(before,set(self.root.rglob('*')))

    def test_doctor_complete_config_is_lightweight_and_hides_reference_text(self):
        self.doctor_fixture()
        with patch.object(v,'sha',side_effect=AssertionError('no large-model hashing')),patch.object(v.subprocess,'check_output',side_effect=AssertionError('no inference/ffprobe')):
            report=v.doctor(self.root,self.file)
        self.assertEqual(report['status'],'configured-unverified')
        self.assertTrue(report['modelFilesPresent']);self.assertTrue(report['customVoiceFilesPresent'])
        self.assertNotIn('PRIVATE REFERENCE CONTENT',json.dumps(report))
        self.assertEqual(report['fullValidation'],'not-run')

    def test_doctor_model_missing_reports_separate_voice_status(self):
        model,_=self.doctor_fixture();(model/'model.safetensors').unlink()
        report=v.doctor(self.root,self.file)
        self.assertEqual(report['status'],'needs-setup');self.assertFalse(report['modelFilesPresent'])
        self.assertTrue(report['customVoiceFilesPresent']);self.assertIn('模型',report['issues'][0])

    def test_doctor_unverified_transcript_and_missing_reference_are_reported(self):
        _,folder=self.doctor_fixture();(folder/'reference.wav').unlink();(folder/'reference.txt').write_text('')
        self.c['voices']['my-voice']['referenceTextVerified']=False;self.save()
        report=v.doctor(self.root,self.file)
        self.assertTrue(report['modelFilesPresent']);self.assertFalse(report['customVoiceFilesPresent'])
        text=' '.join(report['issues'])
        self.assertIn('参考录音',text);self.assertIn('文本为空',text);self.assertIn('referenceTextVerified',text)

    def test_doctor_invalid_or_missing_default_returns_advisory(self):
        for content in ('{','[]','{}',json.dumps(dict(self.c,defaultVoice='absent'))):
            with self.subTest(content=content):
                self.file.write_text(content)
                self.assertEqual(v.doctor(self.root,self.file)['status'],'needs-setup')

    def test_doctor_respects_invalid_explicit_priority(self):
        self.doctor_fixture();self.put_default(self.root/'home/.config/wtt-code-animation-studio')
        with self.discovery_context():
            report=v.doctor(self.root,self.root/'missing.json')
        self.assertEqual(report['status'],'needs-setup');self.assertIn('指定的声音配置不存在',report['issues'][0])

    def test_init_checks_voice_and_prompts_without_writing_private_config(self):
        import contextlib,io
        with self.discovery_context(),contextlib.redirect_stdout(io.StringIO()) as log:
            p.init(self.root/'new-film')
        self.assertIn('声音首次检查',log.getvalue());self.assertIn('尚未发现',log.getvalue())
        self.assertFalse((self.root/'new-film/.voice-local').exists())

    def test_paths_relative_to_configuration_not_cwd(self):
        config = v.load_config(self.file)
        self.assertEqual(config['referenceAudio'], self.root/'voices/my-voice/reference.wav')

    def test_second_voice_shares_model_but_has_own_reference(self):
        self.c['voices']['second'] = dict(self.c['voices']['my-voice'], referenceAudio='voices/second.wav')
        self.save()
        a, b = v.load_config(self.file), v.load_config(self.file, 'second')
        self.assertEqual(a['modelPath'], b['modelPath'])
        self.assertNotEqual(a['referenceAudio'], b['referenceAudio'])

    def discovery_context(self):
        from contextlib import ExitStack
        stack = ExitStack()
        stack.enter_context(patch.dict('os.environ', {}, clear=True))
        stack.enter_context(patch.object(v.Path, 'home', return_value=self.root/'home'))
        stack.enter_context(patch.dict('sys.modules', {'voice': v}))
        return stack

    def put_default(self, base):
        file = base / 'voice.local.json'
        file.parent.mkdir(parents=True, exist_ok=True)
        v.write(file, self.c)
        return file

    def test_discovery_priority_explicit_environment_project_user(self):
        global_file = self.put_default(self.root/'home/.config/wtt-code-animation-studio')
        with self.discovery_context():
            self.assertEqual(v.discover_config(self.root), global_file)
            project = self.put_default(self.root/'.voice-local')
            self.assertEqual(v.discover_config(self.root), project)
            with patch.dict('os.environ', {'CODE_ANIMATION_VOICE_CONFIG': str(self.file)}):
                self.assertEqual(v.discover_config(self.root), self.file)
                self.assertEqual(v.discover_config(self.root, global_file), global_file)

    def test_user_default_is_available_to_new_projects(self):
        config = self.put_default(self.root/'home/.config/wtt-code-animation-studio')
        with self.discovery_context():
            for project in ('project-a', 'project-b'):
                self.assertEqual(v.discover_config(self.root/project), config)

    def test_invalid_higher_priority_never_falls_back(self):
        self.put_default(self.root/'home/.config/wtt-code-animation-studio')
        with self.discovery_context():
            with patch.dict('os.environ', {'CODE_ANIMATION_VOICE_CONFIG': str(self.root/'missing')}):
                with self.assertRaisesRegex(ValueError, '不存在'):
                    v.discover_config(self.root)
            broken = self.root/'.voice-local/voice.local.json'
            broken.parent.mkdir(); broken.symlink_to(self.root/'missing')
            with self.assertRaisesRegex(ValueError, '不可读取'):
                v.discover_config(self.root)

    def test_auto_tts_uses_default_voice_without_system_tts(self):
        config = self.put_default(self.root/'.voice-local')
        with self.discovery_context(), patch.object(p, 'run') as run, patch.object(p, 'tts') as system:
            p.default_tts(self.root)
            command = run.call_args.args[0]
            self.assertEqual(command[command.index('--voice')+1], 'my-voice')
            self.assertEqual(command[command.index('--config')+1], config)
            system.assert_not_called()

    def test_explicit_system_voice_overrides_even_broken_default(self):
        file = self.put_default(self.root/'.voice-local'); file.write_text('broken')
        with self.discovery_context(), patch.object(p, 'tts') as system:
            p.default_tts(self.root, system_voice='Tingting', rate=180)
            system.assert_called_once_with(self.root, 'Tingting', 180)

    def test_no_configuration_retains_original_fallback(self):
        with self.discovery_context(), patch.object(p, 'tts') as system:
            p.default_tts(self.root)
            system.assert_called_once_with(self.root, 'Tingting', 205)

    def test_malformed_config_or_missing_default_fails_without_system_fallback(self):
        file = self.put_default(self.root/'.voice-local')
        with self.discovery_context(), patch.object(p, 'tts') as system:
            file.write_text('broken')
            with self.assertRaises(ValueError): p.default_tts(self.root)
            self.c['defaultVoice'] = 'missing'; v.write(file, self.c)
            with self.assertRaisesRegex(ValueError, '未配置音色'): p.default_tts(self.root)
            system.assert_not_called()

    def test_explicit_clone_voice_overrides_default_and_uses_adjacent_environment(self):
        self.c['voices']['second'] = dict(self.c['voices']['my-voice'])
        config = self.put_default(self.root/'.voice-local')
        python = config.parent/'.venv/bin/python'; python.parent.mkdir(parents=True); python.touch()
        with self.discovery_context(), patch.object(p, 'run') as run:
            p.default_tts(self.root, voice_id='second')
            command = run.call_args.args[0]
            self.assertEqual(command[0], python)
            self.assertEqual(command[command.index('--voice')+1], 'second')

    def test_conflicting_voice_arguments_and_unsupported_clone_rate_fail(self):
        self.put_default(self.root/'.voice-local')
        with self.discovery_context():
            with self.assertRaisesRegex(ValueError, '不能与'):
                p.default_tts(self.root, system_voice='Tingting', voice_id='my-voice')
            with self.assertRaisesRegex(ValueError, '不支持'):
                p.default_tts(self.root, rate=200)

    def test_reference_text_must_be_explicitly_verified(self):
        self.c['voices']['my-voice']['referenceTextVerified'] = False
        self.save()
        with self.assertRaisesRegex(ValueError, '核对'):
            v.load_config(self.file)

    def test_unknown_voice_and_model_fail(self):
        with self.assertRaisesRegex(ValueError, '未配置音色'):
            v.load_config(self.file, 'absent')
        self.c['voices']['my-voice']['model'] = 'not-a-model'
        self.save()
        with self.assertRaisesRegex(ValueError, '未知模型'):
            v.load_config(self.file)

    def test_asr_model_is_not_a_voice(self):
        self.c['voices']['my-voice']['model'] = 'whisper-small-mlx'
        self.save()
        with self.assertRaisesRegex(ValueError, '不是已接入'):
            v.load_config(self.file)

    def test_url_reference_is_rejected(self):
        self.c['voices']['my-voice']['referenceAudio'] = 'https://example.org/voice.wav'
        self.save()
        with self.assertRaisesRegex(ValueError, '本地路径'):
            v.load_config(self.file)

    def test_unsupported_controls_and_invalid_numbers_fail(self):
        for key, value in [('speed', 1.2), ('temperature', float('nan')), ('maxTokens', True), ('seed', -1)]:
            self.c['generation'] = {key: value}
            self.save()
            with self.subTest(key=key), self.assertRaises(ValueError):
                v.load_config(self.file)

    def make_model(self):
        model = self.root / 'model'
        names = ['config.json', 'tokenizer_config.json', 'speech_tokenizer/config.json',
                 'model.safetensors', 'speech_tokenizer/model.safetensors']
        files = []
        for name in names:
            f = model / name
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text('{}')
            files.append({'file': name, 'bytes': 2, 'sha256': v.sha(f)})
        entry = v.catalog('qwen3-tts-1.7b-base-mlx')
        manifest = model / 'model-manifest.json'
        v.write(manifest, {'repo': entry['repo'], 'revision': entry['revision'], 'files': files})
        return model, manifest, entry

    def test_hash_tampering_is_rejected(self):
        model, manifest, entry = self.make_model()
        self.assertEqual(v.verify_model(model, manifest, entry), 5)
        (model / 'model.safetensors').write_text('[]')
        with self.assertRaisesRegex(ValueError, '哈希'):
            v.verify_model(model, manifest, entry)

    def test_unlisted_file_and_wrong_revision_are_rejected(self):
        model, manifest, entry = self.make_model()
        extra = model / 'unexpected.json'
        extra.write_text('{}')
        with self.assertRaisesRegex(ValueError, '清单之外'):
            v.verify_model(model, manifest, entry)
        extra.unlink()
        data = v.read(manifest); data['revision'] = 'main'; v.write(manifest, data)
        with self.assertRaisesRegex(ValueError, 'revision'):
            v.verify_model(model, manifest, entry)

    def test_manifest_cannot_escape_model_directory(self):
        model, manifest, entry = self.make_model()
        outside = self.root / 'outside'
        outside.write_text('{}')
        data = v.read(manifest)
        data['files'].append({'file': '../outside', 'bytes': 2, 'sha256': v.sha(outside)})
        v.write(manifest, data)
        with self.assertRaisesRegex(ValueError, '目录内'):
            v.verify_model(model, manifest, entry)

    def test_missing_encoder_is_rejected(self):
        model, manifest, entry = self.make_model()
        data = v.read(manifest); data['files'] = data['files'][:-1]; v.write(manifest, data)
        with self.assertRaisesRegex(ValueError, '编解码权重'):
            v.verify_model(model, manifest, entry)

    def test_existing_audio_cannot_be_overwritten(self):
        text, out = self.root/'input.txt', self.root/'take.wav'
        text.write_text('一段新文案')
        args = argparse.Namespace(project=None, text_file=text, out=out)
        self.assertEqual(len(v.jobs_for(args)), 1)
        out.write_bytes(b'previous')
        with self.assertRaisesRegex(ValueError, '已存在'):
            v.jobs_for(args)
        self.assertEqual(out.read_bytes(), b'previous')

    def test_unsupported_platform_stops_before_model_loading(self):
        with patch.object(v.platform, 'system', return_value='Linux'):
            with self.assertRaisesRegex(ValueError, 'Apple Silicon'):
                v.check(v.load_config(self.file))

    def test_init_contains_portable_voice_tools_and_no_personal_configuration(self):
        project = self.root / 'film'
        p.init(project)
        for name in ('tools/voice.py', 'config/model-catalog.json', 'config/voice.example.json',
                     'VOICE.md', 'requirements-voice.txt', '.gitignore'):
            self.assertTrue((project/name).is_file())
        self.assertFalse((project/'voice.local.json').exists())
        self.assertFalse((project/'.voice-local').exists())

    def test_download_pins_revision_checks_hash_and_reuses_existing_files(self):
        entry = v.catalog('whisper-small-mlx')
        payload = b'public model test fixture'
        item = types.SimpleNamespace(rfilename='model.safetensors', size=len(payload),
                                     lfs=types.SimpleNamespace(sha256=hashlib.sha256(payload).hexdigest()))
        info = types.SimpleNamespace(sha=entry['revision'], siblings=[item])
        from unittest.mock import Mock
        api = Mock(); api.model_info.return_value = info
        def snapshot_download(**kwargs):
            self.assertEqual(kwargs['revision'], entry['revision'])
            dest = kwargs['local_dir']; dest.mkdir(parents=True)
            (dest/item.rfilename).write_bytes(payload)
        download = Mock(side_effect=snapshot_download)
        hub = types.SimpleNamespace(HfApi=lambda: api, snapshot_download=download)
        with patch.dict('sys.modules', {'huggingface_hub': hub}):
            first = v.download(entry['id'], self.root)
            self.assertFalse(first['reusedVerifiedFiles'])
            second = v.download(entry['id'], self.root)
            self.assertTrue(second['reusedVerifiedFiles'])
            self.assertEqual(download.call_count, 1)
            api.model_info.assert_called_with(entry['repo'], revision=entry['revision'], files_metadata=True)
            item.lfs.sha256 = '0'*64
            download.side_effect = None
            with self.assertRaisesRegex(ValueError, 'SHA256'):
                v.download(entry['id'], self.root)


if __name__ == '__main__':
    unittest.main()
