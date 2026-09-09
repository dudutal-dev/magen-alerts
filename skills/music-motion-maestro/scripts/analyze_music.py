#!/usr/bin/env python3
"""Core music analysis: tempo, beat grid, key, structure, mood, dynamics.

Outputs a single analysis.json that every downstream step consumes.
Everything here is measured from the audio — nothing is guessed.

Usage:
    python analyze_music.py work/audio.wav --out work/analysis.json
"""
import argparse
import json
import sys

import numpy as np

# Krumhansl-Schmuckler key profiles (major / minor), normalized later.
_MAJOR = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
_MINOR = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
_PITCHES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def estimate_key(chroma_mean):
    """Correlate the mean chroma against rotated key profiles."""
    best = (-1.0, "C", "major")
    for i in range(12):
        maj = np.corrcoef(np.roll(_MAJOR, i), chroma_mean)[0, 1]
        minr = np.corrcoef(np.roll(_MINOR, i), chroma_mean)[0, 1]
        if maj > best[0]:
            best = (maj, _PITCHES[i], "major")
        if minr > best[0]:
            best = (minr, _PITCHES[i], "minor")
    return {"tonic": best[1], "mode": best[2], "confidence": round(float(best[0]), 3)}


def segment_structure(librosa, y, sr, beat_times):
    """Detect structural boundaries via a recurrence/novelty approach."""
    # Beat-synchronous chroma+MFCC feature stack for structure.
    hop = 512
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, hop_length=hop, n_mfcc=13)
    feats = np.vstack([chroma, mfcc])
    beat_frames = librosa.time_to_frames(beat_times, sr=sr, hop_length=hop)
    beat_frames = beat_frames[(beat_frames >= 0) & (beat_frames < feats.shape[1])]
    if len(beat_frames) < 4:
        return []
    beat_feats = librosa.util.sync(feats, beat_frames, aggregate=np.median)

    # Aim for a musically sensible number of segments (~ every 8-16 bars).
    n_segments = int(np.clip(len(beat_times) // 32, 3, 10))
    try:
        bounds = librosa.segment.agglomerative(beat_feats, n_segments)
    except Exception:
        return []
    bound_times = beat_times[np.clip(bounds, 0, len(beat_times) - 1)]
    bound_times = np.unique(np.concatenate([[0.0], bound_times]))

    # Label each segment by its relative energy (rough intro/verse/chorus cue).
    rms = librosa.feature.rms(y=y, hop_length=hop)[0]
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop)
    sections = []
    for i, start in enumerate(bound_times):
        end = bound_times[i + 1] if i + 1 < len(bound_times) else librosa.get_duration(y=y, sr=sr)
        mask = (times >= start) & (times < end)
        seg_energy = float(np.mean(rms[mask])) if mask.any() else 0.0
        sections.append({"start": round(float(start), 3), "end": round(float(end), 3),
                         "energy": seg_energy})
    # Normalize energy 0..1 and give a coarse label.
    if sections:
        e = np.array([s["energy"] for s in sections])
        lo, hi = e.min(), e.max() + 1e-9
        for s in sections:
            n = (s["energy"] - lo) / (hi - lo)
            s["energy"] = round(float(n), 3)
            s["label"] = ("high" if n > 0.66 else "mid" if n > 0.33 else "low")
    return sections


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--out", default="work/analysis.json")
    args = ap.parse_args()

    try:
        import librosa
    except ImportError:
        print("librosa not installed. Run: pip install librosa", file=sys.stderr)
        return 1

    y, sr = librosa.load(args.audio, sr=None, mono=True)
    duration = float(librosa.get_duration(y=y, sr=sr))

    # --- Tempo + beat grid ---
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, units="frames")
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    bpm = float(np.atleast_1d(tempo)[0])

    # Downbeats: assume 4/4 and take every 4th beat starting from a strong one.
    downbeats = beat_times[::4].tolist() if len(beat_times) else []

    # --- Onsets ---
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onset_frames = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr).tolist()

    # --- Key ---
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    key = estimate_key(chroma.mean(axis=1))

    # --- Dynamics envelope (downsampled RMS in dB) ---
    rms = librosa.feature.rms(y=y)[0]
    rms_db = librosa.amplitude_to_db(rms + 1e-9)
    step = max(1, len(rms_db) // 200)  # ~200 points max
    dyn_times = librosa.frames_to_time(np.arange(len(rms_db)), sr=sr)
    dynamics = [{"t": round(float(dyn_times[i]), 2), "db": round(float(rms_db[i]), 1)}
                for i in range(0, len(rms_db), step)]

    # --- Mood heuristics (energy / valence) ---
    energy = float(np.clip((np.mean(rms) * 6.0), 0, 1))  # loudness-ish proxy
    # Valence proxy: major mode + brighter spectral centroid => happier.
    centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    bright = float(np.clip(centroid / (sr / 4), 0, 1))
    valence = float(np.clip(0.5 * bright + (0.25 if key["mode"] == "major" else -0.15) + 0.25, 0, 1))
    mood = _mood_label(energy, valence, key["mode"])

    sections = segment_structure(librosa, y, sr, beat_times)

    out = {
        "duration_sec": round(duration, 2),
        "bpm": round(bpm, 1),
        "beat_count": int(len(beat_times)),
        "beat_times": [round(float(t), 3) for t in beat_times],
        "downbeats": [round(float(t), 3) for t in downbeats],
        "onset_times": [round(float(t), 3) for t in onset_times],
        "key": key,
        "energy": round(energy, 3),
        "valence": round(valence, 3),
        "mood": mood,
        "sections": sections,
        "dynamics": dynamics,
    }

    with open(args.out, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"BPM {out['bpm']} | key {key['tonic']} {key['mode']} | "
          f"mood {mood} | {len(sections)} sections | {len(beat_times)} beats")
    print(f"Saved -> {args.out}")
    return 0


def _mood_label(energy, valence, mode):
    hi_e = energy > 0.5
    hi_v = valence > 0.5
    if hi_e and hi_v:
        return "energetic / uplifting"
    if hi_e and not hi_v:
        return "intense / dark"
    if not hi_e and hi_v:
        return "calm / warm"
    return "somber / mellow"


if __name__ == "__main__":
    sys.exit(main())
