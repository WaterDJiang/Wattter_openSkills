"""真实逐句校时、角色请求失效与旧旁白兼容；不加载或下载声音模型。"""
import array
import copy
import importlib.util
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
import wave
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import speech

spec = importlib.util.spec_from_file_location('speech_pipeline_test', ROOT/'scripts/pipeline.py')
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


def film():
    return dict(schema=p.SCHEMA, width=640, height=360, fps=30,
                cast={'narrator': {}, 'hero': {'voiceId': 'actor-a', 'label': '主角'}},
                scenes=[dict(id='one', visualSeconds=.1, leadSeconds=.1, tailSeconds=.1,
                             utterances=[dict(id='u-one', speakerId='hero', text='是你吗？',
                                              performance={'instruct': '轻声疑问'},
                                              pauseAfterSeconds=.11),
                                         dict(id='u-two', speakerId='narrator', text='是我，别怕。')])])


class SpeechProtocolTests(unittest.TestCase):
    def test_cast_preserves_unresolved_default_and_fixed_role(self):
        f = film(); jobs = speech.scene_utterances(f, f['scenes'][0])
        self.assertEqual([j['voiceId'] for j in jobs], ['actor-a', None])
        self.assertEqual(jobs[0]['voice'], 'audio/one-u-one.wav')
        self.assertEqual(jobs[1]['performance'], {'instruct': '', 'intent': ''})

    def test_unknown_character_and_missing_role_voice_fail(self):
        f = film(); f['scenes'][0]['utterances'][0]['speakerId'] = 'unknown'
        with self.assertRaisesRegex(ValueError, '未知角色'):
            speech.scene_utterances(f, f['scenes'][0])
        f = film(); f['cast']['hero'] = {'label': '主角'}
        with self.assertRaisesRegex(ValueError, '缺少 voiceId'):
            speech.scene_utterances(f, f['scenes'][0])

    def test_utterance_ids_are_unique_across_scenes_and_legacy(self):
        f = film(); f['scenes'].append(dict(id='two', visualSeconds=1,
            utterances=[dict(id='u-one', speakerId='hero', text='重复')]))
        with self.assertRaisesRegex(ValueError, '必须唯一'):
            speech.scene_utterances(f, f['scenes'][0])
        f = film(); f['scenes'].append(dict(id='u-one', visualSeconds=1, narration='旁白'))
        with self.assertRaisesRegex(ValueError, '必须唯一'):
            speech.scene_utterances(f, f['scenes'][0])

    def test_legacy_conflict_empty_dialogue_and_unhandled_controls_fail(self):
        changes = [lambda s: s.update(narration='另一路旁白'),
                   lambda s: s.update(voice='audio/legacy.wav'),
                   lambda s: s.update(utterances=[]),
                   lambda s: s['utterances'][0].update(startSeconds=1),
                   lambda s: s['utterances'][0].update(performance={'emotion': 'happy'})]
        for change in changes:
            f = film(); change(f['scenes'][0])
            with self.subTest(f=f), self.assertRaises(ValueError):
                speech.scene_utterances(f, f['scenes'][0])

    def test_invalid_pause_and_external_review_type_fail(self):
        for value in [-.1, float('nan'), True]:
            f = film(); f['scenes'][0]['utterances'][0]['pauseAfterSeconds'] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                speech.scene_utterances(f, f['scenes'][0])
        f = film(); f['scenes'][0]['utterances'][0]['externalVoiceVerified'] = 'yes'
        with self.assertRaisesRegex(ValueError, '布尔'):
            speech.scene_utterances(f, f['scenes'][0])

    def test_voice_request_changes_only_for_synthesis_relevant_fields(self):
        f = film(); job = speech.scene_utterances(f, f['scenes'][0])[0]
        before = speech.request_fingerprint(job)
        for key, value in [('voice', '.asset-review/candidates/new.wav'), ('pauseAfterSeconds', .9)]:
            changed = dict(job, **{key: value})
            self.assertEqual(before, speech.request_fingerprint(changed))
        for key, value in [('voiceId', 'actor-b'), ('speakerId', 'other'),
                           ('text', '另一句话'), ('performance', {'instruct': '开心', 'intent': ''})]:
            self.assertNotEqual(before, speech.request_fingerprint(dict(job, **{key: value})))

    def test_seed_is_stable_when_other_lines_are_inserted(self):
        expected = speech.utterance_seed(42, 'u-two')
        jobs = ['u-one', 'u-two']; before = {uid: speech.utterance_seed(42, uid) for uid in jobs}
        jobs.insert(1, 'new-line'); after = {uid: speech.utterance_seed(42, uid) for uid in jobs}
        self.assertEqual(expected, after['u-two'])
        self.assertTrue(all(before[uid] == after[uid] for uid in before))
        self.assertNotEqual(after['u-one'], after['u-two'])


