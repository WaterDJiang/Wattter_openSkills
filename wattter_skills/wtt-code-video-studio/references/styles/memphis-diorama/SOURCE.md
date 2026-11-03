> 上游方法原文：Lemomo / Lemo-Opuscar，MIT，固定版本 `bebbbe1aa92a3cb4bb6f83500e61b23a17d1aa00`。本文件为参考资料；本库执行规则以同目录 STYLE.md 和主 SKILL.md 为准。示例题材、品牌、字幕语言、次数、片长与外部工具路径不作为本片要求。

# Memphis Diorama — Style Prompt

> A place built as a tabletop model: on warm white paper an organic, grainy frame grows open, and inside it a small world in flat Memphis colours, ink outlines, hard purple shadows and tiny patterns, full of small motions under a slow camera. Calm, bright and warm; a place you watch, not a story you follow.
> References (grammar only): the Memphis Group, Ettore Sottsass, Nathalie Du Pasquier (saturated primaries next to pastels, dots, zigzags and terrazzo flecks on every surface); architectural and railway-layout models (a whole place seen from above, at once); children's picture-book towns (every window has a flower box, every corner has something going on); risograph halftone (shadow as a field of dots). Use none of their objects, layouts, palettes or music.

## 1. Essence, and what it is not

- **Paper and a grainy frame.** A warm white ground; the picture lives in a rounded, organic frame whose edge dissolves into grain. It grows open from the centre at the start and draws back in at the end.
- **Memphis flat colour.** Saturated primaries plus pastels, flat fills, no gradients; a deep-indigo ink outline; small patterns tiled on surfaces (dots, stripes, zigzags, terrazzo flecks, halftone).
- **The eye of a model-maker.** High three-quarter, top-down or cutaway views. The film always looks at a *place*, never at a person.
- **Small motions everywhere.** Water, wind in trees, cloud shadows, birds, boats, walkers, lights coming on one by one. The place is alive because of them, not because of a protagonist.
- **Three lines of type under the frame**: title / one sentence / small data, under three Memphis marks (a yellow dot, a pink triangle, a blue zigzag). Bilingual words take two of them, one Chinese line and one English line (§4).

Not character animation: nobody acts. Code-made faces, gestures, getting in and out of cars always look stiff, so this style never shows them. Not an isometric infographic (that one is cool and diagrammatic; this one has weather, seasons and sound). Not tilt-shift (no photograph, no depth of field: everything is flat and sharp). Not low-poly (no faceted shading or plastic highlights: flat fills, outlines and patterns do the work).

## 2. Materials & rendering

- **Three tones only**: the top face is the brightest, sun-facing sides keep the base colour, the faces turned away drop to about ×0.5–0.95. Hard edges between faces, never smooth shading.
- **Hard shadows**, never blurred, tinted cool purple (shadow ≈ base × (0.70, 0.58, 0.90)); the sun direction never changes within a film.
- **Halftone in the shade**: inside shadows, a staggered grid of lighter dots in world space, like a print. It turns dark areas into texture instead of dirt.
- **Outline as a post pass** from normals and depth: about 2 px deep indigo `#25214A` at 1080p. Light cones, decals, particles (rain, snow, petals, smoke) and thin stems carry no outline; a thin object that is all outline reads as an ink scribble.
- **Patterns belong to the world**: dots and stripes are computed from world coordinates and stay on the object as it moves. Pattern scale grows with distance so far surfaces do not buzz.
- **Detail is built, not textured**: a house is a plinth, plank-striped walls, white corner trims, two roof slabs and a ridge, a gable with a round window, framed windows with shutters and flower boxes, a door with a step, awning and lamp. A tree is a trunk with a branch and a cluster of lobes, plus lighter lobes on the sun side. Water is layered: bank, shallows, a deeper channel, white foam lines at the edges, small white squiggles drifting with the current.
- **Screen space holds only three things**: the grainy frame, the bottom type, explainer callouts.
- **Never**: depth of field, real reflections, bloom, motion blur, volumetric light. A lit lamp is a flat warm colour plus a hard-edged pool of warm light on the ground.
- **Hero objects do not receive shadows** when they pass through shade, or they turn dirty.

## 3. Colour logic

