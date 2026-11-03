> 上游方法原文：Lemomo / Lemo-Opuscar，MIT，固定版本 `bebbbe1aa92a3cb4bb6f83500e61b23a17d1aa00`。本文件为参考资料；本库执行规则以同目录 STYLE.md 和主 SKILL.md 为准。示例题材、品牌、字幕语言、次数、片长与外部工具路径不作为本片要求。

# Live Countdown Split-screen — Style Prompt

> An edit style, not a look. Real footage of one event with a known zero (a launch, a verdict, a final whistle, polls closing), shown in real time: screen time equals event time, a clock ticks every second, and the screen splits into more and more cells as the moment nears, every cell showing the same second. At zero the cells merge into one picture and the clock flips.
> References (grammar only): the real-time clock and splitting screens of the TV series *24*; the multi-camera archive panels and mission-time codes of the documentary *Apollo 11* (2019). Never copy their type, colours, sounds, graphics or shots, and never name them in the film.

## 1. Essence, and what it is not

1. **Real time.** One continuous stretch of the event, never cut, never re-ordered, never sped up. Slow-motion sources are played back at real speed. The clock and the picture can be checked against each other at any frame.
2. **The clock is the lead.** It ticks every whole second (sound and a falling digit), it says who is in control, and it changes state at zero.
3. **Cells show the same second.** Every video cell is synced to the clock, or says plainly that it is not (§8, "sync badge").
4. **The layout is the edit.** Cuts are layout changes, and every layout change lands on a real spoken call or event in the native sound, not on the music.
5. **More cells, closer to zero; one picture at zero.** The number of cells is the tension curve.

