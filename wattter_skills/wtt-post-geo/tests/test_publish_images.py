import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "select-publish-image.py"


class PublishImageTests(unittest.TestCase):
    def run_cli(self, *args: str):
        return subprocess.run([sys.executable, str(SCRIPT), *args], text=True, capture_output=True, check=False)

    def test_bundled_images_match_manifest(self):
        manifest = json.loads((ROOT / "assets" / "default-images" / "manifest.json").read_text(encoding="utf-8"))
        for profile in manifest["assets"].values():
            path = ROOT / "assets" / "default-images" / profile["file"]
            with Image.open(path) as image:
                self.assertEqual(image.size, (profile["width"], profile["height"]))

    def test_missing_preferred_uses_bundled_default(self):
        result = self.run_cli("--use-case", "weixin_cover", "--preferred", "/missing/article-cover.png")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["source"], "bundled_default")
        self.assertEqual((data["width"], data["height"]), (900, 383))
        self.assertEqual(data["fallback_reason"], "preferred_missing")

    def test_exact_size_preferred_wins(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "cover.png"
            Image.new("RGB", (900, 383), "white").save(path)
            result = self.run_cli("--use-case", "weixin_cover", "--preferred", str(path))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["source"], "article_specific")


if __name__ == "__main__":
    unittest.main()
