import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "browser-editor-payload.py"


class BrowserEditorPayloadTests(unittest.TestCase):
    def build(self, content: str, engine: str = "codemirror5", selector: str = ".CodeMirror"):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        source = root / "body.md"
        output_js = root / "write.js"
        source.write_text(content, encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(source),
                "--engine",
                engine,
                "--selector",
                selector,
                "--output-js",
                str(output_js),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        manifest = json.loads(result.stdout) if result.returncode == 0 else None
        return temporary, result, output_js, manifest

    def test_codemirror_script_overwrites_once_and_matches(self):
        temporary, result, output_js, manifest = self.build(
            "第一段。\n\n## 标题\n\n第二段🙂。\n"
        )
        self.addCleanup(temporary.cleanup)
        self.assertEqual(result.returncode, 0, result.stderr)
        script = output_js.read_text(encoding="utf-8")
        self.assertNotIn("第一段", script)

        node_source = f"""
const fs = require('fs');
const cm = {{ value: '旧正文', setValue(value) {{ this.value = value; }}, getValue() {{ return this.value; }} }};
global.document = {{ querySelector() {{ return {{ CodeMirror: cm }}; }} }};
const result = eval(fs.readFileSync({json.dumps(str(output_js))}, 'utf8'));
console.log(JSON.stringify(result));
"""
        node_result = subprocess.run(
            ["node", "-e", node_source],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(node_result.returncode, 0, node_result.stderr)
        browser_result = json.loads(node_result.stdout)
        self.assertTrue(browser_result["written"])
        self.assertTrue(browser_result["matches"])
        self.assertEqual(browser_result["expectedHash"], manifest["expected_hash"])

    def test_iframe_html_uses_visible_text_fingerprint(self):
        temporary, result, output_js, manifest = self.build(
            "<h2>标题</h2><p>正文 <strong>重点</strong></p><script>bad()</script>",
            engine="iframe-html",
            selector="#ueditor_0",
        )
        self.addCleanup(temporary.cleanup)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(manifest["verification_basis"], "visible_text_without_whitespace")
        self.assertIn("iframe-html", output_js.read_text(encoding="utf-8"))

    def test_empty_source_is_rejected(self):
        temporary, result, _, _ = self.build("")
        self.addCleanup(temporary.cleanup)
        self.assertEqual(result.returncode, 2)
        self.assertIn("不能为空", result.stderr)


if __name__ == "__main__":
    unittest.main()
