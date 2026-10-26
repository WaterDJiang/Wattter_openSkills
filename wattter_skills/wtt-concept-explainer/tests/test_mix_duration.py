"""Real FFmpeg regression: loudnorm must preserve fractional-frame audio tails."""
import array
import json
import math
from pathlib import Path
import shutil
import struct
import sys
import tempfile
import unittest
import wave

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import pipeline as p


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'requires FFmpeg')
class MixDurationTests(unittest.TestCase):
    def test_normalization_preserves_frame_duration_and_last_sound(self):
        for total_frames in (82, 201, 5152):
            with self.subTest(total_frames=total_frames), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp); (root / 'audio').mkdir()
                fps = 30; duration = total_frames / fps
                # A real 1s tone ends two frames before the timeline, including the long-film case.
                source = root / 'audio/tone.wav'; sr = 24000
                with wave.open(str(source), 'wb') as w:
                    w.setparams((1, 2, sr, 0, 'NONE', 'not compressed'))
                    w.writeframes(b''.join(struct.pack('<h', round(4500 * math.sin(2 * math.pi * 440 * i / sr))) for i in range(sr)))
                p.write(root / 'film.json', {'schema': p.SCHEMA, 'width': 640, 'height': 360,
                    'fps': fps, 'scenes': [{'id': 'test', 'narration': '', 'visualSeconds': duration}],
                    'audioTracks': [{'file': 'audio/tone.wav', 'startSeconds': (total_frames - 32) / fps, 'gain': .5}]})
                p.write(root / 'assets.json', {'schema': 'code-animation-assets/v1', 'assets': [
                    {'id': 'tone', 'path': 'audio/tone.wav', 'sourceUrl': None, 'license': 'synthetic test', 'useBasis': 'duration regression'}], 'links': []})
                p.asset_review.seal(root)
                t = p.compile_timeline(root, True); p.write(root / 'timeline.json', t)
                p.mix(root)
                with wave.open(str(root / 'audio/mix-master.wav'), 'rb') as w:
                    self.assertEqual(w.getframerate(), 48000)
                    self.assertLessEqual(abs(w.getnframes() - round(t['durationSeconds'] * 48000)), 1)
                    # Check audible final tone, rather than accepting a correctly sized silent file.
                    w.setpos(round((duration - .2) * 48000))
                    samples = array.array('h', w.readframes(2400))
                    self.assertGreater(max(abs(x) for x in samples), 100)


if __name__ == '__main__': unittest.main()
