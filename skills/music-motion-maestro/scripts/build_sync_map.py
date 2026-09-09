#!/usr/bin/env python3
"""Merge analysis into a visual sync map — the bridge from sound to motion.

This is the unique core of the skill. It converts the measured musical
timeline into a list of *visual events*, each with a timestamp, a musical
role, and a "visual weight" (how strongly the animation should react
there). Downstream, every animation cut/move is anchored to one of these
events, so the video is locked to the music instead of loosely themed
around it.

Event roles:
  - downbeat       : bar start — strongest cut candidates
  - beat           : regular pulse — micro-motion / rhythm
  - section-change : structural boundary — change world/palette/energy
  - build          : rising energy — accelerate camera / add elements
  - drop           : energy spike after a build — hard cut / reveal
  - accent         : strong onset off the grid — punch/hit

Usage:
    python build_sync_map.py work/analysis.json --chords work/chords.json --out work/sync_map.json
"""
import argparse
import json
import sys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("analysis")
    ap.add_argument("--chords", default=None)
    ap.add_argument("--out", default="work/sync_map.json")
    args = ap.parse_args()

    with open(args.analysis) as f:
        a = json.load(f)

    chords = None
    if args.chords:
        try:
            with open(args.chords) as f:
                chords = json.load(f)
        except FileNotFoundError:
            chords = None

    beats = a.get("beat_times", [])
    downbeats = set(round(x, 3) for x in a.get("downbeats", []))
    sections = a.get("sections", [])
    dynamics = a.get("dynamics", [])
    onsets = a.get("onset_times", [])

    events = []

    # Beats + downbeats.
    for t in beats:
        is_db = round(t, 3) in downbeats
        events.append({
            "t": round(float(t), 3),
            "role": "downbeat" if is_db else "beat",
            "weight": 0.8 if is_db else 0.35,
        })

    # Section boundaries.
    section_labels = {}
    for s in sections:
        events.append({"t": round(float(s["start"]), 3), "role": "section-change",
                       "weight": 1.0, "section_energy": s.get("energy"),
                       "section_label": s.get("label")})
        section_labels[round(float(s["start"]), 3)] = s.get("label")

    # Build / drop detection from the dynamics envelope.
    for i in range(2, len(dynamics)):
        prev = dynamics[i - 2]["db"]
        cur = dynamics[i]["db"]
        delta = cur - prev
        if delta >= 4.5:  # sharp rise into a section => drop moment
            events.append({"t": round(float(dynamics[i]["t"]), 3), "role": "drop",
                           "weight": 1.0, "db_jump": round(delta, 1)})
        elif 1.5 <= delta < 4.5:
            events.append({"t": round(float(dynamics[i]["t"]), 3), "role": "build",
                           "weight": 0.6, "db_jump": round(delta, 1)})

    # Strong accents = onsets that don't coincide with a beat.
    beatset = set(round(b, 2) for b in beats)
    for o in onsets:
        if round(o, 2) not in beatset:
            events.append({"t": round(float(o), 3), "role": "accent", "weight": 0.5})

    # Attach the ruling chord to each event (nice for lyric/visual cues).
    if chords and chords.get("chords"):
        cseg = chords["chords"]
        for ev in events:
            ev["chord"] = _chord_at(cseg, ev["t"])

    events.sort(key=lambda e: (e["t"], -e["weight"]))

    out = {
        "bpm": a.get("bpm"),
        "key": a.get("key"),
        "mood": a.get("mood"),
        "duration_sec": a.get("duration_sec"),
        "sections": sections,
        "events": events,
        "cut_grid": {
            "on_downbeats": [e["t"] for e in events if e["role"] == "downbeat"],
            "on_drops": [e["t"] for e in events if e["role"] == "drop"],
            "section_changes": [e["t"] for e in events if e["role"] == "section-change"],
        },
    }
    with open(args.out, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"{len(events)} visual events | "
          f"{len(out['cut_grid']['on_downbeats'])} downbeats | "
          f"{len(out['cut_grid']['on_drops'])} drops | "
          f"{len(out['cut_grid']['section_changes'])} section changes")
    print(f"Saved -> {args.out}")
    return 0


def _chord_at(cseg, t):
    for c in cseg:
        if c["start"] <= t < c["end"]:
            return c["chord"]
    return None


if __name__ == "__main__":
    sys.exit(main())
