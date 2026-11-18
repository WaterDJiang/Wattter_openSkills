from __future__ import annotations

import unittest

from .drawingml_utils import parse_font_family


class FontFamilyParsingTests(unittest.TestCase):
    def test_unicode_font_is_used_for_latin_and_east_asian_runs(self) -> None:
        fonts = parse_font_family('"Arial Unicode MS", Arial, sans-serif')
        self.assertEqual(
            fonts,
            {'latin': 'Arial Unicode MS', 'ea': 'Arial Unicode MS'},
        )

    def test_explicit_cjk_font_is_kept_with_latin_font(self) -> None:
        fonts = parse_font_family('"Microsoft YaHei", Arial, sans-serif')
        self.assertEqual(
            fonts,
            {'latin': 'Arial', 'ea': 'Microsoft YaHei'},
        )

    def test_plain_sans_stack_keeps_cjk_fallback(self) -> None:
        fonts = parse_font_family('Arial, sans-serif')
        self.assertEqual(
            fonts,
            {'latin': 'Arial', 'ea': 'Microsoft YaHei'},
        )

    def test_plain_serif_stack_uses_serif_cjk_fallback(self) -> None:
        fonts = parse_font_family('"Times New Roman", serif')
        self.assertEqual(
            fonts,
            {'latin': 'Times New Roman', 'ea': 'SimSun'},
        )

    def test_empty_stack_keeps_existing_defaults(self) -> None:
        self.assertEqual(
            parse_font_family(''),
            {'latin': 'Segoe UI', 'ea': 'Microsoft YaHei'},
        )


if __name__ == '__main__':
    unittest.main()
