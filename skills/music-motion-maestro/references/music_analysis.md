# Interpreting the Music Analysis

How to read `analysis.json` and translate cold numbers into something a
human understands — and into creative direction for the animation.

## Table of contents
1. Tempo (BPM) and feel
2. Beat grid and downbeats
3. Key and mode
4. Structure (sections)
5. Mood: energy and valence
6. Dynamics envelope
7. How to present it to the user

---

## 1. Tempo (BPM) and feel

`bpm` is beats per minute. Rough feel map (use as intuition, not law):

| BPM | Feel | Typical genres |
|-----|------|----------------|
| 60–75 | slow, spacious, ballad | ballads, ambient, downtempo |
| 76–95 | relaxed groove | hip-hop, R&B, reggae |
| 96–115 | mid, walkable | pop, rock, indie |
| 116–130 | driving, danceable | house, pop, disco |
| 128–140 | high energy | EDM, techno, trance |
| 140+ | frantic | DnB, hardcore, footwork |

**Watch for octave errors:** beat trackers sometimes report half or
double the true tempo (e.g. 70 vs 140). If BPM feels wrong for the genre,
mention both the detected value and the half/double, and pick by feel.

## 2. Beat grid and downbeats

- `beat_times[]` — every pulse, in seconds. This is your finest cut grid.
- `downbeats[]` — the "1" of each bar (assumed 4/4). These are the
  **strongest** places to cut in a video; the ear expects change here.
- A bar (measure) = 4 beats in 4/4. One bar's duration = `240 / bpm`
  seconds. Two/four/eight-bar phrases are the natural units of a section.

## 3. Key and mode

`key.tonic` + `key.mode` (major/minor) with a `confidence` (correlation).
- **Major** → generally brighter, happier, resolved.
- **Minor** → generally darker, sad, tense, or dramatic.
- Low confidence (<0.5) or key changes mid-song → say "roughly around X,
  with some movement" rather than stating it as fact.

Use the key for the emotional baseline of the visuals and — if you output
chords — for naming/transposition (see `chord_and_notation.md`).

## 4. Structure (sections)

`sections[]` are structural segments with `start`, `end`, and a normalized
`energy` (0–1) plus a coarse `label` (low/mid/high). These are *detected
boundaries*, not named parts — map them to song logic:

- A **low** early section is usually an **intro**.
- Alternating **mid** and **high** sections are usually **verse / chorus**.
- A single contrasting section late in the song is often a **bridge**.
- The **highest-energy** sections are your **choruses / drops** — spend
  your best visuals there.

Each boundary is a `section-change` event in the sync map — the place to
change world, palette, or energy in the animation.

## 5. Mood: energy and valence

- `energy` (0–1) — how loud/dense/driving it is.
- `valence` (0–1) — how positive/bright it feels (proxy from mode +
  spectral brightness).
- `mood` — a label combining them: *energetic/uplifting*, *intense/dark*,
  *calm/warm*, *somber/mellow*.

This drives the whole visual tone. **Never override the measured mood with
a guess.** A somber minor ballad should not get a neon party animation.

## 6. Dynamics envelope

`dynamics[]` is loudness (dB) sampled over time. Rising runs = **builds**;
sharp jumps = **drops**. The sync map turns these into `build`/`drop`
events. Visually: builds → accelerate motion / accumulate elements; drops
→ hard cut / reveal / release.

## 7. How to present it to the user

After the analysis, always give a one-line human summary before diving in:

> "שיר פופ אנרגטי, **128 BPM**, בסולם **לה מינור**, מבנה של אינטרו־בית־
> פזמון־פזמון עם **drop** חזק בשנייה 47. מצב רוח: energetic/uplifting."

Then offer the deeper artifacts (chord chart, sheet music, sync map,
animation) rather than dumping raw JSON.
