# Writing High-Quality, Complex Animation Prompts

How to write animation prompts that look like a studio made them —
consistent, cinematic, and rich — for modern AI video tools. Pair this
with `sync_choreography.md` to lock them to the music.

## Table of contents
1. The anatomy of a great animation prompt
2. Visual consistency (the Style Bible)
3. Cinematic language you should actually use
4. Motion & camera vocabulary
5. Tool-by-tool notes (Sora, Veo, Kling, Runway, Luma, Pika, Hailuo)
6. Common failure modes and fixes

---

## 1. The anatomy of a great animation prompt

A strong prompt is layered, not a run-on sentence. Cover these layers, in
roughly this order, every time:

1. **Subject** — who/what, described concretely (not "a person" but "a
   young dancer in a red silk dress").
2. **Action / motion** — what moves, and how (the verb matters most for
   video).
3. **Environment** — where, with depth cues (foreground/midground/back).
4. **Style / medium** — 3D Pixar-style, 2D cel anime, claymation,
   photoreal, motion-graphics, ink-and-watercolor, etc.
5. **Camera** — shot size + movement (see §4).
6. **Lighting** — source, direction, quality, color temperature.
7. **Color palette** — 2–4 anchor colors tied to the song's mood.
8. **Mood / atmosphere** — the feeling, in a couple of adjectives.
9. **Detail & texture** — grain, bokeh, particles, material qualities.

Write in confident, present-tense, visual language. Prefer showing motion
("petals swirl upward and scatter") over static description.

## 2. Visual consistency (the Style Bible)

The #1 thing that separates amateur from pro AI video is **consistency
across shots**. Before writing any shot, lock a short **Style Bible** and
repeat its anchors in *every* prompt:

- **Style descriptor** — one exact phrase reused verbatim (e.g.
  "stylized 3D, soft global illumination, Pixar-adjacent").
- **Palette** — the same 2–4 colors named every time.
- **Character/element sheet** — fixed description of the recurring subject
  (hair, wardrobe, proportions, signature detail). Reuse word-for-word.
- **World rules** — lighting logic, lens feel, grain.

Consistency comes from *repetition of exact phrases*, not from asking the
model to "keep it consistent." Copy the anchors into each shot.

## 3. Cinematic language you should actually use

- **Shot sizes:** extreme wide (EWS), wide (WS), full, medium (MS),
  close-up (CU), extreme close-up (ECU), macro.
- **Angles:** eye-level, low-angle (heroic), high-angle (vulnerable),
  top-down / bird's-eye, dutch tilt (unease).
- **Lensing:** wide 24mm (expansive, slight distortion), 50mm (natural),
  85mm (portrait compression, creamy bokeh), macro.
- **Lighting:** golden hour, blue hour, hard noon, rim/backlight, soft
  key, chiaroscuro, neon practicals, volumetric god-rays.
- **Depth:** shallow depth of field, rack focus, deep focus, atmospheric
  haze for layering.

## 4. Motion & camera vocabulary

Video lives and dies on motion. Be specific:

- **Camera moves:** push-in / dolly-in, pull-out, truck left/right,
  crane up, tilt, whip-pan, orbit / arc, drone fly-through, handheld sway,
  slow zoom, snap-zoom.
- **Subject motion:** describe speed and arc ("she spins slowly, dress
  blooming outward", "the city lights streak past in long exposure").
- **Speed ramps:** slow-motion, speed-up, freeze then burst — these are
  your best friends for hitting musical accents (see sync doc).
- **Transitions:** match-cut, whip-pan transition, light-flare wipe,
  morph, mask reveal, cut-on-action.

## 5. Tool-by-tool notes

General rule: all of these like *clear subject + strong motion verb +
style + camera*. Differences:

- **Sora (OpenAI):** handles long, descriptive paragraphs and complex
  scenes; great physical coherence. Give it a rich single paragraph with
  camera + lighting. Good at storyboards of multiple beats.
- **Veo (Google):** strong prompt adherence and realistic motion; responds
  well to explicit camera terms and cinematic lighting. Supports longer
  coherent clips.
- **Kling:** excellent motion and character consistency; strong with
  image-to-video (feed a locked keyframe for consistency). Keep motion
  descriptions concrete.
- **Runway (Gen-3/4):** precise camera control via motion brush / camera
  settings; keep the text prompt focused, control motion in the UI.
- **Luma (Dream Machine):** fluid, dreamy motion; great for organic
  camera moves and morphs. Loves atmospheric prompts.
- **Pika:** fast, stylized; good for punchy short beats and effects
  ("Pikaffects"). Keep it snappy.
- **Hailuo (MiniMax):** strong realism and motion on short clips; concise
  prompts with one clear action work best.

For consistency on any tool, prefer **image-to-video**: generate/lock a
keyframe image (same character each time) and animate from it.

## 6. Common failure modes and fixes

| Problem | Fix |
|---------|-----|
| Character morphs between shots | Reuse the exact character-sheet phrasing; use image-to-video from one keyframe |
| Flat, static clip | Add an explicit camera move + a subject motion verb |
| Muddy, generic look | Name a specific style, palette, lens, and lighting |
| Too much in one shot | One subject + one clear action per shot; split the rest |
| Motion ignores the beat | Anchor each move to a sync-map timestamp (see sync doc) |
| Overlong prompt rambles | Use the layered structure; cut adjectives that don't add an image |
