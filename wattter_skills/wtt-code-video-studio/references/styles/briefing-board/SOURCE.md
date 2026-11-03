> 上游方法原文：Lemomo / Lemo-Opuscar，MIT，固定版本 `bebbbe1aa92a3cb4bb6f83500e61b23a17d1aa00`。本文件为参考资料；本库执行规则以同目录 STYLE.md 和主 SKILL.md 为准。示例题材、品牌、字幕语言、次数、片长与外部工具路径不作为本片要求。

# Engineering Briefing Board — Style Prompt

> One real whiteboard wall, filmed: window light on enamel, ghosts of erased marker, frame and tray. Cut-out photographs of real things land on it with weight; tags, magnets, a ruler and stamps are pinned to it; marker ink draws itself in three colours with fixed meanings. The camera rides the lines from fact to fact and only at the end pulls back to show the whole briefing.
> References (grammar only): explainers filmed on a map wall; the long pull-back over a wall covered in work; drafting conventions (plan above elevation, dimension lines, hatching). Never copy them or name them in the film.

## 1. Essence, and what it is not

1. **A physical board in a room**: enamel, window falloff, a sliding reflection, ghosts of earlier work, frame and tray.
2. **Real things on it**: cut-out photographs of the real objects, a few millimetres off the board, shadowed by one window, parallaxing. They are evidence: never a generated image presented as a real object.
3. **Ink that means something**: graphite for names and rules, blue for water and measurement, red only for the decision; rejected ideas erased to ghosts.
4. **One continuous wall**: no pages; the camera travels along lines, projections and leaders.
5. **The whole wall, once**: every shot is a crop of the final briefing, seen whole only in the last pull-back, as a poster.

Not **Whiteboard Explainer** (a hand drawing line art on a flat page): the board is a filmed object, subjects are photographs. Not **Data Storytelling**: comparisons are dimension lines in real units beside real objects. Not a keynote: no headers, centred bullets, page turns.

## 2. Materials & rendering

- **Board (z 0)**: procedural enamel, wiped ghost strokes, smudges, a window falloff, a sliding diagonal reflection; the frame shadows a warm grey wall.
- **Ink (multiply)**: flat colour at about 90 %, lighter core, round caps, a wet-tip glint on the stroke being drawn. Lettering: a marker font revealed glyph by glyph with seeded tilt and baseline jitter. Erasing leaves a blurred ghost (about 7 %).
- **Prints (z ≈ 6–14)**: photographs cut out at full resolution (a matting model, or a hand polygon / mask), clean edges, one shared grade (lower saturation, a touch warmer, lifted blacks). Thin structure (cables, wires, masts, railings) is measured in the photo and redrawn as clean lines in one colour. Shadow = blurred silhouette along one light vector, softer the higher the object. **No frame upsamples a photo**: ≥ 1 source px per screen px at its largest, measured; cap the zoom or find a bigger source.
- **Secondary layer** (only where the camera never goes before the end): the photos as pinned prints, a source card, sums on sticky notes, a small sketch. Texture and proof for the final wall, lighter than the main line.
- **Props (z ≈ 8–26)**: magnetic tags, magnets, a steel ruler, printed cards, a pitted stamp impression; the tray (z 70) nearest the lens.
- **Camera**: parallax by height, sub-frame motion blur (180° shutter), light grain. Only subtitles are screen-space.

## 3. Colour logic

- Ground: the enamel and its light falloff; the wall around is neutral warm grey.
- Ink: graphite = names, rules, facts; blue = water and measurement (dimensions, projection lines, measured numbers); red = the decision (a rejection, the key word of a verdict, the one mark to notice); grey for drafting only (extension lines, hatching).
- Red is rare: two or three red marks per frame at most, never on a red object. Full colour belongs to the photographs; props stay neutral; a red magnet is a verdict.

## 4. Type & subtitles

- **Marker lettering**: a single-weight marker face covering every script the film uses (ours: LXGW Marker Gothic, OFL, subset — re-run when words change). Content 100–160 board px; a verdict 230–400.
- **Printed labels** (tags, cards, stamps): a sturdy sans; credit lines in a monospace. A tag holds one to three words.
- **Subtitles**: a frosted acrylic strip at the bottom centre with a blue marker tick. If the film is bilingual, the film's language sits on top. **One line per language**: `nowrap`, measured in the page against a 1,500 px safe width; a long line becomes two cues. Key content stays above the strip (bottom 15 %).
- **Reading time**: subtitles ≥ max(1.8 s, speech + 0.6 s); board text stays fully in frame for CJK ÷ 4.5 + other ÷ 15 + 1.5 s from when it appears. In the final wall, text meant to be read is ≥ 20 px on screen.

