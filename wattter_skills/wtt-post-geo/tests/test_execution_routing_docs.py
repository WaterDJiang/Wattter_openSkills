from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ExecutionRoutingDocsTest(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_required_references_exist(self) -> None:
        required = {
            "references/browser-editor-fallback.md",
            "references/execution-routing.md",
            "references/csdn-sync-extension.md",
            "references/login-state-adapters.md",
            "references/result-reporting.md",
            "references/juejin.md",
            "references/baijiahao.md",
            "references/cnblogs.md",
        }
        self.assertEqual([], sorted(path for path in required if not (ROOT / path).is_file()))

    def test_skill_routes_all_supported_platforms(self) -> None:
        skill = self.read("SKILL.md")
        required_links = {
            "references/execution-routing.md",
            "references/browser-editor-fallback.md",
            "references/result-reporting.md",
            "references/csdn-sync-extension.md",
            "references/login-state-adapters.md",
            "references/weixin.md",
            "references/weibo.md",
            "references/zhihu.md",
            "references/csdn.md",
            "references/juejin.md",
            "references/baijiahao.md",
            "references/cnblogs.md",
            "references/xiaohongshu.md",
            "references/twitter.md",
        }
        for link in required_links:
            self.assertIn(link, skill)

        expected_order = "公众号 → 微博 → 知乎 → CSDN → 掘金 → 百家号 → 博客园 → 小红书 → Twitter/X"
        self.assertIn(expected_order, skill)

    def test_payload_contains_execution_state(self) -> None:
        content_format = self.read("references/content-format.md")
        for platform in ("juejin", "baijiahao", "cnblogs"):
            self.assertRegex(content_format, rf"(?m)^\s+- {platform}$")
        for field in (
            "selected_provider",
            "fallback_chain",
            "write_state",
            "circuit_breaker",
            "attempts",
            "verification",
            "fallback_reason",
        ):
            self.assertIn(field, content_format)

    def test_routing_blocks_ambiguous_fallback(self) -> None:
        routing = self.read("references/execution-routing.md")
        for state in (
            "not_started",
            "confirmed_not_created",
            "created_unverified",
            "created_verified",
            "published_unverified",
            "published_verified",
            "unknown",
        ):
            self.assertIn(f"`{state}`", routing)
        self.assertIn("只有确认没有新写入", routing)
        self.assertIn("不得自动回退", routing)

    def test_extension_is_reference_only_and_adapters_require_readback(self) -> None:
        extension = self.read("references/csdn-sync-extension.md")
        self.assertIn("不是 Provider", extension)
        self.assertIn("真实发布任务不加载", extension)
        self.assertIn("不检查 `window.$pluginSyncer.connected`", extension)
        adapters = self.read("references/login-state-adapters.md")
        self.assertIn("created_unverified", adapters)
        self.assertIn("目标平台回读", adapters)
        self.assertIn("WRITE_UNKNOWN", adapters)
        for command in (
            "weibo/article-draft",
            "zhihu/article-draft",
            "juejin/article-draft",
            "baijiahao/article-draft",
            "cnblogs/article-draft",
        ):
            self.assertIn(command, adapters)

    def test_runtime_docs_do_not_route_through_csdn_extension(self) -> None:
        for relative_path in (
            "SKILL.md",
            "README.md",
            "references/execution-routing.md",
            "references/weixin.md",
            "references/weibo.md",
            "references/zhihu.md",
            "references/juejin.md",
            "references/baijiahao.md",
            "references/cnblogs.md",
        ):
            self.assertNotIn("csdn_sync_extension", self.read(relative_path), relative_path)

    def test_platform_references_define_provider_fallback(self) -> None:
        for relative_path in (
            "references/weixin.md",
            "references/weibo.md",
            "references/zhihu.md",
            "references/juejin.md",
            "references/baijiahao.md",
            "references/cnblogs.md",
        ):
            content = self.read(relative_path)
            self.assertIn("Provider", content, relative_path)
            self.assertIn("write_state", content, relative_path)

        weibo = self.read("references/weibo.md")
        self.assertIn("默认设为 `short_post`", weibo)
        self.assertIn("weibo/body.txt", weibo)
        self.assertIn("publish-output/<run-id>/", weibo)
        self.assertIn("--weibo-variant short_post", weibo)
        self.assertIn("只有用户明确要求", weibo)
        self.assertIn("长文草稿失败不得自动改成短微博", weibo)

        content_format = self.read("references/content-format.md")
        self.assertIn("微博默认摘要短帖不需要再次确认", content_format)

    def test_local_markdown_links_exist(self) -> None:
        for path in ROOT.rglob("*.md"):
            content = path.read_text(encoding="utf-8")
            for raw_link in re.findall(r"\[[^\]]+\]\(([^)]+\.md(?:#[^)]+)?)\)", content):
                link = raw_link.split("#", 1)[0]
                self.assertTrue((path.parent / link).resolve().is_file(), f"missing {raw_link} from {path}")

    def test_reference_extension_secrets_were_not_copied(self) -> None:
        forbidden = (
            "9znpamsyl2c7cdrr9sas0le9vbc3r6ba",
            "06981375190026432f77c01bfca33e32",
            "dadde766-b087-42da-8e67-d2499a520ee7",
        )
        combined = "\n".join(path.read_text(encoding="utf-8") for path in ROOT.rglob("*.md"))
        for value in forbidden:
            self.assertNotIn(value, combined)

    def test_final_result_table_is_mandatory(self) -> None:
        skill = self.read("SKILL.md")
        reporting = self.read("references/result-reporting.md")
        for heading in ("平台", "完成情况", "链接"):
            self.assertIn(heading, skill)
            self.assertIn(heading, reporting)
        self.assertIn("publish-results.json", skill)
        self.assertIn("summary --strict", reporting)
        self.assertTrue((ROOT / "scripts/publish-result.py").is_file())

    def test_extension_free_adapters_are_bundled(self) -> None:
        for platform in ("weibo", "zhihu", "juejin", "baijiahao", "cnblogs"):
            source = ROOT / "adapters" / platform / "article-draft.js"
            self.assertTrue(source.is_file(), source)
            content = source.read_text(encoding="utf-8")
            self.assertIn("access: 'write'", content)
            self.assertIn("requireExecute(kwargs)", content)
            self.assertNotIn("$pluginSyncer", content)

        for platform in ("juejin", "baijiahao", "cnblogs"):
            source = ROOT / "adapters" / platform / "draft-account.js"
            self.assertTrue(source.is_file(), source)
            self.assertIn("access: 'read'", source.read_text(encoding="utf-8"))

    def test_real_browser_failure_modes_are_documented(self) -> None:
        browser = self.read("references/browser-editor-fallback.md")
        self.assertIn("fill.verified: false", browser)
        self.assertIn("CodeMirror", browser)
        self.assertIn("不得在 `fill` 后直接调用 `type`", browser)
        self.assertIn("iframe-html", browser)
        self.assertTrue((ROOT / "scripts/browser-editor-payload.py").is_file())

        xhs = self.read("references/xiaohongshu.md")
        self.assertIn("发布成功但无法验证", xhs)
        self.assertIn("不得重试", xhs)

        weibo = self.read("references/weibo.md")
        self.assertIn("旧封面", weibo)
        self.assertIn("仅粉丝阅读全文", weibo)


if __name__ == "__main__":
    unittest.main()
