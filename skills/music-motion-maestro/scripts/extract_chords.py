#!/usr/bin/env python3
"""Beat-synchronous chord recognition via chroma template matching.

Self-contained: no exotic chord libraries. We compute a beat-synchronous
chromagram and match each beat's chroma against major/minor triad
templates (all 12 roots), then merge consecutive identical chords into
timed segments aligned to the beat grid from analyze_music.py.

This is a solid, transparent baseline. For pop/rock progressions it is
usually very usable; dense jazz voicings are harder (documented honestly).

Usage:
    python extract_chords.py work/audio.wav --beats work/analysis.json --out work/chords.json
"""
import argparse
import json
import sys

import numpy as np

_PITCHES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def build_templates():
    """12 major + 12 minor triad chroma templates."""
    templates, names = [], []
    for root in range(12):
        maj = np.zeros(12); maj[[root, (root + 4) % 12, (root + 7) % 12]] = 1
        minr = np.zeros(12); minr[[root, (root + 3) % 12, (root + 7) % 12]] = 1
        templates.append(maj / np.linalg.norm(maj)); names.append(f"{_PITCHES[root]}")
        templates.append(minr / np.linalg.norm(minr)); names.append(f"{_PITCHES[root]}m")
    return np.array(templates), names


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--beats", required=True, help="analysis.json with beat_times")
    ap.add_argument("--out", default="work/chords.json")
    args = ap.parse_args()

    try:
        import librosa
    except ImportError:
        print("librosa not installed. Run: pip install librosa", file=sys.stderr)
        return 1

    with open(args.beats) as f:
        analysis = json.load(f)
    beat_times = np.array(analysis.get("beat_times", []), dtype=float)
    if len(beat_times) < 2:
        print("Not enough beats in analysis.json — run analyze_music.py first.", file=sys.stderr)
        return 1

    y, sr = librosa.load(args.audio, sr=None, mono=True)
    hop = 512
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop)

    beat_frames = librosa.time_to_frames(beat_times, sr=sr, hop_length=hop)
    beat_frames = np.clip(beat_frames, 0, chroma.shape[1] - 1)
    beat_chroma = librosa.util.sync(chroma, beat_frames, aggregate=np.mean)

    templates, names = build_templates()
    # Normalize each beat's chroma, then score against templates.
    bc = beat_chroma / (np.linalg.norm(beat_chroma, axis=0, keepdims=True) + 1e-9)
    scores = templates @ bc  # (24, n_beats)
    best = np.argmax(scores, axis=0)
    per_beat = [names[i] for i in best]

    # Merge consecutive identical chords into timed segments.
    segments = []
    i = 0
    n = min(len(per_beat), len(beat_times) - 1)
    while i < n:
        j = i
        while j + 1 < n and per_beat[j + 1] == per_beat[i]:
            j += 1
        segments.append({
            "start": round(float(beat_times[i]), 3),
            "end": round(float(beat_times[min(j + 1, len(beat_times) - 1)]), 3),
            "chord": per_beat[i],
            "beats": j - i + 1,
        })
        i = j + 1

    progression = _dedupe_progression([s["chord"] for s in segments])

    out = {
        "key": analysis.get("key"),
        "bpm": analysis.get("bpm"),
        "chords": segments,
        "progression_summary": progression,
    }
    with open(args.out, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("Progression: " + " → ".join(progression[:16]) + (" ..." if len(progression) > 16 else ""))
    print(f"{len(segments)} chord segments. Saved -> {args.out}")
    return 0


def _dedupe_progression(seq):
    out = []
    for c in seq:
        if not out or out[-1] != c:
            out.append(c)
    return out


if __name__ == "__main__":
    sys.exit(main())
