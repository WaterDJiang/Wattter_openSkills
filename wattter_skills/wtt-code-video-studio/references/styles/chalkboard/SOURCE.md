> 上游方法原文：Lemomo / Lemo-Opuscar，MIT，固定版本 `bebbbe1aa92a3cb4bb6f83500e61b23a17d1aa00`。本文件为参考资料；本库执行规则以同目录 STYLE.md 和主 SKILL.md 为准。示例题材、品牌、字幕语言、次数、片长与外部工具路径不作为本片要求。

# Chalkboard — Style Prompt

> A real classroom blackboard on which chalk writes itself, stroke by stroke in true stroke order, with no hand, no chalk stick and no eraser in sight. One idea is taught the way a teacher does it: write what people think, wipe it with one pass, write what is true in the same place.
> References (grammar only): a primary-school literacy lesson on a sliding double blackboard; the way a teacher underlines the parts of a character, circles one component and wipes a wrong line. Take the order of a lesson, not any teacher's handwriting.

Suits short lessons on one idea: where a word or a character comes from, a misconception set right, a worked problem. The length follows how many steps the lesson has.

## 1. Essence, and what it is not

- **A clean, freshly wiped board.** One even deep ink green with its own fine grain and very slow mottling. No history on the slate: no old swirls, no ghost lessons, no floating dust, no bokeh.
- **Writing that grows like a hand writes.** Strokes appear along their centre line in the correct stroke order, with pressure: pressed starts and corners, points that lift, 捺 feet that spread, hooks flicked off.
- **Three chalks at most.** White for structure, one accent chalk for the single part the lesson tracks, one pale chalk for a second hand (a pupil, a visitor).
- **A real object in a real room.** Wooden frame, a tray with sticks of chalk, painted tian-zi grids, sliding panels, a wall and a clock around it.
- **Few words, large letters.** The board holds keywords; the explanation is spoken.

Not Whiteboard Explainer: that style is a bright glossy board, coloured markers, floating marker props and magnets, ghost marks of old lessons, and a camera travelling across a knowledge map of many regions to explain how something works. Chalkboard is a dark matte slate with nothing floating in front of it, kept clean, one question per board, the camera facing it flat; it advances by writing a claim, wiping it and rewriting in place, and it lives in a classroom (panels that slide, grids painted on, a tray, a wall). Not a slide either: nothing is typeset, nothing fades in.

## 2. Materials & rendering

- Canvas 2D for everything visible; WebGL2 only for the post pass (camera motion blur, a light vignette, grade, dither).
- Each stroke is baked once into a board-space coverage sprite (coverage, arc length, lateral position). A partial stroke reveals pixels up to the current arc length with a round leading edge; the board's grain decides which grains take the chalk (deposit with a 2×2 supersample and a faint powder halo).
- Chalk edges are firm; loose powder only at the lift-off of a stroke (two to five grains). Never sugar the board.
- Writing strokes carry a width profile per stroke type (start bump, corner bumps, taper for 撇 / 提, foot for 捺, quick lift for hooks) and a pressure profile (heavier at both ends, lighter in the middle). Straight strokes bow slightly; horizontals rise 2–3° to the right; 横, 竖 and 折 enter with a short pressed tick from the upper left.
- Board, panels, frame, tray, clock and wall are baked once in world units; the slate grain is a periodic tile drawn in world space (soft-light) only when the camera is close.
- Erasing is a blurred destination-out band along one smooth path on a layer that holds only the strokes being wiped; it leaves a very thin, even haze. One wipe per film is plenty.
- A wet streak (a board just wiped with a damp cloth) is a soft mask with a wide blur at its drying edge, fading at top and bottom, that darkens the slate slightly; never a hard rim.
- Light: a gentle multiply falloff away from the windows and at most a faint warm window patch. Light never draws shapes across the writing in close shots.

## 3. Colour logic

- Ground: deep ink green slate, wood frame, warm white wall and a coloured dado if the room is seen.
- White chalk carries every structure: characters, lines, labels, arrows.
- The accent chalk (example: orange) is reserved for the one component the lesson tracks; it never decorates and never draws arrows or underlines that are not that component.
- A pale second chalk (example: yellow) marks another person's handwriting.
- No rainbow, no gradients in chalk, no glow. Painted grids are dull and thin so the chalk always wins.

## 4. Type & subtitles