Not a montage (time jumps), not a security wall (the layout never moves), not a flashback structure (real time cannot go back), not a slide deck (cells that don't follow events, text filling the cells, centred titles with page turns).

## 2. Materials & rendering

- **Three kinds of material at once**: video cameras of the same moment (2–8), documents (a fact sheet, a filing, a schedule: shown as paper, never retyped as a slide), and photographs (the people of the day). Our own type explains them; type printed in the material is only picture.
- **Data drawn by us**: checklists, bars, a flight or process profile, a second countdown to the next milestone. Every number comes from an official source (§10).
- **Cells**: hard rectangles on near-black `#06080A`, 24 px outer margin, 8–9 px gutters, 1 px border `rgba(222,232,238,.16)`, a light radial vignette (to 36 % black) on video cells. No rounded corners, no drop shadows, no 3D.
- **Camera chip** top-left of every cell: dark plate 84 %, a square dot (orange = synced video, grey = unsynced or still), code (`CAM 4`, `DOC`, `LIST`), Chinese name, small English name.
- **Burned-in text in the sources** (broadcast bugs, camera IDs, timers, tracker readouts) is cropped by a per-shot usable region, or blurred out (ffmpeg `delogo`) after it has been used for syncing. Never shown as if it were ours.
- **One grade for every source** (ffmpeg): `eq=contrast=1.07:saturation=0.9:gamma=0.97:brightness=-0.01,colorbalance=rs=-0.02:bs=0.03:rh=0.03:bh=-0.02`, then film grain 1 at the master (`mux.sh … 1`). Cool shadows, slightly warm highlights: control rooms and launch pads look like one film.
- **Resolution**: modern footage at most 1.5× its source pixels; for a punch-in, extract that stretch at a higher resolution from the 4K source instead of enlarging a 1080p frame. Documents at ≥ 1 source pixel per screen pixel.

## 3. Colour logic

| Role | Value |
|---|---|
| Ground | `#06080A`; panels `#0B0E11` |
| Main text | `#F2F5F7`; secondary `#7C878D` |
| Accent: the T− sign, synced dots, ticks done, event flags, the active control segment | `#FF5B1F` |
| Speaking light, "heard" tags | `#FF3B30` |
| Plates over full-screen footage | `rgba(6,8,10,.80)` |
| After zero, the clock block | ground `#FF5B1F`, text `#0A0B0C` (inverted) |

Orange means "now / synced / done". Grey means "pending / not synced". Nothing else is coloured; colour belongs to the footage.

## 4. Type & subtitles

- Clock digits: a condensed sans with fixed-width digit slots (ours: Barlow Condensed SemiBold, drawn digit by digit in equal slots so the clock never jitters); size up to 132 px, the T−/T+ sign at 0.85×, tenths at 0.41× in grey, a ten-segment sub-second bar under it.
- Chinese: a sturdy sans (ours: Noto Sans SC 500/700, subset). English text: a clean grotesque (Barlow). Labels, codes and English small print: a monospace (IBM Plex Mono). All OFL, in the project's `fonts/`.
- **The live transcript is the subtitle.** A fixed box (bottom right, or a cell in the grid): a speaking light and the speaker type (commentary / loop / narrator — the narrator, our own voice, is marked in orange so it is never mistaken for the event's audio), the English line appearing word by word at the spoken times (0.08 s fade per word, a block cursor), the Chinese line whole when its cue starts. **One line per language, never wrapped**: a long sentence becomes two cues; each cue ≥ max(1.8 s, speech + 0.6 s). Transcribe only what is said; mark doubtful words in `FACTS.md`.
- Reading time for everything else: CJK ÷ 4.5 + other ÷ 15 + 1.5 s from the moment it is complete (`readcheck.mjs`). A comparison (two bars, two numbers) stays fully on screen ≥ 2.5 s.

## 5. Motion quality

- 30 fps. Clock: on each whole second the new digits drop 14 px in 0.12 s (ease-out); the sub-second bar empties one segment per 0.1 s (fills after zero).
- Re-layout: 0.34 s `easeInOutCubic`. Cells that stay interpolate their rectangles; new cells open from their left edge; leaving cells close to the left; a new cell flashes a 3 px orange border for ~0.2 s when it lands. A grid filling up pops one cell per spoken count in 0.30 s.
- Swaps (one source replaces another in the same rectangle) wipe in from the left. Hard cuts only between full-screen sources.
- Photographs push in ≤ 6 % over their whole stay; names pop one by one 0.16 s apart. Documents move their window down a row in 0.45 s; the highlight sweeps left to right in 0.35 s.
- Never: slow push-ins on video to fake motion, page-turn transitions, centred pop-up words, speed ramps.

## 6. Edit grammar

- **Screen time = event time.** One mapping, `M = t − T0`, for the whole film. Each camera has its own source offset (`s = M + c`) measured once and baked into the frame extraction (`demo/tools/prep.sh`): frames are named by film frame number, so the page never computes sync.
- **Cut points are calls.** Each layout change starts on the first word of a real call in the native audio ("ten", "go for…", "ignition", a name) or on an event visible in the footage. The music follows; it never sets a cut.
- **Cell count rises toward zero**: 1 → 2 → 3–4 → many (6–9, the clock itself becomes the centre cell, the transcript a cell) → **one** at zero → a few again after zero (the event's consequences) → one under the title. The shortest layouts are nearest to zero.
- **Inside a cell, the source cuts itself** (a broadcast switching cameras): keep it; we only cut the layout.
- **Silence before zero**: the music drops out a quarter-second before zero; only the native sound and the clock remain.
- Full-screen moments carry the clock and transcript as plates at the bottom; a gradient (0 → 75 % black) under them.

## 7. Sound palette

Layers, top to bottom:

1. **Native sound** — the event's own audio (commentary, radio loops, crowd), high-pass 90 Hz, compressed, always on top; never ducked.
2. **Narrator** (sparingly, only in gaps of the native sound, never over it): clean and close, a different gender or accent from the event's voices; Kokoro, every line through `asr_check.py`.
3. **The clock**: a tick every whole second (two alternating pitches around 1.5–1.9 kHz, panned ±15 %), louder in the last ten seconds, a soft single pitch after zero.
4. **Interface foley** from `window.EV`: re-layout whoosh + metallic snap; cell pop snap; checklist tock; event-flag whoosh; full-screen cut thump.
5. **Score**, 60 BPM so one beat = one second = one tick: a low synth drone whose low-pass opens toward zero, a bass drum per beat, off-beat hats, a tom per spoken count, timpani roll into zero, silence, then a low brass major chord with bass drum, crash and tubular bell at zero; after zero a new texture (pizzicato bass ostinato, lighter tick). Low brass, timpani, toms, tubular bells, glockenspiel; no piano-and-strings pad.
- Mix: music about 8–10 dB under the native sound and ducked under speech; the ignition (or the event's own climax sound) is the loudest moment; master −14 LUFS via a pre-limited mix so `mux.sh` meets the true-peak target.
- **Changing the music** (e.g. a Suno track): never move the clock or the cuts; choose or stretch a track so a downbeat lands exactly on zero and a section change lands on T−10, and keep the quarter-second silence before zero.

## 8. Native moves (and how to build them)

- **Many into one.** At zero, every cell moves to its tile of the full frame (a 3×3 grid becomes nine 640×360 tiles) while each tile cross-fades to the same full-screen shot, chips and borders vanish in the first half, a warm white flash (`rgba(255,248,236,.7)`, decay τ ≈ 0.11 s) peaks, and the clock and transcript slide from their grid cells back to the bottom. 0.42 s. *Fits:* a verdict read out; the goal at the final whistle.
- **Clock inversion.** At zero the clock block flips from dark with an orange T− to orange with dark T+, and its header changes (countdown → elapsed). *Fits:* polls closing, a store opening.
- **Control strip.** Segments in the clock header (who has control: ground → vehicle → mission control; prosecution → jury → judge); the active one fills orange on the call that hands it over, with a short flash. The story's turns live here.
- **The grid fills on the count.** Empty grid slots show as dashed "standby" frames; each spoken number opens one camera. *Fits:* "three, two, one" before a premiere.
- **Sync badge.** Top-right of each video cell: `● 实时同步 LIVE SYNC` (synced), `○ 同一时段 · 未逐帧同步 SAME WINDOW` (hatched, grey: footage from the same minutes without a usable clock), `慢动作还原 1× REAL-TIME` (slow-motion re-timed). Honesty is part of the look.
- **Planned vs heard checklist.** Official milestones with their planned times tick as the clock passes them; when the native audio actually says one, a red "heard −32.1" tag with a small waveform appears beside it. *Fits:* a court schedule against what was said; a train timetable against the platform announcement.
- **Second countdown.** After zero, a smaller clock counts to the next official milestone (`−1:47 to booster separation, expected T+2:09`) along a schematic profile drawn by time, not distance. *Fits:* the next race split; the next ballot count.
- **Event flag.** An orange bar with black type slides in at the bottom of the relevant cell on its call (`RS-25 ×4 启动 ENGINE START · T−6.36`), held ≥ the reading time.
- **Punch-in on a call.** A hard digital punch-in on the relevant detail when the commentary names it, from a higher-resolution extraction of the same source.
- **Document by rows.** A paper close-up shows two or three rows; a highlight bar and an annotation band below the paper translate the row; the window moves only between rows (its edges in the white space).

## 9. Pitfalls of the medium

- **Unsyncable footage** (an edited "rover" reel with no clock or event to align on). Never fake it: label the cell "same window · not frame-synced", keep it out of the countdown's key seconds or use it only where nothing it shows contradicts the time, and say so in `FACTS.md`. Look first for a source with a burned-in timer, a visible ignition / flash / whistle, or the same audio.
- **Measuring zero.** Never trust metadata. Combine two independent marks: a visible event (ignition flash, a broadcast countdown bug's flip) and the spoken word timing ("booster" at zero). Re-measure on the file you actually cut: `ffmpeg -ss … -c copy` starts on the previous keyframe.
- **Audio and picture of one file can disagree** (a switched feed whose audio lagged its video by ~1 s). Sync each camera on its picture.
- **Slow-motion sources**: measure the factor from two events with a known gap (e.g. engine start to booster ignition = 6.36 s) and re-time with `setpts=PTS/k`.
- **Burned-in text**: broadcast bugs, camera numbers, timers, tracker data. Define per-shot usable regions (they change when the source cuts) or `delogo` them; check every source cut with a frame-difference scan.
- **A static wide shot for ten seconds** reads as flat. Give every 1–2 seconds a new element (a cell, a tick on the list, a flag, a punch-in), not a fake camera move.
- **Spoilers in the subtitle**: a whole-sentence Chinese line reveals the end of a count early. Split counts into separate cues.
- **The clock jitters** if digits are proportional: draw them in fixed slots.
- **Hot peaks** from broadcast audio and the ignition hit miss the true-peak target: pre-limit the mix at about −4 dBFS after normalising to −14 LUFS.
- **Logos.** No agency insignia as a graphic; cut slates and bugs; the film says it is unofficial.

## 10. Materials, sources, facts, engine

**Materials — ask first.** Before searching, ask the user whether they have their own material of the event: footage from several angles, recordings of the audio, photos, documents (schedules, filings, results), data. What they give comes first and is credited as they say.

**If not, where to look** (each item's own page decides; record it):
- **NASA** (images.nasa.gov, svs.gsfc.nasa.gov): U.S. federal government works, public domain in the U.S.; fine to use. Don't use NASA insignia as graphics or imply endorsement; check each item for third-party material.
- **Other U.S. federal agencies** (NOAA, National Archives, DoD DVIDS): public domain, same check for third-party material.
- **Internet Archive**: only items whose own record shows public domain (pre-1931 U.S. publications, U.S. government works) or CC0 / CC BY; skip `youtube-*` / "mirrortube" uploads and anything of unclear origin.
- **Wikimedia Commons**: read each file page; CC0, public domain and CC BY are fine (credit CC BY in full); CC BY-SA and "no known restrictions" are not fine without the user's explicit agreement.
- **Library of Congress**: check each item's rights statement; "no known restrictions" is not CC0.
- Not usable: re-uploads without a source, restored or colourised versions, news-agency footage, anything whose licence is not stated.

**Before downloading, tell the user** what you will fetch, from where and under which licence, in one message. Then fetch only the seconds you need: `python3 demo/tools/grab.py <nasa_id> <orig|large> <start> <duration> <name> [--copy]` reads an HTTP range of a NASA original; `python3 demo/tools/footage.py search|fetch|used|md` searches NASA, Commons and the Internet Archive and records licence, author and page in `SOURCES.jsonl` / `SOURCES.md` automatically. Keep `raw/` under about 1.5 GB.

**Facts**: a `FACTS.md` (claim, URL, quoted wording, or the measurement) covering every number, time, name and call on screen and in the narration; official sources only; planned times and actual (heard) times are kept apart. Check the script against it before the last render.

**Engine** (copy into the project): `demo/index.html` (Canvas 2D: `LAY` layout keyframes with `grid` / `merge` / `cut` / `swap`, `camRegion()` usable regions, `crop()` cover framing, `drawClock()`, `drawTx()`, `drawCheck()`, `drawDoc()`, `drawProfile()`, `drawThrust()`, `window.EV` for the mix, `window.TEXTS` for `readcheck`, `window.SUBFIT` for the one-line subtitle check), `demo/tools/prep.sh` (the sync table → frames), `demo/tools/subs.mjs` (cues → `audio/cues.json`, one-line and duration check), `demo/audio/mix.py` (native sound, ticks, foley, score, ducking, pre-master), `demo/tools/final_asr.py` (Whisper on the finished film), `demo/tools/fetch_fonts.py`.

## 11. Variation space

The agent decides per film: the event, where real time starts and ends, the number of cameras, which documents and data, the control segments, the narrator's lines (or none), the closing layout.

- **Clocks**: T−/T+; a match clock; a wall clock (HH:MM:SS) for a news day; a countdown to a deadline that then counts up as "overtime".
- **Three structures**: rising cells to a merge (this demo); one cell that splits outward after zero (results arriving from many places); two parallel countdowns side by side that meet at zero (two teams, two cities).
- **Three openings**: a single wide shot and the first call; the clock alone on black, then the first camera opens; a document (the schedule) with the first item ticking.
- **Three endings**: the inverted clock over one full-screen shot; the grid refilling with consequences, then one title; the second countdown reaching its own zero.

---

How our demo was made (story, layouts, score, end card, build): [DEMO.md](https://github.com/lemomo-ai/lemo-opuscar/blob/bebbbe1aa92a3cb4bb6f83500e61b23a17d1aa00/styles/countdown/DEMO.md). Read it after your treatment exists.