- The ground outside the frame is always warm white `#FFFCF6`; nothing else is drawn there.
- **5–7 saturated hues + 2–3 pastels** carry the picture. Ink `#25214A` is only for outlines, type, tyres and window frames.
- **Cluster colour by area**: neighbouring blocks differ in hue; one colour's share is controlled (a field type at about a third of the ground, not sprinkled at random). Leave large calm areas of one colour (water, a field, a square) so the picture can breathe.
- **Day is bright and warm.** When it gets dark, darken by the scene: a night scene may be dark, but never grey all over.
- **Night is a luminance shift toward violet**, not a general darkening, so yellows don't go olive; every light is the same warm yellow (about `#FFD36E`). **Dusk** adds an orange-pink layer (about `#FF9E7A`) on the way to night.
- **Time and season change the large areas only** (ground, crowns, roofs, water), never the whole palette. Each changing material carries one colour per state; a wave (§8) swaps them.
- **Night and day by area is also a wave.** When the dark falls or lifts street by street (dawn spreading from one landmark, a district losing power), night and day are two states like two seasons: each changing material carries its night colour (the violet shift above) and its day colour, and the ring swaps them. Lights belong to the night state: a lit window or lamp head is warm yellow on the night side and plain glass or metal on the day side; a lamp's pool is a flat disc on the ground, warm on the night side and the ground's own colour on the day side, so it goes out exactly as the ring passes. Keep the rest of the picture's light unchanged during such a wave: a global darkening on top of it turns the day side grey.
- Winter does not mean all white: crowns go to pastel lilac, ice blue and mint with white dots, paths stay swept, houses keep their colours.
- Example palette (an example only): yellow `#FFD234`, pink `#FF7EB3`, sky `#5CC8FF`, mint `#5EDFB0`, lilac `#B9A0FF`, peach `#FF9C6B`, cobalt `#2F5BFF`, coral `#FF5A5F`, green `#2FCB7A`.

## 4. Type & subtitles

- **Three centred lines under the frame**: line 1, the title, Chinese and English, weight 600, about 25 px, dark; line 2, one sentence, weight 400, about 18 px, grey; line 3, small data (time, solar term, place, coordinates) in a monospace, about 15 px, light grey. Line 3 may change with the picture.
- **Line 3 is optional, and so is line 2.** An empty line leaves its place empty; the others never move up to fill it. With a voice, or when the film's words are bilingual, the type is **one Chinese line and one English line**: line 1 in Chinese (weight 600, about 25 px, dark) and line 2 in English (weight 400, about 18 px, grey), each on one line, never wrapped; line 3 stays empty unless there is small data to show. In this layout both lines change together, as one pair.
- The lines fade in and out with the frame and never move. When a line changes, the old one fades away and the new one fades in; line 1 stays (in the bilingual layout, both lines cross-fade, about 0.4 s out and 0.4 s in). The three marks stay at full strength through every change: only the words fade.
- Typefaces: Inter Tight for Latin, Noto Sans SC for Chinese, IBM Plex Mono for data (all OFL).
- Usually no voice: the type is the narration. With a voice, use plain bottom subtitles, one Chinese and one English line, no styled caption boxes.
- Hold every line ≥ max(1.8 s, reading time + 0.6 s).
- **Callouts** for explainers: a rounded pill with a leader line and a dot, Chinese main and English small, popping out of the model with a back-ease and fading when done.

## 5. Motion quality

- **60 fps, every frame moves**; no stepping, no jitter. The frame's grain boils at 12 fps, which is the only thing on twos.
- **Shapes may be simple; motion may not.** Everything eases. Vehicles accelerate, brake and nod; turns follow smooth curves, never polylines.
- All natural motion is procedural and looping: water, trees, cloud shadows, leaves, snow, smoke, flocks. Every object has its own phase; nothing marches in step.
- **People are distant decoration**: small, walking a cycle, flying a kite, rowing. No close-ups, no acting, no hand business.
- Things never pop into being: they grow from nothing or bounce in with a back-ease; a change of state is announced by an object **squashing down and springing back** (anticipation, then overshoot).
- What never moves: the frame's position, the type's position, the paper, the sun direction.

## 6. Camera grammar

A vocabulary, not a route. Opening and ending come from the topic.

| Move | What it expresses | Can serve |
|---|---|---|
| High slow orbit or drift | the whole place breathing | time passing; day and night; seasons; a loop |
| Straight-down, slowly turning | a map; order | road networks; fields; coverage; data on a grid |
| Locked three-quarter frame | calm; comparable | before and after; data; several places side by side |
| Lateral move along a cutaway | above and inside at once | how a thing works; underground; under water; inside a building |
| Slow push to one detail | something is happening here | a lit window; a stall; a bird on a roof |
| Following one vehicle | flow; a route | a delivery; a commute; one line joining places |

- **Prefer one continuous take**, slow enough that the viewer can stop and look at any corner. When a long take must hold a composition, ease the camera speed down instead of letting the place drift out of frame.
- The frame is about 1520 × 744 px, a little above centre; the type sits under it and never covers the subject.
- **Transitions**: only three — the frame draws in and grows out again; a wave sweeps across (colour, light, season); the ground is cut open (the Cutaway of §8: the same move, whether the cut goes into the ground, a building or water). No white flash, spin or fast hard cut.
- The camera never passes through geometry; to get around something, move in two steps (rise, then travel).