## 5. Motion quality

- 24 fps on ones; nothing is stepped.
- Camera: overlapping eased moves, velocity ∝ u^a (1−u)^b (a, b ≈ 1.5–4), so speed and acceleration never jump; b > a gives inertia. A hand-held breath (≤ 3 px) underneath; shake only on an impact.
- Weight: prints are lowered from the camera side, land, bounce and settle as the shadow tightens; magnets clack on to pin them; tags swing; removed magnets pop toward the lens; struck things jolt and spring back. The camera may meet a landing close, briefly, on the object's most telling detail, then pulls out.
- Blurred in motion, sharp where words are read. Every 1–2 beats something lands, draws or swings; only silences and judgement holds go still.
- Ink draws at the speed of a hand; dimension lines land with an arrowhead tap.
- Never: dissolves, scale-pops on text, bouncy UI easing, text fading in by itself.

## 6. Camera grammar

| Move | What it expresses | Can serve |
|---|---|---|
| Ride a line (with the pen or a dimension) | measuring; "how far does it go?" | lengths compared; a route; a timeline |
| Tilt along projection lines | the same quantity in another view | plan → elevation; a total → its parts |
| Slow push-in, slight Dutch tilt | tension, an approaching problem | a collision; a deadline; an overrun |
| Pull back and sideways | stepping back to state a rule | a constraint; a turn in the argument |
| Whip with the line, overshoot, settle | a result that exceeds | a record; an outlier |
| Rise along a leader line | from evidence to verdict | a conclusion; a recommendation |
| Staircase framing (each new item with the previous result) | comparison in sequence | rankings; tests; options |
| Judgement frame: the whole item, the limit and the verdict, held ≥ 2.5 s | a test the viewer can check | pass / fail against a threshold; a budget against a cap |
| Long pull-back to the whole wall | scale; everything at once | the end of an argument; a summary |

Framing: off-centre, cropped, close. The first frame holds a readable subject; the first strong action hits within 0.5 s. Items tested against a limit each get a judgement frame (wider each time if they grow); the verdict lands after the camera settles. Before the reveal: ≤ about 60 % of the board's width, never both side edges, never the reveal's zone. Transitions are moves; no cuts, fades or zoom-to-fit.

## 7. Sound palette

- Room: an air-conditioning bed and traffic through the window, about 20 dB under the voice — audible, not a hiss; silences keep only this.
- Foley: felt-tip squeaks scaled to stroke length, nib taps, magnet clacks (a pitch per magnet in a row), suction pops, print landings (board thump, paper slap), a ruler's ring, eraser felt, a stamp's thud.
- The subject's own sound arrives early as a J-cut; the first sound after a silence is an impact or the subject's sound.
- Music: a small rhythmic ensemble, walking to brisk — bass, a light kit, wooden percussion, low brass stabs for verdicts (or mallets); no piano-and-strings pad. Landings, stamps and arrows sit on the beat. Voice calm, briefing-room confident, about 8–10 dB over the music; −14 LUFS.

## 8. Native moves

- **The whole-wall reveal.** Design the wall as a poster first (hierarchy, reading path, filling the frame), then plan every shot as a crop of it; keep one zone (secondary layer, verdict, title card) for the reveal alone. *Fits:* a product roadmap; a household budget.
- **The subject passes through the answer.** The real thing moves through the chosen solution, its sound first. *Fits:* a parcel along the chosen route; a train over the new viaduct.
- **Ride the dimension line.** A quantity drawn as a real length to one scale; the camera rides the tip. *Fits:* battery ranges of four cars.
- **Projection lines.** Dashed lines carry an edge from one view to another so two drawings share a scale. *Fits:* a trail map above its elevation profile.
- **Magnets as countable things.** Units clack on in rhythm, pop off when a rule removes them. *Fits:* seats in a vote.
- **Erase to a ghost.** A rejected idea wiped but faintly visible. *Fits:* last year's plan under this year's.
- **The stamp.** A verdict lands with a thud and a jolt. *Fits:* passed / failed tests.
- **The physical answer.** A real prop laid down as the solution. *Fits:* one cable instead of five.
- **Leader to the verdict.** An arrow from the deciding number to the conclusion. *Fits:* the bottleneck in a process.

## 9. Pitfalls of the medium

