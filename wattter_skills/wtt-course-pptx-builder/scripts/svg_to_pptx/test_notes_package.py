"""Speaker notes require a reachable notes master in the exported package."""
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from .pptx_builder import create_pptx_with_native_svg


class NotesPackageTests(unittest.TestCase):
    def test_native_notes_have_a_valid_master_and_preserve_text(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            svg = root / '01_notes.svg'
            svg.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720">'
                '<text x="60" y="100" font-size="32">中文备注测试</text></svg>'
            )
            pptx = root / 'notes.pptx'
            self.assertTrue(create_pptx_with_native_svg(
                [svg], pptx, notes={'01_notes': '讲师提示与中文正文'},
                use_native_shapes=True, workers=0, verbose=False,
            ))
            with zipfile.ZipFile(pptx) as archive:
                self.assertIn('ppt/notesMasters/notesMaster1.xml', archive.namelist())
                rels = ET.fromstring(archive.read('ppt/notesSlides/_rels/notesSlide1.xml.rels'))
                targets = [r.get('Target') for r in rels if r.get('Type', '').endswith('/notesMaster')]
                self.assertEqual(targets, ['../notesMasters/notesMaster1.xml'])
                text = ET.fromstring(archive.read('ppt/notesSlides/notesSlide1.xml'))
                self.assertIn('讲师提示与中文正文', ''.join(text.itertext()))


if __name__ == '__main__':
    unittest.main()