## 7. Sound palette

- **Warm, gentle and continuous**: piano, Rhodes-like electric piano, marimba, celesta, music box, soft synth bass, a warm pad, brushes and shaker. A quiet stretch can be piano and pad alone.
- **One piece, not a medley**: when the place changes (a season, day to night), keep the same harmony and tempo and change only how thick the accompaniment is. A section that stops and a new one that starts sounds broken.
- **Foley is the sound of small things**, kept under the music: birds, ducks, water, a bicycle bell, raindrops, leaves, geese, wind, snow, the click or *ting* of a light coming on. Tuned foley (a light coming on) uses notes of the current chord or its pentatonic scale.
- **The same event always makes the same sound**: if every change of state starts with a squash, every squash gets the same thump, spring and rising harp.
- Silence is allowed, but keep a faint room tone under it.
- Loudness −14 LUFS, true peak ≤ −1 dBTP; fades follow the frame growing open and drawing in. No voice by default.

## 8. Native moves

A menu: use the ones your story needs.

- **Wave.** A ring spreads from one point; everything it passes takes its next state (colours swap per pixel inside the radius; objects grow, open, fall or light up as the ring reaches them). *Fits content like:* night falling street by street; a change of season; a delivery or signal coverage map; power coming back after an outage. Night falling or day breaking by area follows §3 (night and day as two states); how to build it is in §10.
- **Squash and spring.** One landmark squats, springs back, and the change starts from it. Use it to say "this causes that" without a person. *Fits content like:* a fountain that starts the morning; a factory chimney that starts a shift; a station clock that starts the rush hour.
- **Cutaway.** Cut along a line; the near part sinks and slides away to show the section underground, inside a wall or under water. *Fits content like:* how a metro and its pipes work; a tree's roots; what each floor of a building is doing; fish under a pond. What is revealed is built, not implied: floors with their rooms and furniture, soil in layers, pipes and tunnels, water with what lives in it; every cut face is drawn as a section (flat colour with section hatching), never left hollow. The near part leaves in two steps (a lid rises, then slides back; a wall or a slab of ground sinks straight down), so nothing passes through anything, and it comes back the same way in reverse. The engine has no cutaway built in: §10 says how to make one.
- **Grow the frame.** The organic frame grows from the centre to open, draws back in to close, and can close and reopen as a chapter break. *Fits content like:* an opening; a change of chapter; an ending.
- **Living loop.** Every small motion is periodic, so a passage loops seamlessly. *Fits content like:* a website hero; a screensaver; a livestream background; a live wallpaper.
- **Callout.** A pill label with a leader line pops out of the model. *Fits content like:* explaining a mechanism; labelling data; naming places.

## 9. Pitfalls of the medium

| Pitfall | Fix |
|---|---|
| Code-made people look stiff close up | keep them small and far; no acting |
| Day looks grey, not healing | raise saturation, warm it; shadows go purple, not grey |
| Yellows turn olive at night | shift by luminance toward violet; give warm objects their own night colour |
| Colours sprinkled at random look dirty | cluster by area, control each hue's share |
| Every tree looks the same | at least five crown shapes (round, cone, egg, cloud, column…), lighter lobes on the sun side |
| Thin objects turn into black scribbles | thicker stems, or no outline and a brighter colour |
| Large shadows look like dirt | halftone dots in the shade |
| Far outlines and patterns buzz | less detail far away; pattern scale grows with distance |
| A long take drifts until the subject leaves the frame | ease the camera speed down over time |
| A state change happens "by itself" and feels arbitrary | anticipate it: a squash on one landmark, then the wave from there |
| The camera passes through an object | move in two steps, or remove the blocking tree for that shot |
| The frame is crowded and has no air | keep large quiet areas of colour (water, field, square) |

## 10. Engine

`demo/memphis.js` (three.js r170): `Diorama(glCanvas, ctx2d)` renders at 2× with a normal-and-depth outline pass, composites the grainy organic frame (`grow` opens it) and draws the bottom type (`drawText`). `flat(hex, o)` is the flat material: `pat` (1 dots, 2 diagonal stripes, 3 zigzag, 4 vertical stripes, 5 hatch, 6 horizontal stripes), `patCol`, `patScale`, `lit` (no face tones), `emit`, `win` (facade windows), `nightCol`, `col2` / `patCol2` (the next state for a wave). Globals: `setSeason(x, z, r)` (wave), `setHalftone(1)`, `setNight`, `setDusk`, `setLamps([[x, y, z, r]…])`, `setWave` / `setZone` (lights coming on). Helpers: `mesh`, `box`, `rng`. `demo/people.js` has the distant walker. A minimal example that the demo never draws, and how the demo's seasonal materials work: [DEMO.md](https://github.com/lemomo-ai/lemo-opuscar/blob/bebbbe1aa92a3cb4bb6f83500e61b23a17d1aa00/styles/memphis-diorama/DEMO.md) "Build notes".

