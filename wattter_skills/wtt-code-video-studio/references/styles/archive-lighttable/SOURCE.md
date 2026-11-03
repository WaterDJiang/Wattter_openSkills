> 上游方法原文：Lemomo / Lemo-Opuscar，MIT，固定版本 `bebbbe1aa92a3cb4bb6f83500e61b23a17d1aa00`。本文件为参考资料；本库执行规则以同目录 STYLE.md 和主 SKILL.md 为准。示例题材、品牌、字幕语言、次数、片长与外部工具路径不作为本片要求。

# Archive Light Table — Style Prompt

> Real archive objects (glass negatives, slides, letters, telegrams, clippings, drawings) lie on a cool, backlit light table. A loupe comes down on one of them, and inside the glass the object comes alive: a negative turns positive, a line of type lights up, a number lifts off the page, a photograph opens into depth. Precise catalogue numbers, dates and readings are pinned to the objects. Clean, modern and quiet, with no vintage filter.
> References (grammar only): archive documentaries that push into still photographs; visual investigations that annotate real imagery (one line, one reading, one source per screen); product macro films (glass edges, transmitted light). Copy none of their layouts, typefaces, shots or music, and never name them in the film.

## 1. Essence, and what it is not

- **The objects are real**: scans of public-domain or licensed archive items, at their true proportions, with their real damage (broken corners, emulsion edges, folds, pencil marks). Nothing in them is drawn or generated.
- **Light comes from below**: the table glows a near-white cool grey; film and glass transmit it, paper glows warm at its edges, opaque things read darker than the table.
- **The loupe is the camera's door**: every dive into an object goes through a loupe that lands on it. The inside of the lens is where the object changes state.
- **Catalogue truth**: every object carries its real identifier, date and title from its holder; numbers on screen come from the record.
- **One signal colour** for marks, readings and anchors; everything else is the archive's own greys and paper tones.

