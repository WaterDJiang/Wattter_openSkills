> 上游方法原文：Lemomo / Lemo-Opuscar，MIT，固定版本 `bebbbe1aa92a3cb4bb6f83500e61b23a17d1aa00`。本文件为参考资料；本库执行规则以同目录 STYLE.md 和主 SKILL.md 为准。示例题材、品牌、字幕语言、次数、片长与外部工具路径不作为本片要求。

# Constructivist Montage — Style Prompt

> Real archive footage, photographs and documents, printed as one ink-and-paper poster with a single red, and cut on a machine beat. Diagonal bands carry the type; windows cut along the axis hold the film; people are scissored out of photographs and stacked into structures; numbers count, documents are marked in red, and two images collide to make a third idea.
> References (grammar only): Soviet montage cinema of the 1920s (city symphonies with split screens, counting and machine rhythm; "intellectual" montage where A + B yields a concept), constructivist posters and photomontage (red / black / paper, steep diagonals, photo cut-outs with geometric blocks, type as structure). Never copy their shots, layouts, slogans or lettering, and never name them in the film.

## 1. Essence, and what it is not

1. **Evidence, recut.** Every picture is real material (archive film, photographs, documents) about the actual subject. The film's argument comes from how they are cut and set, not from illustration.
2. **One printed sheet.** All material is converted to the same two-tone print (warm ink → paper); red is the only colour and is laid on top as a printed element.
3. **The beat is the editor.** Cuts, slams, wipes and counts sit on a 120 BPM grid (or the score's tempo); sections accelerate by halving shot length.
4. **Type is structure.** Words and numbers are beams: on a −18° band, as solid blocks, stacked vertically. Never floating captions.
5. **The collective over the individual.** Crowds, hands, machines and many small figures; a single face is never the protagonist.

Not **Data Storytelling** or a keynote: no centred headline with bullets, no slide transitions, no header bars; data appears as marked documents, counters and measured bars inside the composition. Not **Swiss Motion Graphics**: asymmetric, diagonal, no grid of white space, no thin rules as decoration. Not **Art Deco** or **60s Spy Titles**: no gold, no fine lines, no jazz. Not a museum slideshow: archive material is never shown "as is" in a neutral frame; it is cut, windowed, stacked and counted.

## 2. Materials & rendering

- **Four kinds of element only**: **bands** (red or ink, along the axis), **windows** (rectangles or parallelograms holding film or photographs), **cut-outs** (people scissored from photographs with a paper-white border), **type blocks**. Plus one paper-fibre texture over everything.
- **The print grade** (one function for film, photos and documents): luminance → percentile stretch (film: one pair of percentiles per clip, so it never pumps; 0.7 / 99.5; photos 0.8 / 99.4) → S-curve `x + s·(x−0.5)·(1−|2x−1|)·2`, s = 0.32 (documents 0.18, they keep their paper) → map to ink→paper: `rgb = INK + (PAPER − INK)·g`. Archive film keeps a ±2.5 % per-frame flicker inside its window (`hash(frame)`), photographs and documents do not.
- **Cut-outs**: a person-segmentation model (u2net_human_seg via onnxruntime) → threshold 0.5 → median filter → largest component → 7 px paper border dilated outside the mask. The border is the medium's own look and hides the model's edge errors. Group photos rarely segment cleanly: use them whole in windows.
- **Documents**: scans at full resolution, never retyped. They are marked: a red highlighter bar in `multiply` over the exact sentence, a hand-drawn red ellipse round a heading, a red circle on a map. Drawings on a document (a chart, a map) may be lifted off the page and reused, keyed from their paper (`alpha = (205 − luminance) / 90`).
- **Resolution ceiling**: archive film ≤ 2.5× its source pixels on screen, modern footage ≤ 1.5×, photos ≥ 1 source px per screen px where possible. Prepare clips with `hqdn3d → lanczos → light unsharp` before grading; add grain only in the mux. A 720-line film transfer can fill a 1,700 px window, not a full 1080p frame: frame it (a window, a split strip, an iris) instead of stretching it.
- **Paper fibre**: a fixed seeded noise canvas multiplied over the frame at α 0.5; film grain 4 added by `mux.sh`.

## 3. Colour logic

| Role | Value | Use |
|---|---|---|
| Red | `#D52B1E` | bands, wedges, blocks, the key number, marker bars, circles and leaders, the one winner in a comparison |
| Ink | `#141210` | type, beams under each floor, window borders, dark grounds |
| Paper | `#EDE4D0` | ground, reversed type, cut-out borders |

- Everything photographic is ink-on-paper; nothing else has colour. Red is never laid on red: a red block on a red ground becomes ink.
- Alternate grounds to make cuts land: paper scene → ink scene → paper. In an acceleration the background itself alternates red / ink per cut.

## 4. Type & subtitles

| Use | Face | Size (1080p) |
|---|---|---|
| Chinese display, slogans | Noto Sans SC 900 (subset) | 110–210 px; stacked vertically 170 px per character |
| Numbers, English display | Oswald 600–700 | numbers 230–440 px; English lines 30–62 px, letter-spacing 2–10 px, capitals |
| Source and footage tags | Space Mono Bold (CJK falls back to Noto) | 17–18 px on an ink or red tab, padding 6 |
| Subtitles | Noto Sans SC 700 40 px over Oswald 500 28 px | bottom left, ink bar at 90 %, a 10 px red tick |

- **Bilingual pairs**: Chinese block, then one English line in Oswald directly under it (or on the neighbouring band). Each language one line, measured.
- **Placement**: along the −18° axis on a band, or as an ink / red block; never centred on the frame, never a header. Numbers can be bigger than the words that explain them.
- **Tags**: every archive window carries its footage tag (`FILM · <TITLE> · <PLACE> <YEAR>`, `PHOTO · <AUTHOR> <YEAR>`), every fact a source tag (`来源 · <PUBLISHER> <YEAR>`). If the footage is not of the subject itself, the tag says what it really is.
- **Subtitles** stay bottom-left in a 960–1056 px strip; key type keeps above y 930 while narration runs. Subtitles hold ≥ max(1.8 s, speech + 0.6 s). On-screen text follows `readcheck.mjs` (CJK ÷ 4.5 + other ÷ 15 + 1.5 s, fully in frame); a comparison holds every item ≥ 2.5 s before its verdict.

## 5. Edit grammar

- **Grid**: one tempo for picture and score (120 BPM: beat 0.5 s, bar 2 s). Every cut, slam, wipe and count lands on a beat, half-beat or sixteenth. The page exports these times as `window.EV`; the mix reads the same list.
- **Shot length**: 0.5–2 s for footage; one idea per shot. A section may accelerate by halving: 0.5 → 0.25 → 0.125 s (never shorter than 3 frames). Holds are reserved for reading: a text block, a freeze, a comparison.
- **Cut rule**: adjacent shots conflict in at least one of direction (left slam / right slam), value (paper / ink ground), or geometry (diagonal band / upright window). Never two paper documents in a row.
- **Nothing static for more than a second**: inside a hold something moves (film in its window, a counter, a slow push, a frame-within-the-frame). Planned exceptions only: the comparison hold, one silence beat, the end card.
- **Transitions inside the medium** (pick per cut, don't fade):
  - *red wipe*: a 260 px red band at 72° (perpendicular to the axis) sweeps the frame in 0.25 s, the next scene revealed behind it; it lands on the downbeat;
  - *iris*: a red marker circle drawn on a map or photo becomes an aperture and opens onto footage;
  - *slam*: the next element arrives from outside along the axis in 0.08–0.2 s, ease-out, hard stop, frame shake (amplitude 3–18 px, `exp(−14·Δt)`);
  - *flash cut*: one frame of 50–80 % paper over a window at a cut or freeze;
  - *hard cut on the beat* between grounds of opposite value;
  - *jump-in*: inside a freeze, a cut to a 1.2× crop of the same frame, the annotation scaling with it.
- **Two silences**: one where the orchestra stops and only an original recording remains, and one true half-bar of nothing (ink frame, one red dot) before the heaviest hit.

## 6. Formats (each is a function in `demo/index.html`)

| Format | How it looks | How it is built |
|---|---|---|
| **Title package** | a red band slams along the axis; a window cut to the band's edge runs footage; digits stamp one per eighth, the CJK unit in red | `S1`: window clipped to the band's top edge (`onBar`), digits measured and slammed individually, `reg()` registers the group for readcheck |
| **Lower third** | a red bar from the left edge with Chinese, an ink tab with the English | 92 px bar at y ≈ 760–850, slams in 0.14 s, slides off with the next transition |
| **Map + iris** | a document map pushes in, a red circle is drawn round the place, the circle opens onto the site | `mapXf()` (scale / focus / angle over time), `mapToScreen()` keeps the circle on the map point; aperture = `arc` clip whose radius grows to the frame |
| **Vertical title** | CJK characters stacked top to bottom beside a tall window, English rotated 90° | per-character slams 1/16 apart |
| **Date on a girder** | the date in paper on a red band crossing the footage | text placed on the band's centre line (point + normal offset), rotated by the axis |
| **Grid** | 3 × 3 windows light one per sixteenth in a spiral, the centre counts 1…9 and lights last in red | cells `back()`-scale in, each a different clip at 1.4–1.8× speed, ping-pong |
| **Split strips** | the frame rotated to the axis, three strips of two panels each; one panel changes per beat; strips drift in opposite directions | panels ≤ 1,160 px wide so the film stays ≤ 2.5×; red seam on the middle strip |
| **Freeze + annotation** | flash, freeze, push; a red ellipse drawn on the object, a leader to a red block with the number; a jump-in; the film keeps running in a small red-framed inset | the circle is computed from the zoom focus so it follows the jump; inset = same clip, live |
| **Document close-up** | a tilted page slams in, a red marker bar crosses the exact sentence, a red block repeats the number huge | marker in `multiply` over the scan's own line coordinates; a tall slot beside it runs footage fast to show speed |
| **Process staircase** | three windows rising along a diagonal, red triangles between them, a counter climbing to the claim | each window 0.75 s apart; the counter is graphic, only its end value is a fact |
| **The question** | a document heading on an ink ground, circled in red; a huge red "?" | heading cropped tight so only the words that matter show |
| **Acceleration + count** | full-frame windows tilted ±4–6°, ground alternating red / ink, a four-digit counter jumping per cut | cut list with shrinking durations; the original sound plays alone |
| **Multiple exposure** | top-down footage, a second clip in `screen` at 45 %, cut-outs in `multiply`, the answer in a block | exposure window ≤ 1,700 px on a red ground |
| **Chart from the document** | the page turns 90°, its drawings lift off and stand on one ground line to scale, red dimension lines, numbers, names; held; then the verdict block | outlines keyed from the scan, scaled so tip-to-ground = value × px per unit; the winner tinted red (`source-in`) |
| **Photomontage tower** (signature) | floors of footage strips slam in from alternate sides every sixteenth, an ink beam under each, a cut-out worker lands on every other; the camera climbs; a crown and a figure on top | `FLOORS` list, camera `y` follows the eased count of built floors; the floor counter runs to the dated anchor, **rests there while its caption is up**, then runs on to the end value |
| **Silence beat** | ink frame, one red rivet | half a bar; the score and foley are gated to zero |
| **Result composition** | huge numbers left, a tall slanted window with the finished subject (camera tilts up it), a tilted photo, a red wedge | numbers slam, the last line restamps the key number on red |

## 7. Sound palette

- **Score**: an original machine ostinato (eighths, minor, e.g. D–D–F–D–A–D–E–F) in spiccato cellos + staccato bassoon, staccato tuba / trombone on the beat, snare sixteenth taps, xylophone for counts (one rising note per lit cell or built floor), horn / trumpet stabs and a short brass motif, timpani rolls into section changes, gran cassa + gong on the heaviest hit. Sampled CC0 libraries (VSCO 2 CE, VCSL). No piano-and-strings bed.
- **Original sound alternates with music**: in one section the orchestra stops and a real recording (a rivet gun, a machine, a crowd) carries the cut alone, each burst trimmed to its shot. Bring it in a beat early (J-cut).
- **Foley for every printed action**: slam = low thump + steel clank; stamp = thump + clack; wipe and iris = whoosh; marker = filtered noise scrub; paper = band-passed rustle; floors and cells = pitched clanks.
- **Layers**: ambience (a real site / street recording, about 20 dB under the voice, out for the silence), foley ducked 35 % under speech, music ducked 70 % under speech (≈ 10 dB under the voice), narration compressed and levelled by RMS. Master to −14 LUFS with the peaks limited to −1.8 dBFS before `mux.sh`, and a 25 ms fade at sample 0 (an AAC encode overshoots on a hit at the first sample).
- **Narration** (when the film has one): short declarative lines, newsreel cadence, never more than one sentence over a format; numbers spelled out for TTS, digits in subtitles.

## 8. Native moves

1. **The document is marked, not quoted**: the actual sentence on the scan gets a red bar; the number then becomes a red block.
2. **The document becomes the chart**: drawings printed on a page are lifted off, turned and stood on a ground line to scale.
3. **A + B → idea**: two kinds of image alternate faster and faster (the machine / the hands; a heading / the people it leaves out) until a card or a number states what the collision meant.
4. **Count the many**: a counter driven by the cuts, a grid that fills cell by cell, a tower floor by floor.
5. **People build the structure**: cut-out figures stacked into the thing they made (photomontage).
6. **Silence, then the heaviest hit** into the result.

## 9. Footage

1. **Ask first.** Before searching, ask the user for their own material: film, video, photographs, scans of documents (reports, brochures, letters, minutes), data. What they give leads; archives fill gaps.
2. **Where to look, and how to judge the licence** (`demo/tools/footage.py` searches, downloads and records licence, author and source page into `SOURCES.jsonl`; `footage.py md` writes `SOURCES.md`):
   - **Internet Archive**: read each item's `licenseurl` and description. Public Domain Mark / CC0 / CC BY are usable; *no licence field* is not. For a pre-1978 US film, check the title and end cards for a copyright notice: published 1930 or earlier = public domain in the US by date; published without notice before 1978 = public domain; with a notice, check renewal. Corroborate date and producer elsewhere (a library catalogue, an archive exhibit). Avoid YouTube mirrors, re-uploads with no provenance, colourised or "restored" versions.
   - **Wikimedia Commons**: read the file page's licence and its source institution. Public domain, CC0, CC BY (credit in full) are usable; CC BY-SA is not used in library demos.
   - **US National Archives (NARA)**, **Library of Congress**, **NASA**, other US federal agencies: federal works are public domain; check each item's rights statement. "No known restrictions" (LOC, Flickr Commons) is **not** clear enough: name it to the user or find the same image elsewhere with a clear statement.
   - **Museums with open access** (Met, Rijksmuseum, Smithsonian): CC0 where the object page says so; check that the item is still marked open access.
   - **University and city libraries** (e.g. Columbia's digitised ephemera on the Internet Archive): use their rights statement; "copyright status undetermined" is not usable.
3. **Tell the user before downloading**: what (title, years), from where (URL), under which licence and why. Keep `raw/` under about 1.5 GB; download serially (Commons rate-limits).
4. Record every asset with the seconds used (`footage.py used <name> "<source s> → film s"`), list it in `demo/CREDITS`, and keep the trail for anything judged "no notice".
5. Footage that is not of the subject itself (another city, another year) may stand in only with a tag that says exactly what it is.

## 10. Facts

Every number, date and claim on screen or in the voice comes from an official or primary source (a contemporary report, an official brochure, a government record), kept in `demo/FACTS.md` with the URL and the quoted wording. Counters are graphics: only their end values and dated anchors are facts. Where two primary sources disagree (a film's intertitle vs. the official brochure), use one and record the conflict.

## 11. Engine

- `demo/index.html`: one Canvas 2D page, stateless `render(t)`; scene functions draw a full frame; wipes draw the old scene, clip, draw the new one, then the band. `txt()` draws and registers rotated text boxes for `readcheck.mjs`; `reg()` registers a group drawn in pieces; `slam()`, `flash()`, `flicker()`, `shake()`, `slant()` (parallelogram windows), `cover()` (focus-point cover fit), `clipImg()` (forward / reverse / ping-pong / speed).
- `demo/tools/prep.py`: the print grade, clip extraction to 24 fps JPEG sequences (one percentile set per clip), stills, document pages and outline keying, cut-outs. `demo/tools/fonts.py`: fetch the OFL fonts and subset Noto Sans SC to the characters used. `demo/tools/cues.mjs`: subtitle cues from the page's own table, measured one line per language. `demo/audio/mix.py`: score, foley, narration, ambience, master.
- Checks: `readcheck.mjs`, `asr_check.py` per line, `tools/final_asr.py` on the final mix, `tools/rhythm_report.py` (flat windows, cut points, hit-to-onset alignment), `mux.sh` loudness.

## 12. Pitfalls of the medium

- **Upscaled archive film** turns to mush on a 1080p full frame: window it; split strips into panels; keep zooms inside the 2.5× ceiling.
- **Per-frame grading pumps**: one percentile pair per clip.
- **Type on a band running off frame**: place it from the band's centre line (point + normal), not by eye.
- **Red on red**: a red answer block on a red exposure ground disappears; switch it to ink.
- **A face as hero**: ordinary identifiable workers appear in groups, at work, in quick cuts; no slow motion or close-up protagonist.
- **Counters read as facts**: label only the end value and dated anchors; a caption beside a counter must match the number shown at every frame (stop the count on the caption's value while it is up).
- **A number without a unit**: every counter carries its unit in the same layout as elsewhere (小时 / 层 / 人 MEN).
- **Ink type over a window**: a line that runs past a photo's edge disappears into dark film; give it a paper tab or keep it clear of the window.
- **The verdict covering what was compared**: place it where no item is, after the hold.
- **Too many documents**: one marked sentence per document shot; a page with three highlights is a slide.
- **Short labels in an acceleration** fail reading time by design: keep text out of the 1/8-beat cuts; put the result in a held block after.
- **A hit at sample 0** overshoots in the AAC encode: fade the first 25 ms.

## 13. Variation space

The agent decides per film: structure, which archive and documents, which formats (not all of them in one film), the axis angle (−15° to −30°), the red's exact hue, tempo (100–140 BPM), whether there is narration (intertitles only is valid), the signature build (a tower, a bridge span, a crowd forming a word, a map filling in).

- **Three structures:** a calendar machine (one counter runs the whole film and stops at milestones); a document that asks and footage that answers (the turn at the middle); one object's journey through a process, then the scale of the whole.
- Subjects that fit: construction and engineering histories, industrial anniversaries, mass events, labour and collective effort, infrastructure openings, any "many people, one machine rhythm" story with archive film and documents behind it.

Our demo: [DEMO.md](https://github.com/lemomo-ai/lemo-opuscar/blob/bebbbe1aa92a3cb4bb6f83500e61b23a17d1aa00/styles/kino-montage/DEMO.md).