- **Text glimpsed in passing** fails the reading time. Fix: words where the camera rests; frame each new item with the last result.
- **Only close-ups.** The viewer never sees the whole object against the limit. Fix: detail → judgement frame → hold → verdict → move on.
- **Photos that don't belong together.** Fix: one grade, one light vector, one viewpoint family.
- **Thin parts lost or stair-stepped** by the matte. Fix: key them against the clean background, redraw clean lines at the measured positions.
- **Upsampled photos** go soft in close-ups. Fix: full-resolution cuts, large sources, a per-frame check.
- **Lettering in photos** (signs, names, logos). Fix: paint out, cut, or choose another photo.
- **The wall seen too early** spends the ending; **a sparse or tiny final wall** wastes it. Fix: measure every frame's visible share; size the hierarchy for the poster; a quiet secondary layer, no empty middle.

## 10. Sources, facts, engine

- **Photos**: Wikimedia Commons (read each file page's licence and author), national libraries and archives (e.g. the Library of Congress: check each item's rights statement), agency media pages, Flickr Commons. Fine: CC0, public domain, CC BY (credit it). CC BY-SA, "no known restrictions" (≠ CC0) or other terms: name them to the user and ask first. For the user's own product, site or people, ask for their photos. No licensable photo of a real thing → draw it in marker as a sketch; never a generated image presented as the real object.
- **Facts**: keep a `FACTS.md` in the project folder (each claim on screen or in the voice, its source URL, the quoted wording, or the measurement method) and deliver it with the film. List every photo in `CREDITS` with source, author and licence.
- **Extra packages and packs** (beyond `setup.sh deps voice music`): `onnxruntime` and the BiRefNet-general matting model (MIT, ~970 MB: https://github.com/danielgatis/rembg/releases/download/v0.0.0/BiRefNet-general-epoch_244.onnx, path in `$BIREFNET_ONNX`) for cut-outs; `fonttools` only to subset CJK fonts offline. The agent installs them itself into a private venv in the project folder (`demo/kit/tools/kit_env.sh` does venv and model), never into `$LIB/.venv`. Without the model: cut with `prep_object.py --poly` (hand polygon) or `--mask` (a mask image).
- **Engine** (copy into the project): `demo/kit/board.js` (camera, prints, tags, magnets, ruler, cards, stamp, ink, erasing, `sceneTexts(t)`, `subCheck()`; fields in `demo/kit/README.md`), `demo/kit/batch.mjs` (stills), `demo/kit/tools/` (cut-outs, line redraws, lettering wipe, prints, fonts), checks in `demo/tools/` (`camcheck.mjs` visible share and judgement frames, `rescheck.mjs`, `subcheck.mjs`).

A minimal world (`node demo/kit/batch.mjs park.json`; `fetch_fonts.py park.json` first for new characters):

```json
{ "dur": 6, "t": 5.5, "board": { "w": 4000, "h": 2400 }, "hand": 0, "cam": { "x": 1500, "y": 1000, "z": 0.8, "moves": [] },
  "elements": [
    { "type": "tag", "text": "地下车库", "xy": [560, 800], "size": 60, "arrive": { "t": 0.2, "kind": "swing" } },
    { "type": "ink", "kind": "dim", "from": [700, 900], "to": [1300, 900], "color": "blue", "t": 0.6, "d": 0.6 },
    { "type": "ink", "kind": "write", "text": "120 米", "xy": [1360, 940], "size": 100, "color": "blue", "t": 1.2 },
    { "type": "stamp", "text": "首选", "xy": [1500, 700], "size": 110, "rot": -8, "t": 4.2 } ] }
```

## 11. Variation space

The agent decides per film: structure, which objects are photographed, plan vs elevation, the wall's reading path, opening, ending, camera path, pacing.

- **Three structures:** one measurement that keeps growing until it breaks a limit; a before/after where the erased first plan stays as a ghost under the second; a checklist stamped item by item as the camera moves down the wall.
- **Three openings:** a stamp on a finished drawing, then back to see why; one number written large, then the line that measures it; a photo dropped onto an empty corner.
- **Three endings:** the wall revealed with the answer circled; back to the opening mark, now corrected; the last tag flipped from a question to an answer, then the pull-back.

---

How our demo was made (story, shots, score, title card, build): [DEMO.md](https://github.com/lemomo-ai/lemo-opuscar/blob/bebbbe1aa92a3cb4bb6f83500e61b23a17d1aa00/styles/briefing-board/DEMO.md). Read it after your treatment exists.
