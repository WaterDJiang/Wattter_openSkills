"""Synthetic fixtures only: material history, exact review approval, and pipeline gates."""
import contextlib
import copy
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1]/'scripts'
if str(SCRIPTS) not in sys.path: sys.path.insert(0, str(SCRIPTS))
import asset_review as a
import pipeline as p


class AssetReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name).resolve()
        (self.root/'media').mkdir(); (self.root/'media/logo.svg').write_text('<svg>original</svg>')
        (self.root/'index.html').write_text('<canvas id="stage"></canvas>')
        self.selection = {'schema': a.SCHEMA, 'assets': [{'id': 'logo', 'path': 'media/logo.svg',
            'sourceUrl': 'https://example.org/original.svg', 'license': 'CC0-1.0',
            'useBasis': 'synthetic test only', 'landingUrl': 'https://example.org/project'}],
            'links': [{'id': 'home', 'url': 'https://example.org/project', 'purpose': 'test link'}]}
        a.write_new(self.root/'assets.json', self.selection)
        a.write_new(self.root/'film.json', {'schema': p.SCHEMA, 'width': 320, 'height': 180, 'fps': 10,
                                          'scenes': [{'id': 'one', 'visualSeconds': .4, 'narration': ''}]})
        self.receipt = a.seal(self.root)
        self.before = self.tree()

    def tearDown(self): self.tmp.cleanup()

    def tree(self):
        return {str(f.relative_to(self.root)): a.sha(f) for f in self.root.rglob('*')
                if f.is_file() and 'candidates' not in f.parts and f.name!='.mutex'}

    def mutate(self, field):
        data = copy.deepcopy(self.selection)
        if field == 'sha256': (self.root/'media/logo.svg').write_text('<svg>different same name</svg>')
        elif field == 'deleted': (self.root/'media/logo.svg').unlink()
        elif field == 'url': data['links'][0]['url'] = 'https://example.org/new'
        elif field == 'license': data['assets'][0][field] = 'CC-BY-4.0'
        else: data['assets'][0][field] = 'https://example.org/new'
        a.replace_json(self.root/'assets.json', data)

    def blocked(self):
        with contextlib.redirect_stderr(io.StringIO()) as readable:
            with self.assertRaisesRegex(ValueError, '未确认'): a.require(self.root)
        text = readable.getvalue()
        self.assertIn('旧值', text); self.assertIn('新值', text); self.assertIn('原因', text); self.assertIn('影响', text)
        reviews = list((a.state(self.root)/'candidates').glob('review-*/review.json'))
        self.assertTrue(reviews)
        return a.read(reviews[-1]), text

    def proposal(self, new=None):
        new = copy.deepcopy(new or self.selection)
        candidate = a.state(self.root)/'candidates/input/new.svg'
        candidate.parent.mkdir(parents=True, exist_ok=True); candidate.write_text('<svg>approved replacement</svg>')
        new['assets'][0]['candidatePath'] = str(candidate.relative_to(self.root))
        file = candidate.parent/'proposal.json'; a.replace_json(file, new)
        with contextlib.redirect_stderr(io.StringIO()):
            return a.propose(self.root, file, '替换测试标志', '该标志所在镜头重新渲染并验收')

    def authorization(self, review, kind='confirmed'):
        dest = self.root/'authorization.json'
        a.replace_json(dest, {'kind': kind, 'statement': '测试夹具模拟：将 logo 替换为已审阅的候选 SVG',
                             'reviewSha256': review['reviewSha256'], 'changes': [r['key'] for r in review['changes']]})
        return dest

    def test_original_rerun_is_read_only_without_confirmation(self):
        self.assertEqual(a.require(self.root), self.receipt)
        self.assertEqual(a.require(self.root), self.receipt)
        self.assertEqual(self.tree(), self.before)
        self.assertFalse((a.state(self.root)/'candidates').exists())

    def test_code_only_changes_do_not_request_material_confirmation(self):
        (self.root/'scenes.js').write_text('const x=2; // code only')
        self.assertEqual(a.require(self.root), self.receipt)
        self.assertFalse((a.state(self.root)/'candidates').exists())

    def test_changed_bytes_same_name_diff_and_block(self):
        self.mutate('sha256'); review, _ = self.blocked()
        row = review['diff']['changes'][0]
        self.assertEqual(row['key'], 'assets.logo.sha256'); self.assertNotEqual(row['old'], row['new'])
        self.assertEqual(a.read(a.state(self.root)/'current.json'), self.receipt)
        self.assertEqual((a.state(self.root)/'versions/v0001/files/logo').read_text(), '<svg>original</svg>')

    def test_source_changed_diff_and_block(self):
        self.mutate('sourceUrl'); _, text = self.blocked(); self.assertIn('sourceUrl', text)

    def test_license_changed_diff_and_block(self):
        self.mutate('license'); _, text = self.blocked(); self.assertIn('CC-BY-4.0', text)

    def test_asset_landing_changed_diff_and_block(self):
        self.mutate('landingUrl'); _, text = self.blocked(); self.assertIn('landingUrl', text)

    def test_web_landing_changed_diff_and_block(self):
        self.mutate('url'); _, text = self.blocked(); self.assertIn('links.home.url', text)

    def test_hardcoded_web_redirect_changed_is_not_code_only(self):
        (self.root/'index.html').write_text('<a href="https://example.org/new">new</a>')
        _, text = self.blocked(); self.assertIn('observed-', text)

    def test_deleted_file_diff_and_block(self):
        self.mutate('deleted'); review, _ = self.blocked()
        self.assertIsNone(review['diff']['changes'][0]['new'])

    def test_candidate_does_not_update_current_assets_or_lock(self):
        self.proposal(); self.assertEqual(self.tree(), self.before)
        self.assertEqual(a.require(self.root), self.receipt)

    def test_accept_creates_new_version_preserving_old_diff_and_files(self):
        proposed = self.proposal(); auth = self.authorization(proposed)
        with contextlib.redirect_stderr(io.StringIO()): receipt = a.accept(self.root, proposed['candidate'], auth)
        self.assertEqual(receipt['version'], 'v0002'); self.assertEqual(a.require(self.root), receipt)
        self.assertEqual((a.state(self.root)/'versions/v0001/files/logo').read_text(), '<svg>original</svg>')
        self.assertEqual((self.root/'media/logo.svg').read_text(), '<svg>approved replacement</svg>')
        self.assertTrue((a.state(self.root)/'versions/v0002/diff.md').is_file())
        with self.assertRaisesRegex(ValueError, '重建'): a.seal(self.root)

    def test_explicit_request_authorization_still_prints_diff(self):
        review=self.proposal(); auth=self.authorization(review, 'explicit-request')
        with contextlib.redirect_stderr(io.StringIO()) as text: a.accept(self.root, review['candidate'], auth)
        self.assertIn('assets.logo.sha256', text.getvalue())

    def test_unbound_or_partial_authorization_fails(self):
        review=self.proposal(); file=self.authorization(review)
        data=a.read(file);data['reviewSha256']='wrong';a.replace_json(file,data)
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaisesRegex(ValueError, '未绑定'):
            a.accept(self.root, review['candidate'],file)
        data['reviewSha256']=review['reviewSha256'];data['changes']=[];a.replace_json(file,data)
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaisesRegex(ValueError, '范围'):
            a.accept(self.root,review['candidate'],file)
        self.assertEqual(a.require(self.root),self.receipt)

    def test_candidate_mutation_after_review_is_blocked(self):
        review=self.proposal();auth=self.authorization(review)
        (a.state(self.root)/'candidates'/review['candidate']/'files/logo').write_text('tampered')
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaisesRegex(ValueError,'候选文件'):
            a.accept(self.root,review['candidate'],auth)
        self.assertEqual(a.require(self.root),self.receipt)

    def test_unreviewed_working_change_cannot_be_overwritten_by_approval(self):
        review=self.proposal();auth=self.authorization(review);self.mutate('sourceUrl')
        with contextlib.redirect_stderr(io.StringIO()),self.assertRaisesRegex(ValueError,'未纳入'):
            a.accept(self.root,review['candidate'],auth)

    def test_stale_approval_cannot_be_replayed(self):
        review=self.proposal();auth=self.authorization(review)
        with contextlib.redirect_stderr(io.StringIO()): a.accept(self.root,review['candidate'],auth)
        with contextlib.redirect_stderr(io.StringIO()),self.assertRaisesRegex(ValueError,'已过期'):
            a.accept(self.root,review['candidate'],auth)

    def test_reseal_and_deleted_lock_cannot_rebaseline(self):
        with self.assertRaisesRegex(ValueError,'重建'): a.seal(self.root)
        (a.state(self.root)/'current.json').unlink()
        with self.assertRaisesRegex(ValueError,'缺失'):a.require(self.root)
        with self.assertRaisesRegex(ValueError,'重建'):a.seal(self.root)

    def test_deleted_history_is_detected_by_film_anchor(self):
        shutil.rmtree(a.state(self.root))
        with self.assertRaisesRegex(ValueError,'缺失'):a.require(self.root)
        with self.assertRaisesRegex(ValueError,'重建'):a.seal(self.root)

    def test_rewritten_manifest_or_hash_report_cannot_pass(self):
        file=a.state(self.root)/'versions/v0001/manifest.json';data=a.read(file)
        data['selection']['assets'][0]['sourceUrl']='https://example.org/new';a.replace_json(file,data)
        a.write_new(self.root/'render-report.json',{'sourceSha256': {'media/logo.svg':a.sha(self.root/'media/logo.svg')}})
        with self.assertRaisesRegex(ValueError,'哈希'): a.require(self.root)

    def test_missing_registration_and_asset_generator_overwrite_are_blocked(self):
        with self.assertRaisesRegex(ValueError,'未登记'):a.registered(self.root,['media/unknown.png'])
        with self.assertRaisesRegex(ValueError,'候选'):a.protect_output(self.root,self.root/'media/logo.svg')
        with self.assertRaisesRegex(ValueError,'候选'):a.protect_output(self.root,self.root/'media/new.wav')

    def test_pipeline_execution_and_acceptance_block_before_work(self):
        t=p.compile_timeline(self.root,True);p.write(self.root/'timeline.json',t)
        self.mutate('sourceUrl')
        for operation in (p.mix,p.finish,p.validate):
            with contextlib.redirect_stderr(io.StringIO()), patch.object(p,'run') as run:
                with self.assertRaisesRegex(ValueError,'未确认'):operation(self.root)
                run.assert_not_called()
        self.assertFalse((self.root/'delivery-check.json').exists())

    def test_after_approval_old_timeline_cannot_be_accepted(self):
        p.write(self.root/'timeline.json',p.compile_timeline(self.root,True))
        review=self.proposal();auth=self.authorization(review)
        with contextlib.redirect_stderr(io.StringIO()):a.accept(self.root,review['candidate'],auth)
        with self.assertRaisesRegex(ValueError,'未绑定'):p.locked(self.root)
        p.write(self.root/'timeline.json',p.compile_timeline(self.root,True))
        self.assertEqual(p.locked(self.root)['assetReview']['version'],'v0002')

    def test_metadata_only_approval_and_asset_removal(self):
        data=copy.deepcopy(self.selection); data['assets'][0]['sourceUrl']='https://example.org/approved-source'
        data['links'][0]['url']='https://example.org/approved-link'
        proposal=self.root/'proposal.json';a.replace_json(proposal,data)
        with contextlib.redirect_stderr(io.StringIO()):
            review=a.propose(self.root,proposal,'变更出处与导流','重新验收');auth=self.authorization(review)
            self.assertEqual(a.accept(self.root,review['candidate'],auth)['version'],'v0002')
        self.assertEqual(a.require(self.root)['version'],'v0002')
        data['assets']=[];a.replace_json(proposal,data)
        (self.root/'media/logo.svg').unlink()
        with contextlib.redirect_stderr(io.StringIO()):
            review=a.propose(self.root,proposal,'确认移除已删除素材','重渲染');auth=self.authorization(review)
            self.assertEqual(a.accept(self.root,review['candidate'],auth)['version'],'v0003')
        self.assertEqual(a.require(self.root)['version'],'v0003')
        self.assertTrue((a.state(self.root)/'versions/v0001/files/logo').is_file())

    def test_new_asset_requires_proposal_and_is_preserved_after_accept(self):
        data=copy.deepcopy(self.selection)
        new=copy.deepcopy(data['assets'][0]);new.update(id='second',path='media/second.svg')
        source=a.state(self.root)/'candidates/added.svg';source.parent.mkdir(parents=True);source.write_text('<svg>new</svg>')
        new['candidatePath']=str(source.relative_to(self.root));data['assets'].append(new)
        proposal=self.root/'proposal.json';a.replace_json(proposal,data)
        with contextlib.redirect_stderr(io.StringIO()):
            review=a.propose(self.root,proposal,'新增测试素材','重新渲染');auth=self.authorization(review)
            self.assertFalse((self.root/'media/second.svg').exists())
            a.accept(self.root,review['candidate'],auth)
        self.assertEqual((self.root/'media/second.svg').read_text(),'<svg>new</svg>')
        self.assertEqual(a.require(self.root)['version'],'v0002')

    def test_voice_sidecar_must_be_registered(self):
        (self.root/'media/test.wav.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'test.wav.json'):
            a.registered(self.root,['media/test.wav'])

    def test_runtime_dynamic_link_diff_and_block(self):
        with contextlib.redirect_stderr(io.StringIO()) as out,self.assertRaisesRegex(ValueError,'未确认'):
            a.observe(self.root,'https://example.org/dynamic')
        self.assertIn('新值',out.getvalue());self.assertIn('dynamic',out.getvalue())
        self.assertEqual(a.read(a.state(self.root)/'current.json'),self.receipt)

    def test_renderer_checks_before_browser_or_reports(self):
        self.mutate('url')
        result=subprocess.run(['node',str(SCRIPTS/'render.cjs'),str(self.root),'--preview'],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0);self.assertIn('links.home.url',result.stderr)
        self.assertFalse((self.root/'preview-report.json').exists())


if __name__=='__main__':unittest.main()