- **Engine, not story.** `memphis.js` and `people.js` hold no place, season or timeline: copy them into your project folder whenever you like, before your treatment too. `main.js` is the demo's film (its place, seasons and timing): open it only after your treatment exists, like the rest of the demo.
- **Night is global.** `setNight`, `setDusk`, `nightCol`, `win` and `setLamps` act on the whole picture at once, and `win`, `setLamps`, `setWave` and `setZone` only show anything while `setNight` is above 0. `setWave(r, x, z)` (with `win` facades and `zoneAware` materials) lights windows ring by ring in a picture that is already at night; it does not darken or brighten by area.
- **Night to day (or day to night) by area** uses the season wave instead, with `setNight(0)` throughout: each changing material is `flat(nightColour, { col2: dayColour, patCol: nightPat, patCol2: dayPat })` (reverse the pair for night falling), and `setSeason(x, z, r)` moves the ring. Windows and lamp heads are their own meshes with `emit: true` (warm yellow, `col2` the day glass or metal); lamp pools are flat discs about 1.5 cm above the ground, `shadow: false` and `userData.noOutline`, warm on the night side and the ground's colour on the day side. The night colour is computed in JS from the shader's own night rule; the helper and the details are in [DEMO.md](https://github.com/lemomo-ai/lemo-opuscar/blob/bebbbe1aa92a3cb4bb6f83500e61b23a17d1aa00/styles/memphis-diorama/DEMO.md) "Build notes".
- **The bottom type.** `drawText(g, [l1, l2, l3], alpha, strong2)` draws all three lines and the marks at one alpha; pass `''` for a line you leave out (`[zh, en, '']` for the bilingual layout). It has no alpha per line, so for a cross-fade (§4) draw the type yourself in the same layout: baseline `y0 = FRAME.cy + FRAME.hh + 64`, the lines at `y0 + 34`, `y0 + 64` and `y0 + 91` in the fonts of §4, the marks once at `y0` at the text's base alpha, each line at its own alpha; then leave `text` out of `dio.render`.
- **Cutaway: build it yourself.** The engine has no section, clipping or boolean. Model the subject so its near part is its own group (a front wall; a roof lid with its gable; a slab of ground in front of the cut, as a thick box instead of the ground plane, which cannot be cut), and model what is behind it (floors, rooms, soil layers, pipes, a pond's depth). Cut faces get `pat: 5` (section hatching) in a colour a step darker than the part. Animate the near group in two steps (lift then slide back; or sink straight down below the ground, where the ground plane hides it), and set it `visible = false` once it is fully away, so it casts no shadow and draws no outline. Close in reverse order. A code sketch is in [DEMO.md](https://github.com/lemomo-ai/lemo-opuscar/blob/bebbbe1aa92a3cb4bb6f83500e61b23a17d1aa00/styles/memphis-diorama/DEMO.md) "Build notes".

## 11. Variation space

You decide the place, the season and time, the camera route, the pace, which native moves, and the palette within §3.

- Structures: **one take that loops** (a square at the same hour every day, ten seconds that join end to start); **the same place in four states** (a market at dawn, noon, dusk, night); **whole view → cutaway → whole view** (a building, then its floors, then the building again with one thing changed).
- Openings: **the frame grows open**; **a place in the dark before dawn lights up**; **a wave sweeps into an already open frame**.
- Endings: **the frame draws back in**; **the lights go out one by one**; **the camera rises until the place is one dot on a map**.

**Use cases** and the order in which information arrives:

1. **A moving scene on a web page** (hero, loading page, 404): first the whole calm place, then one or two small motions that lead the eye; loopable; scroll or the mouse can trigger a light or a change of sky.
2. **Ambient or focus loops** (livestream backgrounds, screensavers, live wallpapers): no type or a single line; the camera almost still; a seamless loop; sound mostly ambience.
3. **Solar terms and seasonal series**: one place, one term or season per part; the colours and small motions change; line 3 carries the term and the date.
4. **How things work**: the whole place → cut open → callouts one step at a time → back to the whole place with the result visible.
5. **City data maps**: map or locked three-quarter view → the data grows out as a wave or as columns → callouts read the values.

---

How our demo was made (story, shots, score, end card, build): [DEMO.md](https://github.com/lemomo-ai/lemo-opuscar/blob/bebbbe1aa92a3cb4bb6f83500e61b23a17d1aa00/styles/memphis-diorama/DEMO.md). Read it after your treatment exists.
