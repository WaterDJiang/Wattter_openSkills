import json
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "provider-preflight.py"

SPEC = importlib.util.spec_from_file_location("provider_preflight", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class ProviderPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        base = Path(self.temporary.name)
        self.registry = base / "registry.json"
        commands = [
            "weibo/publish", "weibo/article-draft", "zhihu/article-draft", "juejin/article-draft",
            "baijiahao/article-draft", "cnblogs/article-draft",
        ]
        self.registry.write_text(json.dumps([{"command": command} for command in commands]), encoding="utf-8")
        self.doctor = base / "doctor.txt"
        self.doctor.write_text("[OK] Connectivity: connected\nEverything looks good!\n", encoding="utf-8")

    def run_cli(self, *args: str):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args, "--registry-file", str(self.registry), "--doctor-file", str(self.doctor)],
            text=True, capture_output=True, check=False,
        )

    def test_selects_short_post_for_weibo_and_login_adapters_for_articles(self):
        result = self.run_cli("--platforms", "zhihu,juejin,baijiahao,cnblogs,weibo")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertFalse(data["extension_required"])
        weibo = data["platforms"]["weibo"]
        self.assertEqual(weibo["variant"], "short_post")
        self.assertEqual(weibo["selected_provider"], "opencli_adapter")
        self.assertEqual(weibo["selected_command"], "weibo/publish")
        for platform in ("zhihu", "juejin", "baijiahao", "cnblogs"):
            self.assertEqual(data["platforms"][platform]["selected_provider"], "opencli_login_adapter")

    def test_explicit_weibo_longform_selects_article_draft(self):
        result = self.run_cli("--platforms", "weibo", "--weibo-variant", "longform")
        self.assertEqual(result.returncode, 0, result.stderr)
        row = json.loads(result.stdout)["platforms"]["weibo"]
        self.assertEqual(row["variant"], "longform")
        self.assertEqual(row["selected_provider"], "opencli_login_adapter")
        self.assertEqual(row["selected_command"], "weibo/article-draft")

    def test_explicit_weibo_longform_never_downgrades_to_short_post(self):
        self.registry.write_text(json.dumps([{"command": "weibo/publish"}]), encoding="utf-8")
        result = self.run_cli("--platforms", "weibo", "--weibo-variant", "longform")
        self.assertEqual(result.returncode, 0, result.stderr)
        row = json.loads(result.stdout)["platforms"]["weibo"]
        self.assertEqual(row["selected_provider"], "opencli_ui")
        self.assertIn("card.weibo.com", row["selected_command"])
        self.assertEqual(row["fallback_reason"], "adapter_not_registered")

    def test_required_images_fast_falls_back_to_ui(self):
        result = self.run_cli("--platforms", "zhihu", "--require-images", "zhihu")
        self.assertEqual(result.returncode, 0, result.stderr)
        row = json.loads(result.stdout)["platforms"]["zhihu"]
        self.assertEqual(row["selected_provider"], "opencli_ui")
        self.assertEqual(row["fallback_reason"], "missing_capability:images")

        result = self.run_cli("--platforms", "weibo", "--require-images", "weibo")
        self.assertEqual(result.returncode, 0, result.stderr)
        row = json.loads(result.stdout)["platforms"]["weibo"]
        self.assertEqual(row["selected_provider"], "opencli_ui")
        self.assertEqual(row["fallback_reason"], "missing_capability:images")

    def test_missing_adapter_fast_falls_back_to_ui(self):
        self.registry.write_text("[]", encoding="utf-8")
        result = self.run_cli("--platforms", "juejin")
        self.assertEqual(result.returncode, 0, result.stderr)
        row = json.loads(result.stdout)["platforms"]["juejin"]
        self.assertEqual(row["selected_provider"], "opencli_ui")
        self.assertEqual(row["fallback_reason"], "adapter_not_registered")

    def test_account_identity_supports_builtin_whoami_fields(self):
        self.assertEqual(MODULE.account_name({"screen_name": "Wattter_J", "user_id": "1"}), "Wattter_J")
        self.assertTrue(MODULE.explicitly_unauthenticated({"logged_in": False, "site": "weibo"}))


if __name__ == "__main__":
    unittest.main()
