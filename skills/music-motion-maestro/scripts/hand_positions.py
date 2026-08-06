#!/usr/bin/env python3
"""Turn chords/notes into concrete hand placements for a performer.

This makes the storyboard's musician *believable*: it maps each chord to a
real guitar fingering (fret per string + a mini fretboard diagram + a plain
sentence you can paste into an image prompt) and to real piano keys (note
names + octave + right-hand finger numbers).

Standalone, stdlib only.

Usage:
    # single chord, quick:
    python hand_positions.py --chord Am --instrument both
    # drive from analysis outputs:
    python hand_positions.py --chords work/chords.json \
        --notes work/piano/notes.json --instrument both --out work/hands.json
"""
import argparse
import json
import sys

PITCHES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
STRINGS_LOW_TO_HIGH = ["E", "A", "D", "G", "B", "e"]  # 6th -> 1st

# Open/barre voicings, low E -> high e. 'x' mute, 0 open, int = fret.
GUITAR = {
    "C":  ["x", 3, 2, 0, 1, 0], "C#": ["x", 4, 6, 6, 6, 4],
    "D":  ["x", "x", 0, 2, 3, 2], "D#": ["x", 6, 8, 8, 8, 6],
    "E":  [0, 2, 2, 1, 0, 0], "F":  [1, 3, 3, 2, 1, 1],
    "F#": [2, 4, 4, 3, 2, 2], "G":  [3, 2, 0, 0, 0, 3],
    "G#": [4, 6, 6, 5, 4, 4], "A":  ["x", 0, 2, 2, 2, 0],
    "A#": ["x", 1, 3, 3, 3, 1], "B":  ["x", 2, 4, 4, 4, 2],
    "Cm":  ["x", 3, 5, 5, 4, 3], "C#m": ["x", 4, 6, 6, 5, 4],
    "Dm":  ["x", "x", 0, 2, 3, 1], "D#m": ["x", 6, 8, 8, 7, 6],
    "Em":  [0, 2, 2, 0, 0, 0], "Fm":  [1, 3, 3, 1, 1, 1],
    "F#m": [2, 4, 4, 2, 2, 2], "Gm":  [3, 5, 5, 3, 3, 3],
    "G#m": [4, 6, 6, 4, 4, 4], "Am":  ["x", 0, 2, 2, 1, 0],
    "A#m": ["x", 1, 3, 3, 2, 1], "Bm":  ["x", 2, 4, 4, 3, 2],
}


def parse_chord(name):
    name = name.strip()
    if name.endswith("m") and name[:-1] in PITCHES:
        return name[:-1], "minor"
    if name in PITCHES:
        return name, "major"
    # tolerate 7ths etc. by falling back to the triad
    for suf in ("maj7", "7", "m7", "sus4", "sus2", "add9", "9", "6"):
        if name.endswith(suf) and name[: -len(suf)] in PITCHES:
            base = name[: -len(suf)]
            return base, ("minor" if suf.startswith("m") else "major")
    return None, None


def guitar_fingering(name):
    shape = GUITAR.get(name)
    if not shape:
        return None
    fretted = [f for f in shape if isinstance(f, int) and f > 0]
    base = min(fretted) if fretted else 0
    has_open = any(f == 0 for f in shape)
    # Barre if the base fret is held on 2+ strings AND no open strings ring
    # (open strings mean it's an open-position chord, not a barre).
    barre = base > 0 and not has_open and sum(1 for f in shape if f == base) >= 2

    # ASCII fretboard: rows = strings high->low for readability.
    lines = []
    for i in reversed(range(6)):  # high e -> low E
        f = shape[i]
        cell = "x" if f == "x" else ("o" if f == 0 else str(f))
        lines.append(f"{STRINGS_LOW_TO_HIGH[i]:>2}|-{cell}-")
    diagram = "\n".join(lines)

    if barre:
        placement = (f"left hand barres all strings at fret {base} with the "
                     f"index finger, the remaining fingers forming the "
                     f"{'minor' if name.endswith('m') else 'major'} shape above it")
    elif base == 0 or has_open:
        placement = ("left hand in an open position near the nut (frets 0-3), "
                     "fingers pressing the fretted strings, others ringing open")
    else:
        placement = (f"left hand around fret {base}, fingers pressing the "
                     f"chord shape")
    return {"chord": name, "shape_low_to_high": shape, "base_fret": base,
            "barre": barre, "diagram": diagram, "placement": placement}


def piano_keys(name, octave=4):
    root, qual = parse_chord(name)
    if root is None:
        return None
    r = PITCHES.index(root)
    intervals = [0, 4, 7] if qual == "major" else [0, 3, 7]
    fingers = [1, 3, 5]  # right-hand root position
    keys = []
    for iv, fg in zip(intervals, fingers):
        idx = r + iv
        octv = octave + idx // 12
        keys.append({"note": PITCHES[idx % 12], "octave": octv, "finger": fg})
    placement = ("right hand in root position: " +
                 ", ".join(f"finger {k['finger']} on {k['note']}{k['octave']}"
                           for k in keys))
    return {"chord": name, "quality": qual, "keys": keys, "placement": placement}


def piano_register_from_notes(notes_path):
    try:
        with open(notes_path) as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    pitches = []
    for n in data.get("notes", []):
        pitches.extend(n.get("pitches", []))
    if not pitches:
        return None
    return {"note_events": data.get("count"),
            "lowest": min(pitches, default=None),
            "highest": max(pitches, default=None),
            "hint": "left hand covers the lower notes, right hand the melody/higher register"}


def one(name, instrument):
    out = {"chord": name}
    if instrument in ("guitar", "both"):
        out["guitar"] = guitar_fingering(name)
    if instrument in ("piano", "both"):
        out["piano"] = piano_keys(name)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chord", help="single chord, e.g. Am")
    ap.add_argument("--chords", help="chords.json from extract_chords.py")
    ap.add_argument("--notes", help="piano/notes.json (optional, for register)")
    ap.add_argument("--instrument", choices=["guitar", "piano", "both"], default="both")
    ap.add_argument("--out", help="write JSON here (else print)")
    args = ap.parse_args()

    result = {"instrument": args.instrument, "positions": []}

    if args.chord:
        result["positions"].append(one(args.chord, args.instrument))
    elif args.chords:
        with open(args.chords) as f:
            cdata = json.load(f)
        seen = {}
        for seg in cdata.get("chords", []):
            ch = seg["chord"]
            if ch not in seen:
                seen[ch] = one(ch, args.instrument)
            entry = dict(seen[ch])
            entry["start"] = seg.get("start")
            entry["end"] = seg.get("end")
            result["positions"].append(entry)
    else:
        print("Provide --chord or --chords.", file=sys.stderr)
        return 1

    if args.notes:
        reg = piano_register_from_notes(args.notes)
        if reg:
            result["piano_register"] = reg

    if args.out:
        with open(args.out, "w") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(result['positions'])} placements -> {args.out}")
    else:
        _pretty(result)
    return 0


def _pretty(result):
    for p in result["positions"]:
        print(f"\n=== {p['chord']} ===")
        g = p.get("guitar")
        if g:
            print("GUITAR:")
            print(g["diagram"])
            print("  " + g["placement"])
        pi = p.get("piano")
        if pi:
            print("PIANO:")
            print("  " + pi["placement"])
    if result.get("piano_register"):
        print("\nPiano register:", result["piano_register"]["hint"],
              f"(lowest {result['piano_register']['lowest']}, "
              f"highest {result['piano_register']['highest']})")


if __name__ == "__main__":
    sys.exit(main())
