from __future__ import annotations

import re
import io
import unittest
from xml.etree import ElementTree as ET

from .emu_units import NS, Xfrm
from .fill_to_svg import resolve_fill
from .ln_to_svg import resolve_stroke
from .pic_to_svg import Image as PILImage
from .pic_to_svg import _apply_blip_image_effects, _blip_opacity
from .prstgeom_to_svg import convert_prst_geom, supported_presets
from .shape_walker import walk_sp_tree
from .txbody_to_svg import convert_txbody


def _xml(body: str) -> ET.Element:
    return ET.fromstring(
        f'<root xmlns:a="{NS["a"]}" xmlns:p="{NS["p"]}">{body}</root>'
    )


class GradientFidelityTests(unittest.TestCase):
    def test_gradient_stops_are_sorted(self) -> None:
        root = _xml(
            """
            <a:gradFill>
              <a:gsLst>
                <a:gs pos="100000"><a:srgbClr val="0000FF"/></a:gs>
                <a:gs pos="0"><a:srgbClr val="FFFFFF"/></a:gs>
                <a:gs pos="54000"><a:srgbClr val="00BEFF"/></a:gs>
              </a:gsLst>
              <a:lin ang="0" scaled="1"/>
            </a:gradFill>
            """
        )
        result = resolve_fill(
            root.find("a:gradFill", NS), None, bounds=(10, 20, 200, 100),
        )
        offsets = [float(value) for value in re.findall(r'offset="([^"]+)"', result.defs[0])]
        self.assertEqual(offsets, [0.0, 0.54, 1.0])

    def test_path_gradient_uses_tile_and_focus_rect(self) -> None:
        root = _xml(
            """
            <a:gradFill rotWithShape="1">
              <a:gsLst>
                <a:gs pos="0"><a:srgbClr val="00BEFF"/></a:gs>
                <a:gs pos="100000"><a:srgbClr val="0165FF"/></a:gs>
              </a:gsLst>
              <a:path path="circle"><a:fillToRect r="100000" b="100000"/></a:path>
              <a:tileRect l="-100000" t="-100000"/>
            </a:gradFill>
            """
        )
        result = resolve_fill(
            root.find("a:gradFill", NS), None, bounds=(10, 20, 200, 100),
        )
        definition = result.defs[0]
        self.assertIn('cx="-1"', definition)
        self.assertIn('cy="-1"', definition)
        self.assertIn('r="2.8284"', definition)
        self.assertIn('data-pptx-path="circle"', definition)
        self.assertIn('data-pptx-fill-to-rect="0 0 1 1"', definition)
        self.assertIn('data-pptx-tile-rect="-1 -1 0 0"', definition)
        self.assertIn('gradientUnits="userSpaceOnUse"', definition)
        self.assertIn(
            'gradientTransform="matrix(200 0 0 100 10 20)"', definition,
        )

    def test_gradient_stroke_keeps_gradient_definition(self) -> None:
        root = _xml(
            """
            <p:spPr>
              <a:ln w="9525">
                <a:gradFill>
                  <a:gsLst>
                    <a:gs pos="100000"><a:srgbClr val="00BEFF"/></a:gs>
                    <a:gs pos="0"><a:srgbClr val="0165FF"/></a:gs>
                  </a:gsLst>
                  <a:lin ang="0" scaled="0"/>
                </a:gradFill>
              </a:ln>
            </p:spPr>
            """
        )
        result = resolve_stroke(
            root.find("p:spPr", NS), None, bounds=(10, 20, 200, 100),
        )
        self.assertRegex(result.attrs["stroke"], r"^url\(#mgrad\d+\)$")
        self.assertEqual(len(result.defs), 1)
        self.assertIn('gradientUnits="userSpaceOnUse"', result.defs[0])
        self.assertLess(result.defs[0].index('offset="0"'), result.defs[0].index('offset="1"'))


