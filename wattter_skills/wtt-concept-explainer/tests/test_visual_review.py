"""视觉检查记录只验证实际文件绑定和覆盖，不伪造视觉判断。"""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import pipeline as p


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.t={'width':1920,'height':1080,'fps':30,'captions':[], 'scenes':[
            {'id':'a1','startFrame':0,'endFrame':60,'director':{'group':'a','reviewAtSeconds':.5}},
            {'id':'a2','startFrame':60,'endFrame':120,'director':{'group':'a'}},
            {'id':'b','startFrame':120,'endFrame':180,'director':{}}]}
        p.write(self.root/'timeline.json',self.t);(self.root/'final.mp4').write_bytes(b'unit-fixture-not-video')
        groups=p.review_plan(self.t);items=[]
        for g in groups:
            for frame in g['frames']:
                for width in (640,1920):
                    name=f'{g["id"]}-f{frame}-w{width}';f=self.root/name;f.write_bytes(name.encode())
                    items.append({'id':name,'groupId':g['id'],'kind':'image','width':width,'frame':frame,'file':name,'sha256':p.digest(f)})
            for i,window in enumerate(g['windows']):
                name=f'{g["id"]}-motion-{i}';f=self.root/name;f.write_bytes(name.encode())
                items.append({'id':name,'groupId':g['id'],'kind':'clip','width':640,'file':name,'sha256':p.digest(f),**window})
        self.manifest={'groups':groups,'evidence':items,'previewWidths':[640,960],
            'finalSha256':p.digest(self.root/'final.mp4'),'timelineSha256':p.digest(self.root/'timeline.json')}
        p.write(self.root/'evidence.json',self.manifest)
        self.r={'schema':'concept-video-review/v1','finalSha256':self.manifest['finalSha256'],
            'timelineSha256':self.manifest['timelineSha256'],'evidenceFile':'evidence.json','evidenceSha256':p.digest(self.root/'evidence.json'),
            'reviewer':{'name':'unit fixture','method':'Synthetic record only, no visual claim'},
            'checks':{key:{'status':'pass','notes':'Synthetic validation fixture, not a production visual judgment',
                'evidenceIds':[e['id'] for e in items]} for key in p.REVIEW_CHECKS},
            'audioReview':{'status':'not_checked','notes':''},'userAcceptance':'pending'}
        self.save()
    def tearDown(self):self.tmp.cleanup()
    def save(self):p.write(self.root/'visual-review.json',self.r)
    def test_valid_binding_does_not_invent_audio_or_user_acceptance(self):
        r=p.check_visual_review(self.root,self.t)
        self.assertTrue(r['passed']);self.assertEqual(r['audioReview']['status'],'not_checked');self.assertEqual(r['userAcceptance'],'pending')
    def test_voice_segments_collapse_to_visual_shots_and_explicit_motion_start(self):
        groups=p.review_plan(self.t);self.assertEqual(len(groups),2)
        self.assertEqual(groups[0]['windows'],[{'startFrame':15,'endFrame':75}])
    def test_motion_anchor_outside_segment_fails(self):
        self.t['scenes'][0]['director']['reviewAtSeconds']=2
        with self.assertRaisesRegex(ValueError,'超出'):p.review_plan(self.t)
    def test_pending_or_failed_is_not_passed(self):
        for status in ('pending','fail'):
            self.r['checks']['motion']['status']=status;self.save()
            with self.assertRaisesRegex(ValueError,'motion 未通过'):p.check_visual_review(self.root,self.t)
    def test_missing_observation_is_rejected(self):
        self.r['checks']['focus']['notes']=' ';self.save()
        with self.assertRaisesRegex(ValueError,'观察'):p.check_visual_review(self.root,self.t)
    def test_stale_final_rejected(self):
        (self.root/'final.mp4').write_bytes(b'new encode')
        with self.assertRaisesRegex(ValueError,'过期'):p.check_visual_review(self.root,self.t)
    def test_evidence_tampering_and_missing_files_rejected(self):
        file=self.root/self.manifest['evidence'][0]['file'];file.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'证据已变化'):p.check_visual_review(self.root,self.t)
        file.unlink()
        with self.assertRaises(FileNotFoundError):p.check_visual_review(self.root,self.t)
    def test_single_shot_cannot_claim_whole_film_reviewed(self):
        self.r['checks']['motion']['evidenceIds']=[e['id'] for e in self.manifest['evidence'] if e['groupId']=='shot-001'];self.save()
        with self.assertRaisesRegex(ValueError,'全部大镜'):p.check_visual_review(self.root,self.t)
    def test_stills_cannot_replace_motion_evidence(self):
        self.r['checks']['motion']['evidenceIds']=[e['id'] for e in self.manifest['evidence'] if e['kind']=='image'];self.save()
        with self.assertRaisesRegex(ValueError,'连续片段'):p.check_visual_review(self.root,self.t)
    def test_large_frames_cannot_replace_small_playback_review(self):
        self.r['checks']['readability']['evidenceIds']=[e['id'] for e in self.manifest['evidence'] if e['width']==1920];self.save()
        with self.assertRaisesRegex(ValueError,'最小尺寸'):p.check_visual_review(self.root,self.t)
    def test_midpoint_does_not_replace_transition_boundaries(self):
        self.r['checks']['transitions']['evidenceIds']=[e['id'] for e in self.manifest['evidence'] if e.get('frame') in (59,149)];self.save()
        with self.assertRaisesRegex(ValueError,'首中尾'):p.check_visual_review(self.root,self.t)
    def test_blank_opening_does_not_replace_readable_caption_frames(self):
        self.r['checks']['readability']['evidenceIds']=[e['id'] for e in self.manifest['evidence'] if e.get('frame') in (0,120) and e['width']==640];self.save()
        with self.assertRaisesRegex(ValueError,'字幕帧'):p.check_visual_review(self.root,self.t)
    def test_init_wont_overwrite_existing_observations(self):
        before=(self.root/'visual-review.json').read_bytes()
        with self.assertRaisesRegex(ValueError,'已存在'):p.review_init(self.root)
        self.assertEqual(before,(self.root/'visual-review.json').read_bytes())
    def test_failed_rerun_removes_stale_success_receipt(self):
        (self.root/'visual-review-check.json').write_text('{}')
        with patch.object(p,'validate',side_effect=ValueError('stale source')):
            with self.assertRaisesRegex(ValueError,'stale source'):p.review(self.root)
        self.assertFalse((self.root/'visual-review-check.json').exists())

if __name__=='__main__':unittest.main()
