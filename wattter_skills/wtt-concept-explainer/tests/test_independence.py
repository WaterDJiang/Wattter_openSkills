"""只安装本技能时的初始化、锁时，以及新旧外部音色配置优先级。"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import voice


class IndependenceTests(unittest.TestCase):
    def test_standalone_bundle_initializes_and_locks_without_sibling_skill(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            bundle = base / 'installed' / 'wtt-concept-explainer'
            shutil.copytree(ROOT, bundle, ignore=shutil.ignore_patterns('__pycache__'))
            project = base / 'project'
            env = dict(os.environ, HOME=str(base/'home'), PYTHONDONTWRITEBYTECODE='1')
            env.pop('CONCEPT_EXPLAINER_VOICE_CONFIG', None)
            env.pop('CODE_ANIMATION_VOICE_CONFIG', None)
            def run(*args):
                return subprocess.run([sys.executable, *map(str,args)], cwd=base, env=env,
                                      text=True, capture_output=True, check=True)
            self.assertFalse((bundle.parent/'wtt-code-animation-studio').exists())
            run(bundle/'scripts/pipeline.py', 'init', project)
            for name in ('pipeline.py','voice.py','asset_review.py','render.cjs'):
                self.assertEqual((project/'tools'/name).read_bytes(), (bundle/'scripts'/name).read_bytes())
            run(project/'tools/asset_review.py', 'seal', project)
            run(project/'tools/pipeline.py', 'timeline', project, '--lock')
            run(project/'tools/pipeline.py', 'check', project)
            self.assertTrue(json.loads((project/'timeline.json').read_text())['locked'])
            self.assertFalse(any(p.is_symlink() for p in bundle.rglob('*')))

    def test_new_user_config_precedes_legacy_data_and_project_precedes_user(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {}, clear=True):
            root = Path(temp).resolve()
            old = root/'.config/wtt-code-animation-studio/voice.local.json'
            new = root/'.config/wtt-concept-explainer/voice.local.json'
            local = root/'project/.voice-local/voice.local.json'
            for file in (old,new,local):
                file.parent.mkdir(parents=True,exist_ok=True);file.write_text('{}')
            with patch.object(voice.Path,'home',return_value=root):
                self.assertEqual(voice.discover_config(root/'fresh'),new)
                self.assertEqual(voice.discover_config(root/'project'),local)
                new.unlink()
                self.assertEqual(voice.discover_config(root/'fresh'),old)

    def test_explicit_then_new_environment_and_invalid_new_does_not_fall_back(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();new=root/'new.json';old=root/'old.json'
            new.write_text('{}');old.write_text('{}')
            with patch.dict(os.environ, {'CONCEPT_EXPLAINER_VOICE_CONFIG':str(new),
                                         'CODE_ANIMATION_VOICE_CONFIG':str(old)}, clear=True):
                self.assertEqual(voice.discover_config(root),new)
                self.assertEqual(voice.discover_config(root,old),old)
                new.unlink()
                with self.assertRaisesRegex(ValueError,'不存在'):
                    voice.discover_config(root)


if __name__ == '__main__': unittest.main()
