import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "prepare-csdn-markdown.py"


class PrepareCsdnMarkdownTests(unittest.TestCase):
    def run_script(self, source_text: str, *args: str):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "source.md"
            output = tmp_path / "output"
            source.write_text(source_text, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(source), "--output-dir", str(output), *args],
                text=True,
                capture_output=True,
                check=False,
            )
            article = (output / "article.csdn.md").read_text(encoding="utf-8") if output.exists() else None
            manifest = (
                json.loads((output / "manifest.json").read_text(encoding="utf-8"))
                if (output / "manifest.json").exists()
                else None
            )
            return result, article, manifest

    def test_strips_frontmatter_and_duplicate_h1(self):
        result, article, manifest = self.run_script(
            "---\ntitle: CSDN 渠道发布指南\nauthor: test\n---\n# CSDN 渠道发布指南\n\n正文内容。\n"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(article, "正文内容。\n")
        self.assertTrue(manifest["stripped_frontmatter"])
        self.assertTrue(manifest["stripped_duplicate_h1"])
        self.assertTrue(manifest["publish_ready"])

    def test_local_image_blocks_publish_readiness(self):
        result, _, manifest = self.run_script(
            "# 一篇完整的技术文章\n\n![架构图](./missing.png)\n"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(manifest["publish_ready"])
        self.assertEqual(len(manifest["local_images"]), 1)
        self.assertEqual(len(manifest["missing_images"]), 1)
        self.assertIn("local_images_require_verified_csdn_upload", manifest["blocking_reasons"])

    def test_multiline_markdown_uses_verified_browser_injection_probe(self):
        result, _, manifest = self.run_script(
            "# CSDN 多段文章测试\n\n第一段。\n\n## 小标题\n\n第二段。\n"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(manifest["direct_fill_ready"])
        self.assertTrue(manifest["browser_injection_ready"])
        self.assertTrue(manifest["automation_candidate"])
        self.assertFalse(manifest["publish_ready"])
        self.assertEqual(manifest["browser_entry_mode"], "browser_injection_probe")
        self.assertIn(
            "multiline_markdown_requires_verified_browser_injection",
            manifest["warnings"],
        )

    def test_single_paragraph_is_ready_for_direct_fill(self):
        result, _, manifest = self.run_script(
            "# CSDN 单段正文测试\n\n这是一段可以直接写入编辑器的测试正文。\n"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(manifest["direct_fill_ready"])
        self.assertFalse(manifest["browser_injection_ready"])
        self.assertTrue(manifest["automation_candidate"])
        self.assertTrue(manifest["publish_ready"])
        self.assertEqual(manifest["browser_entry_mode"], "direct_fill")

    def test_rejects_short_title(self):
        result, article, manifest = self.run_script("# 短题\n\n正文。\n")
        self.assertEqual(result.returncode, 2)
        self.assertIsNone(article)
        self.assertIsNone(manifest)
        self.assertIn("5～100", result.stderr)


if __name__ == "__main__":
    unittest.main()
