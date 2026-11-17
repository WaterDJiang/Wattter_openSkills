"""Synthetic fixtures validate consent gates; no fixture is real user artwork approval."""
import hashlib
import importlib.util
import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import preview_review as q
import pipeline as p
import asset_review as a

QUOTE = '测试夹具：确认当前这版四帧可继续渲染；不代表用户批准任何实际作品'


def png(path, rgb):
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)
    rows = b''.join(b'\0' + bytes(rgb) * 160 for _ in range(90))
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>2I5B', 160, 90, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b''))


class PreviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        (self.root / 'map.js').write_text('// synthetic test renderer, not actual artwork')
        (self.root / 'config.json').write_text('{"test":true}')
        for i in range(4):
            png(self.root / f'f{i}.png', (30 + i * 40, 80, 170))
        self.request = {'kind': 'map', 'fps': 30, 'totalFrames': 300, 'width': 160, 'height': 90,
                        'sourceSha256': {x: q.digest(self.root / x) for x in ('map.js', 'config.json')},
                        'frames': [{'frame': f, 'file': f'f{i}.png'} for i, f in enumerate((24, 105, 195, 276))]}

    def prepare(self):
        return q.prepare(self.root, self.request)

    def approve(self):
        result = self.prepare()
        return q.decide(self.root, result['version'], QUOTE)

    def test_prepare_creates_exact_four_real_images_and_labeled_grid_but_no_consent(self):
        result = self.prepare()
        manifest = q.read(self.root / result['manifestFile'])
        self.assertEqual(len(manifest['frames']), 4)
        self.assertEqual([x['seconds'] for x in manifest['frames']], [.8, 3.5, 6.5, 9.2])
        self.assertEqual(q.image_size(self.root / result['contactSheet']), (1280, 800))
        self.assertEqual(manifest['userApproval'], 'pending')
        with self.assertRaisesRegex(ValueError, '尚未获用户确认'):
            q.check(self.root)

    def test_explicit_fixture_confirmation_allows_same_fingerprint_rerun(self):
        before = self.approve()
        repeated = self.prepare()
        self.assertTrue(repeated['reused'])
        self.assertEqual(q.check(self.root, 'map'), before)
        self.assertEqual(len(list((self.root / '.preview-review/versions').iterdir())), 1)

    def test_same_images_in_new_candidate_directory_reuse_current_approval(self):
        before = self.approve()
        folder = self.root / 'candidate';folder.mkdir()
        for i, item in enumerate(self.request['frames']):
            file = folder / f'f{i}.png';file.write_bytes((self.root / item['file']).read_bytes())
            item['file'] = f'candidate/f{i}.png'
        self.assertTrue(self.prepare()['reused'])
        self.assertEqual(q.check(self.root), before)

    def test_runtime_resample_must_match_custom_approved_frames_before_export(self):
        receipt = self.approve()
        self.assertEqual(receipt['frameIndices'], [x['frame'] for x in self.request['frames']])
        folder = self.root / 'runtime';folder.mkdir()
        frames = []
        for i, item in enumerate(self.request['frames']):
            file = folder / f'f{i}.png';file.write_bytes((self.root / item['file']).read_bytes())
            frames.append({'frame': item['frame'], 'file': f'runtime/f{i}.png'})
        self.assertEqual(q.check(self.root, self.request['kind'], {'frames': frames}), receipt)
        png(self.root / frames[0]['file'], (15, 30, 240))
        with self.assertRaisesRegex(ValueError, '本次重绘四帧'):
            q.check(self.root, self.request['kind'], {'frames': frames})
        self.assertEqual(q.check(self.root), receipt)
        frames[0]['frame'] += 1
        with self.assertRaisesRegex(ValueError, '本次重绘四帧'):
            q.check(self.root, self.request['kind'], {'frames': frames})

    def test_generic_continue_style_choice_or_wrong_version_is_not_consent(self):
        result = self.prepare()
        for msg in ('', ' ', '继续', 'A', '好的', 'yes'):
            with self.assertRaisesRegex(ValueError, '明确原话'):
                q.decide(self.root, result['version'], msg)
        with self.assertRaisesRegex(ValueError, '当前展示版本'):
            q.decide(self.root, 'v0002', QUOTE)
        self.assertFalse(list((self.root / '.preview-review').rglob('decision-*.json')))

    def test_same_named_source_content_change_blocks_before_new_version_approved(self):
        self.approve()
        old = q.read(self.root / '.preview-review/current.json')
        (self.root / 'map.js').write_text('// same name, different geometry')
        with self.assertRaisesRegex(ValueError, '源文件变化'):
            q.check(self.root)
        self.request['sourceSha256']['map.js'] = q.digest(self.root / 'map.js')
        result = self.prepare()
        self.assertEqual(result['version'], 'v0002')
        self.assertTrue((self.root / '.preview-review/versions/v0001/decision-0001.json').is_file())
        self.assertNotEqual(q.read(self.root / '.preview-review/current.json'), old)
        with self.assertRaisesRegex(ValueError, '尚未获用户确认'):
            q.check(self.root)
        q.decide(self.root, result['version'], QUOTE)
        self.assertEqual(q.check(self.root)['version'], 'v0002')

    def test_original_sample_and_immutable_snapshot_tampering_block(self):
        self.approve()
        png(self.root / 'f0.png', (240, 240, 20))
        with self.assertRaisesRegex(ValueError, '样帧已变化'):
            q.check(self.root)
        result = self.prepare()
        q.decide(self.root, result['version'], QUOTE)
        m, _ = q.current(self.root)
        png(self.root / m['frames'][0]['file'], (1, 1, 1))
        with self.assertRaisesRegex(ValueError, '样帧已变化'):
            q.check(self.root)

    def test_contact_sheet_or_manifest_tamper_is_not_new_approval(self):
        receipt = self.approve()
        (self.root / receipt['contactSheet']).write_bytes(b'edited collage')
        with self.assertRaisesRegex(ValueError, '拼图已变化'):
            q.check(self.root)
        result = self.prepare()
        q.decide(self.root, result['version'], QUOTE)
        file = self.root / result['manifestFile']
        data = q.read(file);data['userApproval'] = 'approved';q.write(file, data)
        with self.assertRaisesRegex(ValueError, '清单已被替换'):
            q.check(self.root)

    def test_rejection_is_preserved_and_blocks_previous_approval(self):
        receipt = self.approve()
        q.decide(self.root, receipt['version'], '测试夹具：拒绝这版拼图，修改后重看', False)
        self.assertEqual(len(list((self.root / '.preview-review/versions/v0001').glob('decision-*.json'))), 2)
        with self.assertRaisesRegex(ValueError, '已撤回'):
            q.check(self.root)

    def test_four_distinct_in_range_frames_and_real_dimensions_are_required(self):
        self.request['frames'][3]['frame'] = 24
        with self.assertRaisesRegex(ValueError, '不同帧号'):
            self.prepare()
        self.request['frames'][3]['frame'] = 300
        with self.assertRaisesRegex(ValueError, '越出片长'):
            self.prepare()
        self.request['frames'][3]['frame'] = 276
        self.request['width'] = 1920
        with self.assertRaisesRegex(ValueError, '尺寸不符'):
            self.prepare()

    def test_path_escape_and_cross_route_approval_are_rejected(self):
        self.approve()
        with self.assertRaisesRegex(ValueError, '其他导出路线'):
            q.check(self.root, 'pipeline')
        self.request['sourceSha256']['../outside.js'] = 'a' * 64
        with self.assertRaisesRegex(ValueError, '越出项目'):
            self.prepare()


