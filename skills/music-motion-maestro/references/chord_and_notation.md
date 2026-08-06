# Chords, Tablature & Notation

Turning `chords.json` and `piano/` into things a musician can actually
play or read.

## Table of contents
1. Presenting the chord progression
2. Guitar: open-chord diagrams, capo, transposition
3. Guitar tablature
4. Piano: from MIDI to readable sheet music
5. Honesty about transcription accuracy

---

## 1. Presenting the chord progression

`chords.json` has `chords[]` (timed segments) and `progression_summary`
(deduped chord flow). Present it two ways:

**A. As a progression** — the harmonic story:
```
Am → F → C → G   (i – VI – III – VII in A minor)
```
Add the Roman-numeral analysis relative to `key` when you can — it teaches
the user *why* it works and helps them transpose.

**B. As a timed chord chart** — for playing along:
```
[0:00] Am | [0:02] F | [0:04] C | [0:06] G   (2 beats each, 128 BPM)
```
Group by bar. If a chord lasts a whole bar, show one per bar; if it changes
mid-bar, split the bar (e.g. `Am  F |`).

## 2. Guitar: open-chord diagrams, capo, transposition

Render common chords as ASCII fretboard diagrams (strings E A D G B e,
left = low E, `x` = muted, `o` = open, numbers = fret):

```
   Am        C         G         F(barre)
e|-0-      e|-0-      e|-3-      e|-1-
B|-1-      B|-1-      B|-0-      B|-1-
G|-2-      G|-0-      G|-0-      G|-2-
D|-2-      D|-2-      D|-0-      D|-3-
A|-0-      A|-3-      A|-2-      A|-3-
E|-x-      E|-x-      E|-3-      E|-1-
```

**Capo advice:** if the progression is full of barre chords (F, Bb),
suggest a capo position that turns them into open chords. Example: songs in
Eb often become easy in D-shapes with a capo on fret 1. State the capo and
the *shapes* the player uses ("capo 1, play as if in D").

**Transposition:** if the user wants an easier or vocal-friendly key, shift
every chord by the same number of semitones and re-name.

## 3. Guitar tablature

For riffs/melody (from `piano/notes.json` or the melody line), lay out
6-line tab. Keep timing loose but ordered; annotate with the beat when it
helps. Tab is for single-note lines and riffs; chords use diagrams above.

## 4. Piano: from MIDI to readable sheet music

The transcription step produces:
- `piano/notes.mid` — raw MIDI.
- `piano/transcription.musicxml` — **open in MuseScore / Finale / Sibelius**
  for engraved, printable sheet music. This is the best deliverable.
- `piano/notes.json` — note events (pitches, start, duration).
- `piano/lead_sheet.txt` — quick top-line melody.

**To render engraved sheet music to an image/PDF** (if tools available):
```bash
# MuseScore (best quality):
mscore piano/transcription.musicxml -o piano/sheet.pdf
# or LilyPond via music21:
python -c "from music21 import converter; \
converter.parse('piano/transcription.musicxml').write('lily.png', 'piano/sheet')"
```

**Lead sheet** = melody staff + chord symbols above it. Combine the piano
melody (`notes.json`) with the chord timeline (`chords.json`) to produce
one: the single most useful artifact for a singer/pianist.

## 5. Honesty about transcription accuracy

Audio→notation is estimation. Set expectations honestly, once:
- **Solo piano / clear lead melody** → high accuracy, minor cleanup.
- **Full-band mix** → the melody and bass come through; inner voices are
  noisier. Great as a starting point to edit, not a final engraving.
- Offer to focus on **just the melody** or **just the chords** if the full
  transcription is messy — usually far more useful than a dense, wrong
  full score.