class SpeechProjectInitTests(unittest.TestCase):
    def test_generated_voice_guide_has_reachable_local_links(self):
        fake = types.SimpleNamespace(doctor=lambda *_: {'nextStep': 'test fixture', 'issues': []})
        with tempfile.TemporaryDirectory() as temp, patch.dict(sys.modules, {'voice': fake}):
            project = Path(temp) / 'project'
            p.init(project)
            guide = (project / 'VOICE.md').read_text(encoding='utf-8')
            local_links = []
            for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', guide):
                url = urlsplit(target)
                if url.scheme or url.netloc or not url.path:
                    continue
                local_links.append(url.path)
                self.assertTrue((project / url.path).is_file(), f'VOICE.md 链接不存在：{target}')
            self.assertIn('config/model-catalog.json', local_links)
            self.assertIn('config/voice.example.json', local_links)
            self.assertIn('兼容说明（Skill references/migration.md）', guide)
            self.assertIn('制作契约（Skill references/production.md）', guide)
            self.assertIn('制作流程（Skill references/production.md）', guide)
            self.assertIn('[MLX 模型页](https://huggingface.co/', guide)
            self.assertFalse((project / 'references').exists())


@unittest.skipUnless(shutil.which('ffprobe'), 'requires FFprobe')
class SpeechTimelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name)
        self.f = film(); self.save()

    def tearDown(self):
        self.tmp.cleanup()

    def save(self):
        p.write(self.root/'film.json', self.f)

    def audio(self, job, seconds, *, sidecar=True, legacy=False):
        file = self.root/job['voice']; file.parent.mkdir(parents=True, exist_ok=True)
        sr = 8000
        samples = array.array('h', (round(2000*math.sin(2*math.pi*440*i/sr)) for i in range(round(seconds*sr))))
        with wave.open(str(file), 'wb') as w:
            w.setparams((1, 2, sr, 0, 'NONE', 'not compressed')); w.writeframes(samples.tobytes())
        if sidecar:
            record = dict(text=job['text'], audioSha256=p.digest(file))
            if not legacy:
                record['speechRequestSha256'] = speech.request_fingerprint(job)
            p.write(file.with_suffix('.wav.json'), record)
        return file

    def voices(self):
        jobs = speech.scene_utterances(self.f, self.f['scenes'][0])
        self.audio(jobs[0], .51); self.audio(jobs[1], .76)
        return jobs

    def test_measured_turns_and_pauses_drive_frames_and_caption_ownership(self):
        self.voices(); t = p.compile_timeline(self.root, True)
        first, second = t['speech']
        self.assertEqual((first['voiceStartFrame'], first['voiceFrames'], first['pauseAfterFrames']), (3, 16, 4))
        self.assertEqual((second['voiceStartFrame'], second['voiceFrames']), (23, 23))
        self.assertEqual(t['totalFrames'], 49)
        self.assertIsNone(t['scenes'][0]['voice']); self.assertEqual(t['scenes'][0]['voiceFrames'], 0)
        self.assertEqual({c['speakerId'] for c in t['captions']}, {'hero', 'narrator'})
        self.assertEqual({c['utteranceId'] for c in t['captions']}, {'u-one', 'u-two'})
        for cap in t['captions']:
            track = next(x for x in t['speech'] if x['utteranceId'] == cap['utteranceId'])
            self.assertTrue(track['voiceStartFrame'] <= cap['startFrame'] < cap['endFrame'] <= track['voiceStartFrame']+track['voiceFrames'])

    def test_new_role_or_performance_rejects_old_audio_even_if_marked_external(self):
        self.voices()
        for change in [('role', lambda: self.f['cast']['hero'].update(voiceId='actor-b')),
                       ('performance', lambda: self.f['scenes'][0]['utterances'][0].update(performance={'instruct':'欣喜'}))]:
            original = copy.deepcopy(self.f); change[1](); self.f['scenes'][0]['utterances'][0]['externalVoiceVerified'] = True; self.save()
            with self.subTest(change=change[0]), self.assertRaisesRegex(ValueError, '请求已过期'):
                p.compile_timeline(self.root, True)
            self.f = original; self.save()

    def test_new_dialogue_requires_bound_sidecar_or_explicit_external_verification(self):
        jobs = self.voices(); file = self.root/jobs[0]['voice']; record = file.with_suffix('.wav.json')
        d = p.read(record); d.pop('speechRequestSha256'); p.write(record,d)
        with self.assertRaisesRegex(ValueError, '请求已过期'):
            p.compile_timeline(self.root, True)
        record.unlink()
        with self.assertRaisesRegex(ValueError, '核对台词'):
            p.compile_timeline(self.root, True)
        self.f['scenes'][0]['utterances'][0]['externalVoiceVerified'] = True; self.save()
        self.assertTrue(p.compile_timeline(self.root, True)['locked'])

    def test_limit_never_truncates_multiple_voices(self):
        self.voices(); self.f['maxSeconds'] = 1; self.save()
        with self.assertRaisesRegex(ValueError, '不能裁切'):
            p.compile_timeline(self.root, True)

    def test_output_paths_cannot_escape_project(self):
        self.f['scenes'][0]['utterances'][0]['voice'] = '../outside.wav'; self.save()
        with self.assertRaisesRegex(ValueError, '位于项目内'):
            p.compile_timeline(self.root)

    def test_legacy_timeline_shape_and_values_are_unchanged(self):
        self.f = dict(schema=p.SCHEMA, width=640, height=360, fps=30,
                      scenes=[dict(id='one', visualSeconds=.1, leadSeconds=.1,
                                   tailSeconds=.1, narration='旧旁白。')])
        self.save(); job=speech.scene_utterances(self.f,self.f['scenes'][0])[0]
        self.audio(job,.5,legacy=True); t=p.compile_timeline(self.root,True)
        self.assertNotIn('speech',t); self.assertNotIn('cast',t)
        self.assertEqual(t['totalFrames'],21)
        self.assertEqual(t['scenes'][0]['voiceFrames'],15)
        self.assertEqual(t['captions'],[{'text':'旧旁白。','startFrame':3,'endFrame':18}])

    def test_mixed_projects_include_legacy_voice_once(self):
        self.voices(); legacy=dict(id='legacy',visualSeconds=.1,leadSeconds=0,tailSeconds=0,narration='旁白')
        self.f['scenes'].append(legacy); self.save()
        job=speech.scene_utterances(self.f,legacy)[0]; self.audio(job,.5,legacy=True)
        t=p.compile_timeline(self.root,True)
        self.assertEqual(len(t['speech']),3)
        self.assertEqual(t['speech'][-1]['speakerId'],'narrator')
        self.assertEqual(t['scenes'][-1]['voice'],'audio/legacy.wav')

    def test_missing_configuration_or_system_say_does_not_flatten_dialogue(self):
        fake=types.SimpleNamespace(discover_config=lambda *_:None)
        with patch.dict(sys.modules,{'voice':fake}),patch.object(p,'tts') as system:
            with self.assertRaisesRegex(ValueError,'需要声音配置'):
                p.default_tts(self.root)
            with self.assertRaisesRegex(ValueError,'不支持逐角色'):
                p.default_tts(self.root,system_voice='Tingting')
            system.assert_not_called()

    def test_cli_locked_timeline_requires_every_dialogue_asset(self):
        self.voices(); p.write(self.root/'assets.json',dict(schema='code-animation-assets/v1',assets=[],links=[]))
        p.asset_review.seal(self.root)
        result=subprocess.run([sys.executable,str(ROOT/'scripts/pipeline.py'),'timeline',str(self.root),'--lock'],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('未登记',result.stderr)
        self.assertFalse((self.root/'timeline.json').exists())

    @unittest.skipUnless(shutil.which('ffmpeg'), 'requires FFmpeg')
    def test_real_mix_uses_dialogue_tracks_without_duplicating_legacy_scene_voice(self):
        self.voices(); legacy=dict(id='legacy',visualSeconds=.5,leadSeconds=0,tailSeconds=0,narration='旁白')
        self.f['scenes'].append(legacy); self.save()
        job=speech.scene_utterances(self.f,legacy)[0];self.audio(job,.5,legacy=True)
        assets=[]
        for file in sorted((self.root/'audio').iterdir()):
            assets.append(dict(id='a-'+file.name.replace('.','-'),path=str(file.relative_to(self.root)),sourceUrl=None,
                               license='synthetic test',useBasis='dialogue mix regression'))
        p.write(self.root/'assets.json',dict(schema='code-animation-assets/v1',assets=assets,links=[]));p.asset_review.seal(self.root)
        p.write(self.root/'timeline.json',p.compile_timeline(self.root,True));p.mix(self.root)
        self.assertEqual(p.read(self.root/'audio/mix-report.json')['tracks'],3)
        t=p.read(self.root/'timeline.json')
        with wave.open(str(self.root/'audio/mix-master.wav')) as w:
            self.assertEqual(w.getnframes(),round(t['totalFrames']*48000/30))
            w.setpos(round((t['durationSeconds']-.2)*48000));values=array.array('h',w.readframes(2000))
            self.assertGreater(max(map(abs,values)),100)


@unittest.skipUnless(shutil.which('node'), 'requires Node')
class RuntimeSpeechTests(unittest.TestCase):
    def test_active_role_resets_on_seek_and_sentence_pauses(self):
        script=r'''
const fs=require('fs'),vm=require('vm');
const timeline={width:640,height:360,fps:30,totalFrames:10,durationSeconds:10/30,locked:true,
 scenes:[{id:'one',startFrame:0,endFrame:10,durationFrames:10,voice:null,voiceFrames:0}],captions:[],
 speech:[{speakerId:'a',utteranceId:'u-a',voiceStartFrame:2,voiceFrames:3},
         {speakerId:'b',utteranceId:'u-b',voiceStartFrame:6,voiceFrames:2}]};
const ctx={reset(){},save(){},restore(){}};const nodes={};for(const id of ['#seek','#time','#audio','#play'])nodes[id]={pause(){}};
nodes['#stage']={getContext:()=>ctx};const seen=[];
const window={drawScene:async(_,o)=>seen.push([o.frame,o.activeSpeakerId,o.activeUtteranceId,o.speech?.speakerId??null])};
const box={window,console,URLSearchParams,location:{search:'?export=1'},document:{fonts:{ready:Promise.resolve()},body:{classList:{toggle(){}}},querySelector:id=>nodes[id]},fetch:async url=>({ok:true,json:async()=>url==='assets.json'?{links:[]}:timeline}),requestAnimationFrame(){}};
(async()=>{await vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),box);for(const f of [2,4,5,6,7,8,2])await window.renderFrame(f);process.stdout.write(JSON.stringify(seen));})();
'''
        out=subprocess.check_output(['node','-e',script,str(ROOT/'assets/starter/runtime.js')],text=True)
        actual=json.loads(out)
        self.assertEqual([x[1] for x in actual],[None,'a','a',None,'b','b',None,'a'])
        self.assertEqual([x[2] for x in actual],[None,'u-a','u-a',None,'u-b','u-b',None,'u-a'])
        self.assertTrue(all(x[1]==x[3] for x in actual))


if __name__=='__main__':unittest.main()
