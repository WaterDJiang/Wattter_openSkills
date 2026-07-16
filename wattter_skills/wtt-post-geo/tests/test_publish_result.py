import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "publish-result.py"


class PublishResultTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.ledger = Path(self.temporary.name) / "publish-results.json"

    def run_cli(self, *args: str):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def init(self, platforms: str = "zhihu,xiaohongshu"):
        result = self.run_cli("init", "--file", str(self.ledger), "--platforms", platforms)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_summary_contains_required_three_columns_and_all_platforms(self):
        self.init()
        published = self.run_cli(
            "update",
            "--file",
            str(self.ledger),
            "--platform",
            "zhihu",
            "--status",
            "published",
            "--write-state",
            "published_verified",
            "--provider",
            "opencli_ui",
            "--item-id",
            "123",
            "--link",
            "https://zhuanlan.zhihu.com/p/123",
        )
        self.assertEqual(published.returncode, 0, published.stderr)
        filled = self.run_cli(
            "update",
            "--file",
            str(self.ledger),
            "--platform",
            "xiaohongshu",
            "--status",
            "filled",
            "--write-state",
            "unknown",
            "--detail",
            "6 图草稿存在，正文无法回读",
        )
        self.assertEqual(filled.returncode, 0, filled.stderr)

        summary = self.run_cli("summary", "--file", str(self.ledger), "--strict")
        self.assertEqual(summary.returncode, 0, summary.stderr)
        self.assertIn("| 平台 | 完成情况 | 链接 |", summary.stdout)
        self.assertIn("| 知乎 | 已发布 | [打开](https://zhuanlan.zhihu.com/p/123) |", summary.stdout)
        self.assertIn("| 小红书 | 已填写待确认：6 图草稿存在，正文无法回读 | — |", summary.stdout)
        data = json.loads(self.ledger.read_text(encoding="utf-8"))
        self.assertEqual(data["task_status"], "partial")

    def test_published_requires_verified_state_and_link(self):
        self.init("twitter")
        result = self.run_cli(
            "update",
            "--file",
            str(self.ledger),
            "--platform",
            "twitter",
            "--status",
            "published",
            "--write-state",
            "published_unverified",
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("不允许 write_state", result.stderr)

    def test_strict_summary_rejects_pending_platform(self):
        self.init("weibo")
        result = self.run_cli("summary", "--file", str(self.ledger), "--strict")
        self.assertEqual(result.returncode, 2)
        self.assertIn("仍有平台未记录最终状态", result.stderr)

    def test_verified_draft_cannot_be_replaced_by_another_draft(self):
        self.init("juejin")
        first = self.run_cli(
            "update",
            "--file",
            str(self.ledger),
            "--platform",
            "juejin",
            "--status",
            "draft",
            "--write-state",
            "created_verified",
            "--link",
            "https://juejin.cn/editor/drafts/1",
        )
        self.assertEqual(first.returncode, 0, first.stderr)
        second = self.run_cli(
            "update",
            "--file",
            str(self.ledger),
            "--platform",
            "juejin",
            "--status",
            "draft",
            "--write-state",
            "created_verified",
            "--link",
            "https://juejin.cn/editor/drafts/2",
        )
        self.assertEqual(second.returncode, 2)
        self.assertIn("拒绝替换", second.stderr)

    def test_attempt_records_timing_state_and_fallback_reason(self):
        self.init("juejin")
        started = self.run_cli(
            "attempt-start",
            "--file", str(self.ledger),
            "--platform", "juejin",
            "--provider", "opencli_login_adapter",
            "--attempt-id", "juejin-1",
        )
        self.assertEqual(started.returncode, 0, started.stderr)
        finished = self.run_cli(
            "attempt-finish",
            "--file", str(self.ledger),
            "--platform", "juejin",
            "--attempt-id", "juejin-1",
            "--status", "failed",
            "--write-state", "confirmed_not_created",
            "--fallback-reason", "adapter_endpoint_drift",
            "--error", "HTTP 404",
            "--evidence", "draft list unchanged",
        )
        self.assertEqual(finished.returncode, 0, finished.stderr)
        data = json.loads(self.ledger.read_text(encoding="utf-8"))
        attempt = data["platforms"]["juejin"]["attempts"][0]
        self.assertEqual(attempt["status"], "failed")
        self.assertEqual(attempt["write_state"], "confirmed_not_created")
        self.assertEqual(attempt["fallback_reason"], "adapter_endpoint_drift")
        self.assertIsInstance(attempt["duration_ms"], int)
        self.assertIsNotNone(attempt["finished_at"])
        self.assertEqual(data["platforms"]["juejin"]["fallback_reason"], "adapter_endpoint_drift")


if __name__ == "__main__":
    unittest.main()
