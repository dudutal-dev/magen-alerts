# Sync Choreography — Locking Motion to Music

This is the heart of the skill. Anyone can write an animation prompt;
almost no one anchors it to the *actual* musical timeline. This document
turns `sync_map.json` into visual choreography where every cut and move
lands where the ear expects it.

## Table of contents
1. The golden rule
2. Reading the sync map
3. Mapping musical roles → visual actions
4. Cutting to the grid (bars, phrases, downbeats)
5. Dynamics → motion energy
6. Building the shot list
7. Worked micro-example

---

## 1. The golden rule

**Cuts and major motion changes land on `downbeat`, `section-change`, and
`drop` events. Micro-motion rides the `beat`s. Accents get punches.**

If a viewer feels the video "moving with" the song, you've succeeded. If it
looks like nice footage laid loosely over audio, you haven't — go back and
anchor the timings.

## 2. Reading the sync map

`sync_map.json` gives you:
- `events[]` — each with `t` (seconds), `role`, `weight` (0–1 reaction
  strength), and often the ruling `chord`.
- `cut_grid` — pre-extracted lists: `on_downbeats`, `on_drops`,
  `section_changes`. **Use `cut_grid` to place your cuts directly.**
- `sections[]`, `bpm`, `key`, `mood` for the overall plan.

One bar = `240 / bpm` seconds. A comfortable shot is often 1, 2, or 4 bars
— always ending on a downbeat, never on an arbitrary second count.

## 3. Mapping musical roles → visual actions

| Role | Visual action |
|------|---------------|
| `section-change` | Change the world: new location, palette shift, energy step. The biggest visual gear-changes go here. |
| `drop` | Hard cut + reveal / burst / speed-ramp release. The single most impactful visual moment. |
| `build` | Accelerate: push-in that speeds up, elements accumulating, camera rising, particles gathering. Tension before the drop. |
| `downbeat` | Primary cut points and strong motion hits (a step, a turn, an impact). |
| `beat` | Micro-motion: bounce, pulse, blink, sway, light flicker — small things on the pulse. |
| `accent` | A punch: quick zoom, flash, snap, a particle burst off the grid. |

## 4. Cutting to the grid (bars, phrases, downbeats)

- **Fast section (high energy / chorus / drop):** cut every 1–2 bars, or
  even every downbeat for intensity. Motion is big and directional.
- **Slow section (intro / verse / ballad):** long takes of 4–8 bars, slow
  continuous camera moves; let one gesture breathe across the phrase.
- **Always end a shot on a downbeat or section boundary.** Ending a shot
  mid-bar reads as a mistake.
- **Phrase awareness:** music usually moves in 4- and 8-bar phrases. Let
  your biggest visual statements align to phrase starts, not just any bar.

## 5. Dynamics → motion energy

Map the loudness envelope to how *much* things move:
- Loud / dense → fast cuts, big camera moves, many elements, high contrast.
- Quiet / sparse → slow, minimal, negative space, gentle drift.
- A **build** should *visibly accelerate*; the **drop** is the payoff —
  the release of everything the build accumulated.

This contrast is what makes it feel choreographed rather than uniform.

## 6. Building the shot list

For each section in `sections[]`:
1. State the section's role (intro/verse/chorus/etc.) and energy.
2. Decide cut rhythm (bars-per-shot) from its energy (§4).
3. List shots; for each shot record: `start`–`end` (seconds, on the grid),
   the sync events it covers, and the one clear action.
4. Write the full animation prompt per shot using
   `assets/templates/animation_prompt_template.md`, filling the **Sync**
   field with the exact timestamps/events it must hit.

Keep the **Style Bible anchors identical** across every shot (see
`animation_prompting.md`) so the world stays consistent while the *timing*
tracks the music.

## 7. Worked micro-example

Song: 120 BPM (1 bar = 2.0 s), A minor, drop at 0:32.

```
Section: Chorus  (0:32–0:48, energy high) — drop at 0:32
Cut rhythm: 1 bar/shot (high energy)

Shot 1  0:32–0:34  covers: drop@0:32, downbeat@0:32
  Action: hard cut to wide — the dancer bursts into a spin as the beat drops;
          confetti explodes outward on the hit.
  Sync: cut exactly on 0:32 drop; spin accent lands on downbeat 0:32.

Shot 2  0:34–0:36  covers: downbeat@0:34, beats@0:34/0:35
  Action: medium push-in; her steps land on each beat (0:34, 0:35),
          lights pulse on the pulse.
  Sync: micro-motion on beats; cut on downbeat 0:36.
```

Every timestamp above comes from the sync map — nothing is invented. That
is the whole point.