- Chinese is hand-authored stroke data (centre lines + stroke type per stroke) drawn by the chalk engine, never a font's outline. Every character the topic needs is added to the data and checked against an OFL kai font behind it before shooting (how: §10, *New characters*).
- English on the board is a single-line OFL handwriting font (EMS family) drawn by the same engine; symbols missing from the font (arrows, plus) are drawn as strokes.
- On the board: keywords only, one line of Chinese, the next line English, a size smaller.
- Sizes at 1080p: big characters 300–450 px; labels ≥ 55 px CJK and ≥ 30 px Latin cap height; small writing gets heavier chalk so no stroke is thinner than 3 px.
- Reading time: every block stays fully in frame ≥ CJK ÷ 4.5 + other ÷ 15 + 1.5 s, counted from the frame it is wholly visible (readcheck). A block is fully written before it is read.

### Voice and subtitles

- When the style tells a story it is narrated: one calm teacher's voice in short spoken sentences, said as the matching chalk appears; what the voice names is being written or shown at that moment.
- A quiet subtitle plate sits above the bottom safe area: the spoken line in Chinese and a free English translation, one line each, a plain kai face (an OFL subset) on a soft dark plate, in and out with the voice. Long lines are split at sentence ends into several cues.
- Nothing the viewer must read on the board sits behind the plate; frames held for the board's words are composed above it.
- Pauses between voice lines are short (0.25–0.4 s); one longer hold (about 1.5 s) is kept for the verdict. Board action (a panel sliding, a wipe) runs under the voice instead of waiting for it.

## 5. Motion quality

- 30 fps, continuous (render with `--fps 30`: `core/render/video.mjs` defaults to 24).
- Chalk speed, measured on our demo: a big character takes about 0.1 s per stroke including the air between strokes (a ten-stroke character about 1 s), labels about 0.04 s per stroke. Writing speeds up rather than making the voice wait, but a big character written much faster than about 0.07 s per stroke stops looking like a hand.
- When reading time and chalk speed pinch in a short film, change the words, not the hand. Ways that work (choose per film): fewer and shorter blocks on the board; big characters only for what the lesson tracks, everything else at label size; start a block while the voice is still on the previous line, so it is finished when it is named; write the next block while the last one is still being read in the same frame; hold the frame instead of moving on; make the film longer.
- Camera eases in and out (cubic), never bounces except a whip landing.
- Things appear only by being written, wiped, revealed by a sliding panel or by drying. Nothing fades in.

## 6. Camera grammar

The camera always faces the board flat on (no perspective tilt).

| Move | What it expresses | Can serve |
|---|---|---|
| Close shot on the writing | attention on how a character or line is built | a component; a step of a proof; a spelling |
| Slow lateral pan along a line | time or sequence | a timeline; a derivation; a list of cases |
| Pull back to a fixed medium frame | the whole question at once | a comparison; a claim and its counter-claim |
| Same frame later | judgement | a correction; a before / after |
| Locked frame while a panel slides | a page turned in the room's own way | a new chapter; a hidden board |
| Whip with motion blur (≤ 0.5 s) | a jump to another part of the wall | a change of board |
| Cut on a line crossing a seam | a connection | cause and effect; the same part in two places |
| Wide shot of the whole wall | summary | the map of what was learnt |