class PipelineGateTests(PreviewTests):
    def setUp(self):
        super().setUp()
        film = {'schema': p.SCHEMA, 'width': 160, 'height': 90, 'fps': 30,
                'scenes': [{'id': 'test', 'visualSeconds': 1, 'narration': ''}]}
        p.write(self.root / 'film.json', film)
        p.write(self.root / 'assets.json', {'schema': 'code-animation-assets/v1', 'assets': [], 'links': []})
        a.seal(self.root)
        t = p.compile_timeline(self.root, True);p.write(self.root / 'timeline.json', t)
        (self.root / 'audio').mkdir();(self.root / 'audio/mix-master.wav').write_bytes(b'unit-only synthetic mix bytes')
        p.write(self.root / 'audio/mix-report.json', {'assetReview': t['assetReview'], 'timelineSha256': p.digest(self.root / 'timeline.json'), 'mixSha256': p.digest(self.root / 'audio/mix-master.wav')})
        (self.root / 'silent.mp4').write_bytes(b'unit-only placeholder; never decoded or claimed as video')
        self.render = {'assetReview': t['assetReview'], 'mode': 'render', 'timelineSha256': p.digest(self.root / 'timeline.json'), 'videoSha256': p.digest(self.root / 'silent.mp4'), 'sourceSha256': {}}
        p.write(self.root / 'render-report.json', self.render)
        self.request.update(kind='pipeline', totalFrames=30, assetReview=t['assetReview'], sourceSha256={x: q.digest(self.root / x) for x in ('film.json', 'timeline.json', 'assets.json', 'map.js')}, frames=[{'frame': f, 'file': f'f{i}.png'} for i, f in enumerate((2, 8, 18, 27))])

    def test_optional_speech_protocol_must_be_bound_and_changes_invalidate(self):
        # Consent here is explicitly synthetic test data, never artwork authorization.
        folder = self.root/'tools'; folder.mkdir()
        helper = folder/'speech.py'; helper.write_text('# synthetic speech protocol v1')
        with self.assertRaisesRegex(ValueError, 'tools/speech.py'):
            self.prepare()
        self.request['sourceSha256']['tools/speech.py'] = q.digest(helper)
        self.approve()
        helper.write_text('# synthetic speech protocol v2')
        with self.assertRaisesRegex(ValueError, '源文件变化'):
            q.check(self.root)

    # These tests focus on the production wrapper, not inherited map-only assertions.
    def test_prepare_creates_exact_four_real_images_and_labeled_grid_but_no_consent(self):
        self.prepare()
        with self.assertRaisesRegex(ValueError, '尚未获用户确认'):
            p.check_render(self.root)
        self.assertEqual(p.locked(self.root)['totalFrames'], 30)

    def test_new_code_file_invalidates_approval_but_non_code_output_does_not(self):
        receipt = self.approve()
        (self.root / 'notes.txt').write_text('render log output')
        self.assertEqual(q.check(self.root), receipt)
        (self.root / 'late-added.js').write_text('// newly added code must be re-previewed')
        with self.assertRaisesRegex(ValueError, '文件集合新增或删除'):
            q.check(self.root)
        (self.root / 'late-added.js').unlink()
        folder = self.root / 'code';folder.mkdir();(folder / 'late-added.css').write_text('body{color:red}')
        with self.assertRaisesRegex(ValueError, '文件集合新增或删除'):
            q.check(self.root)

    def test_explicit_fixture_confirmation_allows_same_fingerprint_rerun(self):
        receipt = self.approve();self.render['previewReview'] = receipt;p.write(self.root / 'render-report.json', self.render)
        self.assertEqual(p.check_render(self.root)['totalFrames'], 30)
        self.assertEqual(q.check(self.root), receipt)

    def test_finish_and_validate_stop_before_encoding_without_current_approval(self):
        for operation in (p.finish, p.validate):
            with patch.object(p, 'run') as run:
                with self.assertRaisesRegex(ValueError, '尚无四帧拼图'):
                    operation(self.root)
                run.assert_not_called()

    def test_full_browser_export_blocks_before_chrome_or_file_mutation(self):
        before = (self.root / 'silent.mp4').read_bytes()
        result = subprocess.run(['node', str(ROOT / 'scripts/render.cjs'), str(self.root), '--render'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('尚无四帧拼图', result.stderr)
        self.assertEqual((self.root / 'silent.mp4').read_bytes(), before)
        self.assertFalse((self.root / 'preview').exists())

    def test_runtime_change_blocks_cli_before_encoder_and_inherits_custom_frames(self):
        self.approve()
        # Synthetic browser adapter: exercise the real Node -> Python export gate,
        # without presenting this fixture as Chrome rendering or user artwork.
        adapter = self.root / 'synthetic-browser.cjs'
        adapter.write_text('''
const fs=require('fs'),path=require('path'),root=process.env.SYNTHETIC_ROOT;
require('http').createServer=()=>({once(){},listen(port,host,ready){ready();},address(){return {port:9988};},close(){}});
const t=JSON.parse(fs.readFileSync(path.join(root,'timeline.json'))),frames=[2,8,18,27],trace=[];
let current=0;
const page={on(){},async route(){},async goto(){},async waitForFunction(){},
 async evaluate(fn,arg){const src=String(fn);if(arg!==undefined){current=arg;return;}
 if(src.includes('__filmMeta'))return t;if(src.includes('querySelectorAll'))return [];},
 locator(){return {async boundingBox(){return {width:t.width,height:t.height};},
 async screenshot(){trace.push(current);fs.writeFileSync(path.join(root,'synthetic-trace.json'),JSON.stringify(trace));
 let index=frames.indexOf(current);if(index<0||current===8)index=0;
 return fs.readFileSync(path.join(root,`f${index}.png`));}};}};
module.exports={chromium:{async launch(){return {async newPage(){return page;},version(){return 'synthetic-test-browser';},async close(){}};}}};
''')
        before = (self.root / 'silent.mp4').read_bytes()
        result = subprocess.run(['node', str(ROOT / 'scripts/render.cjs'), str(self.root), '--render'], capture_output=True, text=True,
                                env=dict(os.environ, PLAYWRIGHT_MODULE=str(adapter), SYNTHETIC_ROOT=str(self.root)))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('本次重绘四帧与已批准样帧不同', result.stderr)
        self.assertEqual((self.root / 'silent.mp4').read_bytes(), before)
        self.assertFalse((self.root / 'render-ffmpeg.log').exists())
        trace = q.read(self.root / 'synthetic-trace.json')
        self.assertTrue(set((2, 8, 18, 27)) <= set(trace))
        self.assertLess(len(trace), 30 + 20)

    def test_path_escape_and_cross_route_approval_are_rejected(self):
        self.approve()
        with self.assertRaisesRegex(ValueError, '其他导出路线'):
            q.check(self.root, 'map')

    def test_four_distinct_in_range_frames_and_real_dimensions_are_required(self):
        self.request['frames'][3]['frame'] = 30
        with self.assertRaisesRegex(ValueError, '越出片长'):
            self.prepare()

    def test_init_quality_and_preview_docs_have_no_missing_local_links(self):
        import re, voice
        with patch.object(voice, 'doctor', return_value={'nextStep': 'synthetic fixture no model', 'issues': []}):
            p.init(self.root / 'new-project')
        project = self.root / 'new-project'
        self.assertTrue((project / 'tools/preview_review.py').is_file())
        for name in ('QUALITY.md', 'PREVIEW.md', 'ASSETS.md', 'FOOTAGE.md'):
            for target in re.findall(r'\]\(([^)]+)\)', (project / name).read_text()):
                # Remote references are not files in the standalone project.
                if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target) or target.startswith('#'):
                    continue
                self.assertTrue((project / target.split('#')[0]).exists(), f'{name} -> {target}')


if __name__ == '__main__':
    unittest.main()