class TextFidelityTests(unittest.TestCase):
    def test_bottom_anchored_paragraphs_include_inherited_spacing(self) -> None:
        root = _xml(
            """
            <p:txBody>
              <a:bodyPr anchor="b" lIns="0" tIns="0" rIns="0" bIns="0">
                <a:noAutofit/>
              </a:bodyPr>
              <a:lstStyle/>
              <a:p><a:pPr algn="ctr"/><a:r><a:rPr sz="2000"/><a:t>XXX部门</a:t></a:r></a:p>
              <a:p><a:pPr algn="ctr"/>
                <a:r><a:rPr sz="2000"/><a:t>202</a:t></a:r>
                <a:r><a:rPr sz="2000"/><a:t>6</a:t></a:r>
                <a:r><a:rPr sz="2000"/><a:t>年1月</a:t></a:r>
              </a:p>
            </p:txBody>
            <p:bodyStyle><a:lvl1pPr>
              <a:lnSpc><a:spcPct val="90000"/></a:lnSpc>
              <a:spcBef><a:spcPts val="1000"/></a:spcBef>
            </a:lvl1pPr></p:bodyStyle>
            """
        )
        result = convert_txbody(
            root.find("p:txBody", NS), Xfrm(0, 0, 300, 122.67), None,
            fallback_lst_styles=(root.find("p:bodyStyle", NS),),
        )
        svg = ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{result.svg}</svg>')
        text_nodes = svg.findall("{http://www.w3.org/2000/svg}text")
        self.assertEqual(
            ["".join(node.itertext()) for node in text_nodes],
            ["XXX部门", "2026年1月"],
        )
        self.assertAlmostEqual(float(text_nodes[0].attrib["y"]), 75.20, delta=0.02)
        self.assertAlmostEqual(float(text_nodes[1].attrib["y"]), 117.34, delta=0.02)

    def test_percentage_line_spacing_moves_first_baseline(self) -> None:
        for spacing, expected_y in (("100000", 80.0), ("150000", 128.0)):
            with self.subTest(spacing=spacing):
                root = _xml(
                    f"""
                    <p:txBody>
                      <a:bodyPr lIns="0" tIns="0" rIns="0" bIns="0"/>
                      <a:lstStyle/>
                      <a:p><a:pPr><a:lnSpc><a:spcPct val="{spacing}"/></a:lnSpc></a:pPr>
                        <a:r><a:rPr sz="6000"/><a:t>XXX</a:t></a:r>
                      </a:p>
                    </p:txBody>
                    """
                )
                result = convert_txbody(
                    root.find("p:txBody", NS), Xfrm(0, 0, 400, 200), None,
                )
                svg = ET.fromstring(
                    f'<svg xmlns="http://www.w3.org/2000/svg">{result.svg}</svg>'
                )
                text_node = svg.find("{http://www.w3.org/2000/svg}text")
                self.assertIsNotNone(text_node)
                self.assertAlmostEqual(float(text_node.attrib["y"]), expected_y)


