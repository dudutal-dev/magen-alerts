#!/usr/bin/env python3
"""Transcribe audio to a piano/lead MIDI and derive notation artifacts.

Uses Spotify's basic-pitch (a solid, pip-installable neural transcriber)
to produce a MIDI file, then music21 to derive:
  - notes.mid       (raw transcription)
  - transcription.musicxml   (openable in MuseScore / Finale / Sibelius)
  - notes.json      (machine-readable note list: pitch, start, dur, vel)
  - lead_sheet.txt  (human-readable melody summary)

Transcription is estimation, not ground truth. Clean solo piano / clear
melodies transcribe very well; dense full-band mixes are noisier — say so
to the user rather than overselling accuracy.

Usage:
    python transcribe_piano.py work/audio.wav --out work/piano
"""
import argparse
import json
import os
import sys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--out", default="work/piano", help="output directory")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    try:
        from basic_pitch.inference import predict_and_save
        from basic_pitch import ICASSP_2022_MODEL_PATH
    except ImportError:
        print("basic-pitch not installed. Run: pip install basic-pitch", file=sys.stderr)
        return 1

    # basic-pitch writes <stem>_basic_pitch.mid into the output dir.
    predict_and_save(
        [args.audio], args.out,
        save_midi=True, sonify_midi=False, save_model_outputs=False, save_notes=False,
        model_or_model_path=ICASSP_2022_MODEL_PATH,
    )

    # Locate the produced MIDI and normalize its name to notes.mid. Ignore a
    # notes.mid left by an earlier run, or a second run would re-parse it.
    produced = None
    newest = -1.0
    for fn in os.listdir(args.out):
        if fn == "notes.mid" or not fn.endswith((".mid", ".midi")):
            continue
        path = os.path.join(args.out, fn)
        mtime = os.path.getmtime(path)
        if mtime > newest:
            newest, produced = mtime, path
    if not produced:
        print("basic-pitch did not produce a MIDI file.", file=sys.stderr)
        return 1
    mid_path = os.path.join(args.out, "notes.mid")
    if produced != mid_path:
        os.replace(produced, mid_path)

    # Derive notation + note list with music21.
    try:
        from music21 import converter
    except ImportError:
        print(f"MIDI saved -> {mid_path} (install music21 for MusicXML/notation).")
        return 0

    score = converter.parse(mid_path)
    xml_path = os.path.join(args.out, "transcription.musicxml")
    score.write("musicxml", fp=xml_path)

    notes = []
    # flatten first: an offset taken from recurse() is relative to its measure,
    # so start times restarted every bar and sorting scrambled the order.
    for n in score.flatten().notes:
        pitches = [p.nameWithOctave for p in n.pitches] if n.isChord else [n.pitch.nameWithOctave]
        notes.append({
            "pitches": pitches,
            "start": round(float(n.offset), 3),
            "dur": round(float(n.quarterLength), 3),
        })
    notes.sort(key=lambda x: x["start"])
    with open(os.path.join(args.out, "notes.json"), "w") as f:
        json.dump({"notes": notes, "count": len(notes)}, f, ensure_ascii=False, indent=2)

    # A compact human-readable melody line (top note per event).
    lead = " ".join(n["pitches"][-1] for n in notes[:400])
    with open(os.path.join(args.out, "lead_sheet.txt"), "w") as f:
        f.write(lead + ("\n" if lead else ""))

    print(f"Transcribed {len(notes)} note events.")
    print(f"  MIDI      -> {mid_path}")
    print(f"  MusicXML  -> {xml_path}   (open in MuseScore for engraved sheet music)")
    print(f"  notes.json/ lead_sheet.txt in {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
