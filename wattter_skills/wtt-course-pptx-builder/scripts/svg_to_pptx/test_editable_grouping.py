from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from .drawingml_converter import convert_svg_to_slide_shapes


class EditableGroupingTests(unittest.TestCase):
    def convert(self, body: str) -> tuple[str, list]:
        with tempfile.TemporaryDirectory(prefix="editable-grouping-") as temp:
            svg = Path(temp) / "page.svg"
            svg.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720">'
                + body
                + "</svg>",
                encoding="utf-8",
            )
            xml, _media, _rels, anim = convert_svg_to_slide_shapes(svg)
        return xml, anim

    def test_imported_single_shape_group_is_flattened(self) -> None:
        xml, anim = self.convert(
            '<g id="shape-42" data-name="文本框 41">'
            '<text x="80" y="120">可直接编辑</text></g>'
        )
        self.assertEqual(xml.count("<p:grpSp>"), 0)
        self.assertEqual(xml.count("<p:sp>"), 1)
        self.assertEqual(anim, [])

    def test_imported_multi_shape_group_keeps_source_name(self) -> None:
        xml, anim = self.convert(
            '<g id="shape-42" data-name="对比卡片">'
            '<rect x="80" y="100" width="300" height="200"/>'
            '<text x="100" y="140">标题</text></g>'
        )
        self.assertEqual(xml.count("<p:grpSp>"), 1)
        self.assertIn('name="对比卡片"', xml)
        self.assertEqual(anim, [])

    def test_semantic_single_child_group_is_preserved(self) -> None:
        xml, anim = self.convert(
            '<g id="card-benefit"><rect x="80" y="100" '
            'width="300" height="200"/></g>'
        )
        self.assertEqual(xml.count("<p:grpSp>"), 1)
        self.assertIn('name="card-benefit"', xml)
        self.assertEqual(len(anim), 1)

    def test_chrome_single_child_group_is_preserved_without_animation(self) -> None:
        xml, anim = self.convert(
            '<g id="page-header"><text x="80" y="120">标题</text></g>'
        )
        self.assertEqual(xml.count("<p:grpSp>"), 1)
        self.assertIn('name="page-header"', xml)
        self.assertEqual(anim, [])


if __name__ == "__main__":
    unittest.main()