class PresetGeometryFidelityTests(unittest.TestCase):
    def test_deck_specific_presets_are_supported(self) -> None:
        self.assertTrue({"donut", "blockArc", "snip2DiagRect"}.issubset(supported_presets()))

    def test_deck_specific_presets_emit_paths(self) -> None:
        xfrm = Xfrm(10, 20, 200, 100)
        cases = {
            "donut": '<a:prstGeom xmlns:a="%s" prst="donut"><a:avLst/></a:prstGeom>' % NS["a"],
            "blockArc": (
                '<a:prstGeom xmlns:a="%s" prst="blockArc"><a:avLst>'
                '<a:gd name="adj1" fmla="val 10800000"/>'
                '<a:gd name="adj2" fmla="val 21579731"/>'
                '<a:gd name="adj3" fmla="val 12194"/>'
                '</a:avLst></a:prstGeom>' % NS["a"]
            ),
            "snip2DiagRect": (
                '<a:prstGeom xmlns:a="%s" prst="snip2DiagRect"><a:avLst>'
                '<a:gd name="adj1" fmla="val 3890"/>'
                '<a:gd name="adj2" fmla="val 4846"/>'
                '</a:avLst></a:prstGeom>' % NS["a"]
            ),
        }
        for preset, xml in cases.items():
            with self.subTest(preset=preset):
                element = ET.fromstring(xml)
                geom = convert_prst_geom(preset, xfrm, element)
                self.assertIsNotNone(geom)
                self.assertEqual(geom.tag, "path")
                self.assertTrue(geom.path_d)

    def test_arc_is_never_theme_filled(self) -> None:
        element = ET.fromstring(
            '<a:prstGeom xmlns:a="%s" prst="arc"><a:avLst/></a:prstGeom>'
            % NS["a"]
        )
        geom = convert_prst_geom("arc", Xfrm(0, 0, 200, 100), element)
        self.assertIsNotNone(geom)
        self.assertTrue(geom.force_no_fill)

    def test_arc_adjustments_use_drawingml_angle_units(self) -> None:
        element = ET.fromstring(
            '<a:prstGeom xmlns:a="%s" prst="arc"><a:avLst>'
            '<a:gd name="adj1" fmla="val 10800000"/>'
            '<a:gd name="adj2" fmla="val 0"/>'
            '</a:avLst></a:prstGeom>' % NS["a"]
        )
        geom = convert_prst_geom("arc", Xfrm(0, 0, 200, 100), element)
        self.assertIsNotNone(geom)
        self.assertEqual(geom.path_d, "M 0 50 A 100 50 0 0 1 200 50")


class GroupFillFidelityTests(unittest.TestCase):
    def test_child_grp_fill_inherits_parent_group_fill(self) -> None:
        slide = _xml(
            """
            <p:cSld><p:spTree>
              <p:grpSp>
                <p:nvGrpSpPr><p:cNvPr id="1" name="group"/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
                <p:grpSpPr>
                  <a:xfrm><a:off x="0" y="0"/><a:ext cx="914400" cy="914400"/><a:chOff x="0" y="0"/><a:chExt cx="914400" cy="914400"/></a:xfrm>
                  <a:solidFill><a:srgbClr val="12ABEF"/></a:solidFill>
                </p:grpSpPr>
                <p:sp>
                  <p:nvSpPr><p:cNvPr id="2" name="child"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
                  <p:spPr>
                    <a:xfrm><a:off x="0" y="0"/><a:ext cx="914400" cy="914400"/></a:xfrm>
                    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
                    <a:grpFill/>
                  </p:spPr>
                </p:sp>
              </p:grpSp>
            </p:spTree></p:cSld>
            """
        )
        child = walk_sp_tree(slide)[0].children[0]
        self.assertIsNotNone(child.inherited_group_fill)
        fill = resolve_fill(child.inherited_group_fill, None)
        self.assertEqual(fill.attrs["fill"], "#12ABEF")


class PictureFidelityTests(unittest.TestCase):
    def test_alpha_mod_fix_ratio_is_resolved(self) -> None:
        root = _xml('<a:blip><a:alphaModFix amt="10000"/></a:blip>')
        self.assertEqual(_blip_opacity(root.find("a:blip", NS)), 0.1)

    def test_alpha_mod_fix_is_baked_into_png_alpha_channel(self) -> None:
        if PILImage is None:
            self.skipTest("Pillow is not installed")
        source = io.BytesIO()
        PILImage.new("RGB", (1, 1), (10, 20, 30)).save(source, format="PNG")
        root = _xml('<a:blip><a:alphaModFix amt="10000"/></a:blip>')
        filename, data = _apply_blip_image_effects(
            "image.png", source.getvalue(), root.find("a:blip", NS),
        )
        self.assertRegex(filename, r"^image_fx_[0-9a-f]{8}\.png$")
        rendered = PILImage.open(io.BytesIO(data)).convert("RGBA")
        self.assertEqual(rendered.getpixel((0, 0)), (10, 20, 30, 26))


if __name__ == "__main__":
    unittest.main()