**Sources and licences.** Open collections with masters and catalogue records: the Library of Congress (files on `tile.loc.gov`; records from its SRU server `lx2.loc.gov:210/lcdb` when loc.gov pages are blocked), Smithsonian Open Access (CC0), the Rijksmuseum (CC0), NARA, Europeana (check each item's rights statement). CC0, public domain and CC BY (credited) are fine. "No known restrictions", CC BY-SA and other terms are not CC0: name the terms to the user and ask. For brand history, ask the user for their scans, archive numbers and right to use them. Never stand a generated image in for an archive object. Keep a `FACTS.md` in the project folder (claim, source URL, quoted wording, or how a figure was derived) and deliver it with the film.

Not Halftone Dossier (no newsprint dots, no aged-paper grade), not Satellite Briefing (objects on a table, not the ground from orbit), not Data Storytelling (no charts; the numbers live on the objects), not a keynote (no slides or header bars).

## 2. Materials & rendering

- **One world, one camera**: every object is a textured quad on the table with a centre, rotation and scale (texture px → world units at true size). The camera is a 2D centre, zoom and roll; the table and every mark go through the same world → screen function.
- **The light table**: an emissive surface (≈ 0.97 white, slightly cool), soft falloff, diffuser noise, an aluminium frame and a dark desk beyond. It can be switched off (ambient ≈ 0.04) and flicker on.
- **Glass negatives**: transmission from the scan's positive, `T = 0.035 + 0.9 · (1 − pos)^1.25`, with a warm silver-gelatin tint; the emulsion mask comes from the scan (white margin touching the border = no glass), so broken corners show the table. Dust and scratches are procedural, anchored to the table.
- **Paper**: backlit, its colour is transmission (paper tone × light); lit lines get darker ink and brighter paper; unlit text can dim to bring one line forward.
- **The loupe**: inside the lens each pixel maps back to the table through the magnification (≈ 2.5×) with a pincushion term (k ≈ 0.16 at the rim), slightly different per RGB channel for colour fringes. Around it: a black ring with a bevel highlight and a clear acrylic skirt that refracts the table and glows at its foot. Landing and lifting, it scales by about 1.35× and casts a soft shadow.
- **The photograph space**: after the push the lens stops being a lens. A photo gains depth from a ground-plane nearness map (zero at the horizon, linear in the row below it), cut-out layers for upright subjects and a filled background; a dolly and a lateral shift drive parallax, and a subject layer may drift. Things left on the ground plane lean: centre the dolly between them.
- **Sampling**: all texture reads inside the branching lens code use explicit gradients (`textureGrad`), otherwise quads that cross a branch pick a wrong mip level and leave dashed seams.
- **Marks** live on a 2D canvas above the picture: hairlines 1.5–3 px, rings, crop corners, underlines, leaders. Table marks are clipped out under the loupe; marks inside a photograph use its forward mapping, parallax included.
- **Post**: a light vignette and fine moving grain (heavier inside photographs). No film damage, no sepia, no halftone.

## 3. Colour logic

- Neutral ground: the light table (near-white, cool) and the archive's own tones (silver greys, paper tans). Do not regrade the archive into a colour scheme.
- **One signal colour** (e.g. a signal orange) for marks, readings, anchors and the verdict; never as a fill behind pictures, never for decoration.
- Text is ink (near-black) on light areas and paper-white on dark caption plates; choose the contrast by the ground, never colour on colour.
- Positives inside the lens may be gently levelled (black and white points) so a weak scan reads; negatives stay as the glass gives them.

Example (our demo): table #F7F9FB, ink #15171A, signal #FF5A1F, caption plates rgba(14,15,17,0.74).

## 4. Type & subtitles

- **Roles**: a monospace for identifiers, dates and readings (e.g. IBM Plex Mono, 17–34 px; readings 74–120 px); a sans for labels in the film's language (e.g. Noto Sans SC or Inter, 21–36 px); a serif only for titles and the one name a photograph carries (60–76 px). OFL, self-hosted, CJK subset when needed.
- **Labels attach to objects**: an anchor dot and ring, a vertical leader, then the text. A reading sits in a dark caption plate with a small label above and the source (the catalogue number or the original wording) below.
- **Subtitles** are a caption strip at the bottom centre, on a dark plate with a 3 px signal-coloured edge. If the film is bilingual, the film's language goes on top. Hold ≥ max(1.8 s, speech + 0.6 s).
- **Quote the source when you can**: a crop of the actual line, or the record's wording in quotation marks, beats a paraphrase.

## 5. Motion quality

- 24 fps on ones; every camera parameter on smooth monotone curves through keys (no overshoot, no stepping).
- The camera glides across the table, slows to let the loupe land, then pushes. Speed lives in the glides and pushes; holds are for reading.
- The loupe lands with a fast ease-out (≈ 0.4 s), lifts the same way. Lines draw on in 0.3–0.6 s; text wipes in from its leader side; numbers count up and land with the voice.
- What never moves: the archive's own content outside a photograph space, and the table itself.

## 6. Camera grammar

| Move | What it expresses | Can serve |
|---|---|---|
| table glide (pan and roll) | surveying; moving to the next piece of evidence | a timeline of documents; a product family; an album |
| loupe landing + push into the lens | choosing one object; "look closer" | the claim; the key photograph; a signature |
| inside the lens: tracking along a line | reading | a letter, a ledger line, a caption, a spec |
| photograph space: dolly + parallax | being there | the event itself; the founding moment; the place |
| rise out of the lens | stepping back, the evidence noted | a transition; a summary |
| pull back to the whole table | scale; everything at once | an index, a timeline, a closing |

Framing: at a reading moment the subject fills at least a third of the frame height; readings and labels stay clear of the subtitle strip (bottom 140 px). Transitions are made by the loupe (land, push, rise, lift) and the glide; no cuts, fades to black or page turns between objects.

## 7. Sound palette

- **Ambience**: the light table's ballast hum (100 Hz and harmonics), starter clicks, room tone. Inside a photograph the hum gives way to that place's air.
- **Foley**: the loupe on glass (a clack with a high ring), paper sweeps for glides and lit lines, ticks for scales and counters, a pen stroke for a verdict, soft clicks as labels land.
- **Music**: restrained and small: a felt piano, a few strings, glass or bowed metal for the moments of seeing. Build by subdivision and register, not by drums. Leave real silences before a reveal or a verdict; the first sound after them should be the loupe, the place or the verdict.
- **Voice**: a calm narrator, short sentences that state what the object says. Music about 10 dB under the voice, ducked while it speaks; −14 LUFS.

## 8. Native moves

- **Negative to positive under the loupe.** A develop front spreads from the lens centre with a thin warm edge, turning the glass negative into its positive only inside the lens. *Fits content like:* a founder's portrait plate; a factory on a lantern slide; an X-ray film becoming the product inside.
- **The line lights up.** On paper inside the lens one line of type brightens while the rest dims, an underline draws under it, and one word or number lifts out into a reading card. *Fits content like:* a ledger entry; a patent claim; the first order on an invoice.
- **Into the photograph.** The lens rim grows past the frame while the view inside widens; the photograph gains layered depth and a subject drifts. *Fits content like:* the first shop front; a launch day crowd; an expedition camp.
- **Measuring on the photograph.** A ruler laid on the ground plane in perspective, with ticks that crowd toward the horizon and a counter that lands on the recorded figure, marked as a schematic when it is one. *Fits content like:* a race distance; a bridge span; a building's height.
- **Two records, held side by side.** Two caption cards, each with a crop of its source, held still until both are read before one is struck. *Fits content like:* a misprinted date; two versions of a founding story; specification against delivery.
- **The table becomes the index.** Pull back to the whole table; each object's tag flies into one list with its identifier and its reading. *Fits content like:* a company timeline; a collection catalogue; a product family.

## 9. Pitfalls of the medium

- **Over-magnifying a weak scan**: keep the lens interior under about 1.5 screen px per scan px; choose items by scan size.
- **The loupe sweeping over empty table**: lay objects close together, land the loupe straight onto the object (drop in, don't slide in), and glide the camera over objects, not gaps.
- **Shear in the photograph space**: one depth map for a photo with people or machines in it tears them apart. Cut upright subjects into layers, fill behind them, and keep 2.5D moves small enough that the fill is barely seen.
- **Labels that scroll away**: a label on a moving table leaves the frame before it is read; hold the camera, or fix the caption on screen.
- **Vintage creep**: no sepia, no halftone, no paper-ageing overlay. The age is in the objects, not the grade.

## 10. Engine

- `demo/film.js`: `IT` (objects: centre, rotation, scale), `toW()` / `toT()` (texture ↔ world), `CAM` keys and `w2s()`, `dive()` (loupe point, land/lift times, lens interior as tracks), `shot(t)`, `int2s()` (photograph → screen for marks), the shader (`lightTable`, `paper`, `negative`, `parallax`, rim and skirt), the overlay (`annot`, `measure`, `compare`, `indexPanel`).
- `demo/tools/prep.py`: emulsion masks from scans, difference matting of a subject against a smooth sky, ground-only cuts, push-pull fill.
- Minimal example, not in the demo: put one 35 mm slide (`IT.slide = {c, r, k, size}`), a loupe landing with `dive(toW(IT.slide, p), t0, t1, keysS, keysC)`, and light one line with `band()`.
- **Extra packages and packs**: none beyond `setup.sh deps voice music` (numpy, scipy, Pillow, soxr are in the core tier). A score in this palette needs sample libraries: `sh tools/fetch.sh instruments salamander` (piano), `vsco2ce` (strings), `vcsl` (glass, bowed vibraphone). Anything else a film needs goes into a private venv or `node_modules` in the project folder, never into `$LIB/.venv`.

## 11. Variation space

The agent decides the objects, their order, the story, which native moves to spend and where, the camera path, the subject of the photograph space, and the signal colour.

- **Three structures**: a company's founding told as five objects in date order, each dive revealing one person; a single photograph explored in three dives (the place, the people, the date on the back); a before/after pair of plans and photographs of one building.
- **Three openings**: the table switching on in the dark; a loupe already on a plate, rising to reveal the table; a hand-written date on an envelope filling the frame.
- **Three endings**: the index of everything on the table; the last photograph held in depth with one line of text; the light table switching off, leaving one object glowing.

---

How our demo was made (story, shots, score, end card, build): [DEMO.md](https://github.com/lemomo-ai/lemo-opuscar/blob/bebbbe1aa92a3cb4bb6f83500e61b23a17d1aa00/styles/archive-lighttable/DEMO.md). Read it after your treatment exists.
