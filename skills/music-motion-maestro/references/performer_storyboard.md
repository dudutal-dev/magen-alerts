# Performer Storyboard — a Musician Character That Actually Plays

A reusable specialty: build a **storyboard of a character performing** a
song on **guitar or piano**, where the body moves to the groove and — the
part almost everyone gets wrong — **the hands are in the correct positions
for the chords/notes actually being played**. Lock the character once, and
reuse it for *any* song by re-driving the hands from that song's analysis.

## Table of contents
1. Why hand accuracy matters
2. The reusable Performer Character Sheet
3. Guitar: left hand on the neck, right hand, body motion
4. Piano: hand span, key positions, posture
5. Driving hands from the analysis (the data link)
6. Storyboard structure (panels)
7. Style variants (3D realistic, 3D animated, 2D, etc.)
8. Prompts adapted per tool (GPT/DALL·E, Gemini, Midjourney, Sora, Kling)

---

## 1. Why hand accuracy matters

Audiences — especially anyone who plays — instantly feel a "fake" musician:
a guitarist strumming with a limp left hand nowhere near a real chord
shape, or a pianist's fingers mashing random keys. Getting the **left-hand
fret position** and the **piano key cluster** right is what makes the
performance believable. We already have the real chords (`chords.json`)
and notes (`notes.json`) from the analysis, and `scripts/hand_positions.py`
converts them into concrete finger placements. Use them.

## 2. The reusable Performer Character Sheet

Lock this **once** and reuse the exact wording for every shot and every
song — this is what keeps the character consistent (see
`animation_prompting.md` on consistency). Fill
`assets/templates/performer_storyboard_template.md`:

- **Identity:** age, build, face, hair, wardrobe, signature detail.
- **Instrument:** exact guitar (type/color/body) or piano (grand/upright,
  color), so it never morphs.
- **Framing defaults:** the character sheet also fixes the "hero" angles
  you'll reuse (¾ front, side, hands close-up).
- **Style anchor:** one exact style phrase (see §7).

Reuse = paste the identical block into every panel prompt. Consistency
comes from repetition of exact phrases, not from asking for it.

## 3. Guitar: left hand on the neck, right hand, body motion

**Left hand (fretting) — the believable part:**
- Position it at the **fret of the current chord**. Open chords (Em, Am, C,
  G, D) sit near the nut (frets 0–3); barre chords climb the neck (e.g. an
  F barre at fret 1, a B‑flat around fret 1–6 depending on shape).
- Describe the *shape*: "index barres the strings, ring and middle fingers
  form the chord above it" — not just "hand on the neck".
- When the chord changes (from `chords.json`/`sync_map`), the hand
  **slides/reshapes on that beat**. That motion, synced to the chord
  change, is the money shot.

**Right hand (strumming/picking):**
- Strums fall on the rhythm — downstrokes on strong beats, up on offbeats.
- On accents/downbeats the arm gives a bigger stroke; in quiet parts,
  gentle fingerpicking.

**Body motion:**
- Subtle groove: weight shift, head nod, shoulder sway **on the beat**;
  a bigger lean-in on builds and drops. Keep it musical, not frantic.

## 4. Piano: hand span, key positions, posture

- Place hands over the **register the notes live in** (from `notes.json`):
  low notes → left hand toward the low keys, melody → right hand higher.
- For a chord, the fingers cover the actual triad keys (e.g. C major →
  thumb C, middle E, pinky G). `hand_positions.py` gives the exact keys and
  a sensible finger assignment.
- **Posture:** curved fingers, relaxed wrists, upright back; forearms
  roughly parallel to the floor. Pedal foot moves on harmony changes.
- Body sways gently from the torso on the beat; bigger lean on swells.

## 5. Driving hands from the analysis (the data link)

```bash
python scripts/hand_positions.py --chords work/chords.json \
    --notes work/piano/notes.json --instrument both --out work/hands.json
# or ad-hoc for a single chord:
python scripts/hand_positions.py --chord Am --instrument guitar
```

`hands.json` gives, per chord/timestamp: the **guitar fingering** (fret per
string + fingers + a mini fretboard diagram) and the **piano keys** (note
names + octave + finger numbers). Feed these strings straight into the
hand-placement field of each storyboard panel so the drawing matches the
music. When the chord changes on a beat, that's when the hand moves.

## 6. Storyboard structure (panels)

A storyboard is a sequence of still panels (keyframes) that a video tool
then animates. For a performer, a good default set per section:

1. **Establishing** — full body + instrument, ¾ front, sets the scene.
2. **Performance medium** — waist-up, both hands visible on the instrument.
3. **Hands close-up** — the fretting hand / the keys, in the *correct*
   position for the current chord (this sells realism).
4. **Emotion** — face/expression on a musical peak (chorus/drop).

Anchor each panel's timing to the sync map (`sync_choreography.md`): the
hands-close-up should land where the chord changes; the emotion panel on
the chorus/drop. Repeat the set per section, escalating energy.

## 7. Style variants (specialize in all)

Use one **exact** style phrase per project, reused everywhere:

- **3D realistic / photoreal:** "photorealistic 3D render, physically based
  materials, cinematic lighting, subsurface skin detail, 50mm lens".
- **3D animated (Pixar/DreamWorks-adjacent):** "stylized 3D character,
  soft global illumination, appealing proportions, subsurface skin,
  expressive rig".
- **2D cel / anime:** "clean 2D cel animation, bold line art, flat shading
  with soft gradients".
- **Painterly / motion-graphics / claymation / pixel:** name the medium
  precisely and keep textures consistent.

Whatever the style, the **hand positions stay physically correct** — style
changes the render, not the musicianship.

## 8. Prompts adapted per tool

The storyboard *stills* are usually made in an image model, then animated.
Adapt phrasing:

- **GPT‑4o / DALL·E (ChatGPT):** conversational, descriptive sentences;
  great at following explicit instructions like "left hand forms an A‑minor
  shape at the second fret, index on the D string." Ask for a specific
  panel and camera; iterate by referencing the previous image.
- **Google Gemini (Imagen):** concise, well-structured descriptions;
  responds well to clear subject + explicit hand instruction + style +
  camera. Good at photoreal.
- **Midjourney:** dense comma-separated descriptors + parameters
  (`--ar 16:9`, style refs); use a character reference image (`--cref`) to
  keep the performer consistent across panels.
- **Sora / Veo / Kling / Runway (video):** feed the locked keyframe image
  (image‑to‑video) and describe the *motion* — the strum, the hand slide on
  the chord change, the body sway on the beat. Kling/Runway are especially
  strong at keeping the character consistent from a keyframe.

**Golden pattern:** generate a consistent keyframe still (image model) →
animate it (video model), with the hand motion synced to the chord change
from the sync map. That gives a believable, reusable performer for any song.
