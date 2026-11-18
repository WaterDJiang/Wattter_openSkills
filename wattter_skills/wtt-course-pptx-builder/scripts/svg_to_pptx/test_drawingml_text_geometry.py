"""Regression checks for editable text frames converted from SVG anchors."""

from __future__ import annotations

import unittest
from xml.etree import ElementTree as ET

from .drawingml_context import ConvertContext
from .drawingml_elements import convert_text
from .drawingml_utils import EMU_PER_PX, SVG_NS, estimate_text_width


_NAMESPACES = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
}


def _frame(text: str, *, x: float, font_size: float, anchor: str) -> tuple[float, float, float, ET.Element]:
    element = ET.Element(
        f'{{{SVG_NS}}}text',
        {
            'x': str(x),
            'y': '200',
            'font-size': str(font_size),
            'font-weight': 'bold',
            'font-family': '"微软雅黑", sans-serif',
            'text-anchor': anchor,
        },
    )
    element.text = text
    result = convert_text(element, ConvertContext())
    assert result is not None
    root = ET.fromstring(
        '<root xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
        f'{result.xml}</root>'
    )
    off = root.find('.//a:xfrm/a:off', _NAMESPACES)
    ext = root.find('.//a:xfrm/a:ext', _NAMESPACES)
    assert off is not None and ext is not None
    return (
        int(off.get('x')) / EMU_PER_PX,
        int(off.get('y')) / EMU_PER_PX,
        int(ext.get('cx')) / EMU_PER_PX,
        root,
    )


class EditableTextGeometryTests(unittest.TestCase):
    def test_em_dash_and_circled_numbers_keep_full_glyph_width(self) -> None:
        self.assertEqual(estimate_text_width('——', 18), 36)
        self.assertEqual(estimate_text_width('①', 24), 24)

    def test_mixed_size_runs_share_baseline_and_use_each_runs_width(self) -> None:
        element = ET.fromstring(
            f'<text xmlns="{SVG_NS}" x="100" y="200" font-size="20">'
            '<tspan font-size="44">45秒</tspan><tspan>，保留初答</tspan></text>'
        )
        result = convert_text(element, ConvertContext())
        self.assertIsNotNone(result)
        root = ET.fromstring(
            '<root xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
            'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
            f'{result.xml}</root>'
        )
        off = root.find('.//a:xfrm/a:off', _NAMESPACES)
        ext = root.find('.//a:xfrm/a:ext', _NAMESPACES)
        self.assertAlmostEqual(int(off.get('y')) / EMU_PER_PX, 156, places=3)
        expected = estimate_text_width('45秒', 44) + estimate_text_width('，保留初答', 20)
        self.assertGreaterEqual(int(ext.get('cx')) / EMU_PER_PX, expected)
        self.assertGreaterEqual(int(ext.get('cy')) / EMU_PER_PX, 44)
        self.assertEqual(root.findall('.//a:rPr', _NAMESPACES)[0].get('sz'), '3300')

    def test_bold_uppercase_text_has_room_for_single_line(self) -> None:
        # The China Mobile source renders XXX at 65.7 px (32 px font) and
        # 164.2 px (80 px font); narrower frames wrapped XX + X in LibreOffice.
        for font_size, rendered_width in ((32, 65.7), (80, 164.2)):
            with self.subTest(font_size=font_size):
                left, top, width, root = _frame('XXX', x=466.93, font_size=font_size, anchor='start')
                self.assertAlmostEqual(left, 466.93, places=3)
                self.assertAlmostEqual(top, 200 - font_size, places=3)
                self.assertGreater(width, rendered_width)
                self.assertEqual(
                    ''.join(node.text or '' for node in root.findall('.//a:t', _NAMESPACES)),
                    'XXX',
                )
                self.assertEqual(root.find('.//a:bodyPr', _NAMESPACES).get('wrap'), 'none')

    def test_center_and_end_anchors_keep_the_svg_alignment_point(self) -> None:
        middle_x = 618.2
        left, _, width, _ = _frame('XXX', x=middle_x, font_size=80, anchor='middle')
        self.assertAlmostEqual(left + width / 2, middle_x, places=3)

        end_x = 466.93
        left, _, width, _ = _frame('XXX', x=end_x, font_size=32, anchor='end')
        self.assertAlmostEqual(left + width, end_x, places=3)


if __name__ == '__main__':
    unittest.main()
