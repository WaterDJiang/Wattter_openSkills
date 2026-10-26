"""Frame-level rhythm contracts; no downloaded music or personal voice required."""
import copy
from fractions import Fraction
import math
from pathlib import Path
import sys
import tempfile
import unittest
import wave

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import pipeline as p


class RhythmTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.c={'schema':p.SCHEMA,'width':320,'height':180,'fps':30,
                'scenes':[{'id':'one','visualSeconds':4,'narration':'','leadSeconds':0,'tailSeconds':0}]}

    def tearDown(self):self.tmp.cleanup()

    def compile(self,lock=False):
        p.write(self.root/'film.json',self.c)
        return p.compile_timeline(self.root,lock)

    def rhythm(self,**extra):self.c['rhythm']={'bpm':120,'basis':'测试设计节奏',**extra}

    def audio(self):
        (self.root/'audio').mkdir(exist_ok=True)
        with wave.open(str(self.root/'audio/click.wav'),'wb') as w:
            w.setnchannels(1);w.setsampwidth(2);w.setframerate(8000);w.writeframes(b'\0\0'*1600)

    def test_legacy_shape_and_timing_unchanged(self):
        t=self.compile();self.assertNotIn('rhythm',t);self.assertNotIn('loop',t)
        self.assertEqual(t['totalFrames'],120);self.assertEqual(t['audioTracks'],[])

    def test_absolute_rounding_has_no_accumulated_drift(self):
        self.c['scenes'][0]['visualSeconds']=3600;self.rhythm(bpm=137,offsetSeconds=.123)
        beats=self.compile()['rhythm']['beats'];self.assertGreater(len(beats),8000)
        for i in (1,137,1000,len(beats)-1):
            expected=math.floor((Fraction('0.123')+i*Fraction(60,137))*30+Fraction(1,2))
            self.assertEqual(beats[i]['frame'],expected)

    def test_events_and_sound_share_quantized_frame(self):
        self.audio();self.rhythm(offsetSeconds=.15,audioFile='audio/click.wav',events=[{'id':'tap','beat':1,'action':'点击','sceneId':'one'}])
        self.c['audioTracks']=[{'file':'audio/click.wav','startBeat':1}]
        t=self.compile(True);event=t['rhythm']['events'][0]
        self.assertEqual(event['frame'],20);self.assertEqual(t['audioTracks'][0]['startSeconds'],20/30)
        self.assertEqual(t['totalFrames'],120)

    def test_measured_variable_beats_and_loop_metadata(self):
        self.c['rhythm']={'beatTimesSeconds':[.1,.63,1.23],'basis':'逐拍核对','events':[]};self.c['loop']=True
        t=self.compile();self.assertEqual([b['frame'] for b in t['rhythm']['beats']],[3,19,37]);self.assertTrue(t['loop'])

    def test_invalid_grid_fails(self):
        bad=[{'bpm':0},{'bpm':float('nan')},{'bpm':True},{'bpm':2000},{'bpm':120,'beatTimesSeconds':[0]},
             {'beatTimesSeconds':[]},{'beatTimesSeconds':[.5,.4]},{'beatTimesSeconds':[0,.001]},
             {'beatTimesSeconds':[0,4]},{'bpm':120,'offsetSeconds':4},
             {'beatTimesSeconds':[0,.5],'offsetSeconds':0},{'bpm':120,'beatsPerBar':True}]
        for data in bad:
            with self.subTest(data=data):
                self.c['rhythm']={'basis':'test',**data}
                with self.assertRaises(ValueError):self.compile()

    def test_basis_unknown_fields_and_loop_types_fail(self):
        for data in ({'bpm':120},{'bpm':120,'basis':'x','guess':1}):
            self.c['rhythm']=data
            with self.assertRaises(ValueError):self.compile()
        self.rhythm();self.c['loop']='yes'
        with self.assertRaisesRegex(ValueError,'loop'):self.compile()

    def test_event_bounds_duplicates_and_scene_drift_fail(self):
        event={'id':'tap','beat':1,'action':'点击'}
        for events in ([dict(event,beat=8)],[dict(event,beat=.5)],[event,event],
                       [dict(event,sceneId='missing')],[dict(event,action='')]):
            self.rhythm(events=events)
            with self.assertRaises(ValueError):self.compile()

    def test_conflicting_track_locations_or_missing_grid_fail(self):
        self.audio();self.c['audioTracks']=[{'file':'audio/click.wav','startBeat':1}]
        with self.assertRaisesRegex(ValueError,'startBeat'):self.compile()
        self.rhythm();self.c['audioTracks'][0]['startSeconds']=0
        with self.assertRaisesRegex(ValueError,'同时'):self.compile()

    def test_track_past_end_is_not_truncated(self):
        self.audio();self.c['rhythm']={'beatTimesSeconds':[0,3.95],'basis':'test'}
        self.c['audioTracks']=[{'file':'audio/click.wav','startBeat':1}]
        with self.assertRaisesRegex(ValueError,'片尾'):self.compile(True)

    def test_reference_music_must_be_used_in_film(self):
        self.rhythm(audioFile='audio/missing.wav')
        with self.assertRaisesRegex(ValueError,'audioTracks'):self.compile()

    def test_narration_duration_is_not_shortened_to_grid(self):
        self.audio();self.c['scenes'][0].update(narration='测试',voice='audio/click.wav',externalVoiceVerified=True)
        self.rhythm();t=self.compile(True)
        self.assertEqual(t['scenes'][0]['voiceFrames'],6);self.assertEqual(t['totalFrames'],120)

    def test_changed_grid_invalidates_locked_timeline_without_asset_review(self):
        p.write(self.root/'film.json',self.c);p.write(self.root/'assets.json',{'schema':'code-animation-assets/v1','assets':[],'links':[]})
        p.asset_review.seal(self.root);self.c=p.read(self.root/'film.json');self.rhythm()
        p.write(self.root/'timeline.json',self.compile(True));self.c['rhythm']['bpm']=110;p.write(self.root/'film.json',self.c)
        with self.assertRaisesRegex(ValueError,'过期'):p.locked(self.root)
        self.assertFalse((self.root/'.asset-review/candidates').exists())


if __name__=='__main__':unittest.main()