The room is part of the style: at least once the frame opens wide enough to read board, frame, tray and wall as a classroom (where, and what else the room holds, is the film's choice). Close shots may show only slate and frame.

Rules: the subject is never smaller than a third of the frame in close shots; text blocks are never cut by the frame edge while they are read; no empty board for more than half a second. Transitions are hard cuts, a sliding panel or a line across a seam; no dissolves or page flips.

## 7. Sound palette

- Voice first: it is the loudest element; music sits 15–18 dB under it and comes up only in the pauses.
- Foley: real chalk recordings cut into grains, one grain chain per stroke, level from stroke size; a light knock on landings; the accent chalk slightly softer and duller. A felt pass for the wipe, the low roll of a sliding panel ending on a stop, room tone very low; school sounds (a distant bell) only as punctuation. Where the recordings come from and how to cut them: §10, *Sound*.
- Music: sparse plucked strings (a guqin model or nylon guitar) with marimba and pizzicato bass; a plucked note can be "born" from something drawn. Silence while a question or a verdict is read.
- Mix: about −16 LUFS integrated before mastering, true peak ≤ −1.5 dBFS.

## 8. Native moves

- **Write, wipe, rewrite in place.** The wrong reading is written under its object, wiped with one pass, and the right one written in the same spot from the same camera position. *Fits content like:* a common misconception in physics; a misremembered date; a sum everybody gets wrong.
- **Tracked component in accent chalk.** One part keeps its colour and its height across several forms. *Fits content like:* a root through a word family; a variable through an equation's rearrangements; a gene through generations.
- **Sliding panel reveal.** The front panel slides away to show a clean back board, and can slide back to close the lesson. *Fits content like:* "but before that…"; the hidden proof; the answer kept back.
- **A line that sews two boards.** One accent line runs across the seam to join two places. *Fits content like:* the same constant in two formulas; a quote and its source; cause and effect.
- **Drying wet streak.** The freshly wiped board dries back and reveals what was left untouched. *Fits content like:* yesterday's question; a note left by a student; a reminder at the corner.
- **Second hand.** A different, childlike chalk colour and hand on the same board. *Fits content like:* a pupil's question; a visitor's comment; a wrong attempt.
- **Chalk as a measuring tool.** An accent object laid along a white line and ticked off, so a comparison is shown, not told. *Fits content like:* a unit's origin; a scale; how many of one thing fit another.

## 9. Pitfalls of the medium

- Dirty boards (old swirls, ghosts, floating dust) read as "messy", not "real". Keep the slate clean and let the grain carry the realism.
- Equal-width polylines look like a plotter and make characters misread. Use stroke-type width and pressure profiles.
- Character data that is structurally wrong is caught at once by native readers: check every character against a reference before shooting.
- Small writing at 1080p disappears with the same chalk width as large writing; give small text heavier chalk.
- Text written while the camera moves away fails reading time; hold the frame or keep the block in view.
- Accent colour spread over arrows and decorations stops meaning anything.
- A soft halo at the chalk's front reads as glow. The demo's `drawFront` (`props.js`) puts a faint radial gradient under its grains: in your copy, drop the gradient and keep the grains.
- A wet streak with a hard edge looks like a cut-out.
- Board-speak in the voice ("A plus B", component names with no meaning) is not understood: every component is said with what it means the first time it appears.

## 10. Engine

The demo's code is a working engine; copy it into the project folder and write the film yourself.

**Copy as is:** `js/chalk.js` (`Stroke`, `bake`, `drawStroke`: the chalk), `js/hand.js` (`writeChar(ch, cx, cy, size, clock, o)`, `writeLine` for mixed Chinese and Latin, `writeLatin`, `latinWidth`, `loadSvgFont`; each returns `Stroke[]` with `t0`/`t1` set and `.end` = the time the last stroke ends), `js/r2d.js` (grain tile, deposit), `js/stage.js` (slates, frame, tray, clock, wall, `paintGrid`; world units: slate x 0…6400, y 0…1700, panel width `PW` 3200), `js/post.js`, `js/lab.js`, `tools/foley_lib.py`, `tools/subset.py` (subtitle font cut from the strings in `SUB` in `film.js`), `tools/srt.py`. `js/props.js` too, minus the glow (§9).

**Adapt:** `js/hz.js` (keep its characters, add yours), `index.html` (title), `js/app.js` (the compositor: it draws the layers, wet streak, wipe, light, subtitle plate and exposes `render`, `TEXTS`, `DUR`, `EV`; edit it to the film's board instead of feeding it placeholder data).

**Write yourself:** `js/film.js` (every stroke, time, camera key, voice start and subtitle, as data), the voice lines, the score and mix (`audio.py` is the demo's own score; its chalk-grain part is reusable), `build.sh`. `js/ancient.js` is the demo's old forms of one character: not an engine file.

**What `app.js` reads from `build(W, H)` in `film.js`:**

| Field | What it is |
|---|---|
| `S` | every `Stroke`, each with `layer`: `'FL'` (the sliding front panel, in panel-local units, moved by `slideX`), `'FR'` (the right panel, world units), `'BK'` (the back board, drawn only once the panel has moved), `'WORLD'` (on top, world units, drawn while `t < T.back0`); FL strokes also carry `phase` (`'pre'` = can be wiped, `wiped: true` = removed by the wipe; `'post'` = written after it). `o.R` sets bake resolution (default 2) |
| `DUR` | length in seconds |
| `camAt(t)` | `{cx, cy, s, shot}`: centre in world units, scale for a 1920-wide frame, shot index (motion blur is only taken within one shot) |
| `slideX(t)` | the front panel's offset; `() => 0` if it never moves |
| `TX` | board text for readcheck: `{id, text, layer, box:[x0,y0,x1,y1] in that layer's units, t0, t1}` |
| `SUBS` | subtitle cues `{id, t0, t1, zh, en}` |
| `EV` | sound events for `core/render/events.mjs`: `vo` (voice starts), `sub` (for the .srt), `chalk` (`t, d, len, color, pan, big`, one per stroke) and any of your own |
| `G1`, `G2`, `SMALL`, `T.back0`, `wet`, `wipe` | painted grids on the front panel and back board; when the closing slide starts; the wet streak `{x0, y0, y1, xEnd, bx0, t0, t1}`; the wipe `{t0, t1, w, path}` |

A film without a wet streak, a wipe, grids or a sliding panel removes those parts from its copy of `app.js` (or guards them, e.g. `if (!F.wet) return` at the top of `drawWet`, `if (!F.wipe) return null` in `drawWipeHaze`), and draws `WORLD` strokes on a condition of its own if there is no closing slide. Don't pass dummy fields to keep the compositor quiet.

**New characters.** `hz.js` maps a character to its strokes in standard stroke order (GF 0023-2020); each stroke is `"type x,y x,y …"`: the centre line through its anchor points in a 100 × 100 box, y down. Types: `h` 横, `s` 竖, `p` 撇, `n` 捺, `d` 点, `t` 提, `x` 悬针竖; `z…` for turns (corners pressed); a last letter `g` ends in a hook (its last point is the hook's tip), `p` / `t` in a point, `d` in a dot. Write only the centre line: the slight bow, the rise of horizontals and the pressed entry tick are added by `writeChar`. Symbols (arrows, plus, a tick) are written the same way. A way that works:

1. Take the stroke order and count from a dictionary that shows the standard order, and write down the type sequence first.
2. Set the character large from the reference kai (LXGW WenKai, `fonts/`) on a 100-unit grid, placed as the check page places it so the numbers line up: e.g. with PIL, `ImageFont.truetype(font, 1000)` drawn into a 1000 × 1000 image at `(0, 880)` with `anchor='ls'` (left edge, baseline at 0.88 of the box), with 100-px grid lines; read each stroke's start, corners and end off it and divide by 10. Keep the anchors on the middle of the font's stroke, not its edge.
3. Open `index.html?lab=hz&chars=<new characters>&size=400`: the chalk is drawn over the font in red. Check stroke count and order, which strokes touch or cross and which stop short, the proportion of each component, hook directions and the 撇/捺 feet; then look again at the size the film uses for it. Fix the numbers, not the font.
4. Read it at film size the way a native reader would, before shooting (§9): a structure that looks right at 400 px over the font can still read as another character on its own.

**Sound.** Three CC0 / CC BY recordings of chalk on a board from Wikimedia Commons (URLs in the demo's `build.sh`, credits in `CREDITS`) are cut into tagged grains with `python -I tools/foley_lib.py <out_dir> <name>=<file> …`: `tap`, `stroke` and `squeak` grains plus `index.json` with each grain's length, attack and brightness. The demo's `audio.py` places one grain chain per `chalk` event (length from `d`, level from `len`, the accent chalk low-passed); other recordings can be cut the same way.

**Render.** `node core/render/events.mjs <film>` (events from the page), your mix, `node core/render/video.mjs <film> --fps 30`, `sh core/render/mux.sh <video> <mix> <out> 30 1`, `node core/render/readcheck.mjs <film>`. The page bakes every stroke on load (about 10 s for 500 strokes), then 20–50 ms per 1080p frame. readcheck counts from the first frame a block's box is on screen, which is when its writing starts: leave the reading time after the last stroke yourself (§4).

## 11. Variation space

The agent decides the topic, the board layout, the number of panels, the tracked component, the hands, the camera path and the pacing.
- **Structures:** a proof built on one board line by line; three wrong answers wiped one after another before the right one; two boards in dialogue, question on one, answer on the other.
- **Openings:** a duster's last pass revealing a formula; a close-up of the tray as one chalk starts writing; the bell ringing over an empty, freshly wiped board.
- **Endings:** the whole wall with the lesson complete; a final underline under one word; the board half-wiped for the next class with one line kept.

---

How our demo was made (story, shots, score, end card, build): [DEMO.md](https://github.com/lemomo-ai/lemo-opuscar/blob/bebbbe1aa92a3cb4bb6f83500e61b23a17d1aa00/styles/chalkboard/DEMO.md). Read it after your treatment exists.
