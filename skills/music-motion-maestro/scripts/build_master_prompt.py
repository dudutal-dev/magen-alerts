#!/usr/bin/env python3
"""Assemble ONE master prompt for a whole clip, from all the analysis.

This is the capstone: instead of hand-writing shot after shot, it reads the
sync map + chords + hand positions and emits a single, self-contained
"MASTER PROMPT" that covers the *entire* piece — every section, every chord
change with the correct hand placement, and every movement cue locked to
the beat. Paste it into an image/video model to generate the full,
music-perfect performer storyboard. Reusable: swap in a new song's analysis
and you get a new master prompt for the same locked character.

Usage:
    python build_master_prompt.py work/sync_map.json \
        --chords work/chords.json --hands work/hands.json \
        --instrument guitar --style "stylized 3D, soft global illumination" \
        --character "young musician, tousled hair, denim jacket" \
        --title "My Song" --out work/master_prompt.md
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def load(path):
    if not path:
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def chord_at(chords, t):
    if not chords:
        return None
    for c in chords.get("chords", []):
        if c["start"] <= t < c["end"]:
            return c["chord"]
    return None


def hand_for(hands, chord, instrument):
    """Return a placement sentence for a chord, from hands.json or computed."""
    if not chord:
        return None
    if hands:
        for p in hands.get("positions", []):
            if p.get("chord") == chord:
                if instrument == "guitar" and p.get("guitar"):
                    return p["guitar"]["placement"]
                if instrument == "piano" and p.get("piano"):
                    return p["piano"]["placement"]
    # fallback: compute on the fly
    try:
        import hand_positions as hp
        one = hp.one(chord, instrument)
        node = one.get("guitar" if instrument == "guitar" else "piano")
        return node["placement"] if node else None
    except Exception:
        return None


def bars_per_shot(label):
    return {"high": 1, "mid": 2, "low": 4}.get(label, 2)


def cue_for(label):
    return {
        "high": "big body lean and sway on the beat; strong strokes/attacks",
        "mid": "steady groove, head nod and weight shift on the beat",
        "low": "gentle, minimal sway; let gestures breathe across the phrase",
    }.get(label, "groove on the beat")


def build_shots(sync, chords, hands, instrument):
    bpm = sync.get("bpm") or 120
    bar = 240.0 / bpm
    downbeats = sorted(sync.get("cut_grid", {}).get("on_downbeats", []))
    drops = set(round(x, 2) for x in sync.get("cut_grid", {}).get("on_drops", []))
    sections = sync.get("sections", []) or [{"start": 0, "end": sync.get("duration_sec", 0),
                                             "label": "mid"}]

    def snap(t):
        # snap a time to the nearest downbeat, if any is close
        if not downbeats:
            return round(t, 2)
        nearest = min(downbeats, key=lambda d: abs(d - t))
        return round(nearest if abs(nearest - t) <= bar * 0.6 else t, 2)

    # Chord-change times, used so a panel never spans two chords (a single
    # hand can only hold one shape — hand accuracy would break otherwise).
    chord_starts = [c["start"] for c in (chords.get("chords", []) if chords else [])]

    shots = []
    for si, sec in enumerate(sections, 1):
        label = sec.get("label", "mid")
        step = bars_per_shot(label) * bar
        panel_types = ["establishing", "performance-medium", "hands-close-up", "emotion"]

        # Candidate cut points: the rhythmic grid PLUS every chord change
        # inside the section, snapped to downbeats and deduped.
        cuts = {round(sec["start"], 2), round(sec["end"], 2)}
        g = sec["start"] + step
        while g < sec["end"] - 1e-3:
            cuts.add(snap(g))
            g += step
        for cs in chord_starts:
            if sec["start"] + 1e-3 < cs < sec["end"] - 1e-3:
                cuts.add(round(cs, 2))
        ordered = sorted(c for c in cuts if sec["start"] - 1e-3 <= c <= sec["end"] + 1e-3)

        k = 0
        for a, b in zip(ordered, ordered[1:]):
            if b - a < 1e-2:
                continue
            t, end = a, b
            mid = (t + end) / 2.0
            ch = chord_at(chords, mid)
            is_drop = any(abs(d - t) < bar * 0.5 for d in drops)
            shots.append({
                "section": si, "label": label,
                "start": round(t, 2), "end": round(end, 2),
                "panel": panel_types[k % len(panel_types)],
                "chord": ch,
                "hand": hand_for(hands, ch, instrument),
                "movement": cue_for(label),
                "is_drop": is_drop,
            })
            k += 1
    return shots, bar


def mmss(t):
    return f"{int(t // 60)}:{int(t % 60):02d}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sync_map")
    ap.add_argument("--chords")
    ap.add_argument("--hands")
    ap.add_argument("--instrument", choices=["guitar", "piano"], default="guitar")
    ap.add_argument("--style", default="[LOCK ONE STYLE — e.g. stylized 3D, soft global illumination]")
    ap.add_argument("--character", default="[LOCK CHARACTER — age, build, hair, wardrobe, signature detail]")
    ap.add_argument("--palette", default="[2-4 anchor colors]")
    ap.add_argument("--title", default="Untitled")
    ap.add_argument("--out", default="work/master_prompt.md")
    args = ap.parse_args()

    sync = load(args.sync_map)
    if not sync:
        print("Could not read sync_map.json — run build_sync_map.py first.", file=sys.stderr)
        return 1
    chords = load(args.chords)
    hands = load(args.hands)

    shots, bar = build_shots(sync, chords, hands, args.instrument)
    key = sync.get("key") or {}
    key_str = f"{key.get('tonic','?')} {key.get('mode','')}".strip()
    inst = args.instrument

    lines = []
    lines.append(f"# 🎬 MASTER PROMPT — Performer Storyboard: \"{args.title}\"")
    lines.append("")
    lines.append(f"> One prompt, whole clip. {sync.get('bpm')} BPM · key {key_str} · "
                 f"mood {sync.get('mood')} · {mmss(sync.get('duration_sec') or 0)} · "
                 f"bar = {bar:.2f}s · instrument: {inst}")
    lines.append("")
    lines.append("## GLOBAL DIRECTIVE (read first)")
    lines.append("Generate a complete, consistent storyboard for the ENTIRE clip as an "
                 "ordered sequence of panels. The SAME character and style appear in every "
                 "panel — only pose, framing, and hands change. Every hand position and body "
                 "movement below is locked to the real music: the fretting/keying hand must "
                 "match the named chord, and motion accents fall on the listed timestamps. "
                 "Do not invent chords or drift the character.")
    lines.append("")
    lines.append("## LOCKED CHARACTER + STYLE (repeat verbatim in every panel)")
    lines.append(f"- **Character:** {args.character}")
    lines.append(f"- **Instrument:** {inst}")
    lines.append(f"- **Style:** {args.style}")
    lines.append(f"- **Palette:** {args.palette}")
    lines.append("")
    lines.append("## MOVEMENT SPINE (locked to the beat)")
    cg = sync.get("cut_grid", {})
    lines.append(f"- **Hard cuts / section changes:** {', '.join(mmss(t) for t in cg.get('section_changes', []))}")
    lines.append(f"- **Drops (release / reveal):** {', '.join(mmss(t) for t in cg.get('on_drops', [])) or '—'}")
    lines.append("- **On every beat:** micro-motion (nod / sway / strum-attack); bigger lean on builds & drops.")
    lines.append("")
    lines.append("## PANEL SEQUENCE (cover the whole piece)")
    lines.append("")
    lines.append("| # | Time | Sec | Panel | Chord | Hand placement | Movement |")
    lines.append("|---|------|-----|-------|-------|----------------|----------|")
    for i, s in enumerate(shots, 1):
        drop = " 💥DROP" if s["is_drop"] else ""
        hand = s["hand"] or "—"
        lines.append(f"| {i} | {mmss(s['start'])}–{mmss(s['end'])} | {s['section']} | "
                     f"{s['panel']}{drop} | {s['chord'] or '—'} | {hand} | {s['movement']} |")
    lines.append("")
    lines.append("## PER-PANEL PROMPT PATTERN")
    lines.append("For each row, expand into a full prompt: "
                 "`[LOCKED CHARACTER + STYLE verbatim] — [panel framing/camera] — "
                 "playing the [instrument], [HAND PLACEMENT from the row] forming the [CHORD] — "
                 "[MOVEMENT cue] — [lighting] — [palette] — [mood].` "
                 "Keep the character+style block identical every time; only the framing, chord, "
                 "hands, and movement change.")
    lines.append("")
    lines.append("## TOOLS")
    lines.append("- **Stills (keyframes):** GPT-4o / DALL·E, Gemini Imagen, or Midjourney "
                 "(use a character reference to hold consistency).")
    lines.append("- **Animate:** feed each keyframe to Sora / Veo / Kling / Runway (image-to-video) "
                 "and describe the motion — the strum/keypress, the hand reshaping on each chord "
                 "change, the body sway on the beat.")
    lines.append("")

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Master prompt with {len(shots)} panels covering the whole clip -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
