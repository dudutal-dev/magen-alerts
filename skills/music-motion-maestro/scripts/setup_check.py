#!/usr/bin/env python3
"""Check that all dependencies for the music-motion-maestro pipeline are present.

Run this first when anything in the pipeline fails — it tells you exactly
what is missing and how to install it, instead of failing deep inside a
library with a cryptic traceback.
"""
import importlib
import shutil
import sys

PY_DEPS = {
    "yt_dlp": "yt-dlp        (download audio from YouTube)",
    "librosa": "librosa       (tempo/beat/key/structure analysis)",
    "numpy": "numpy         (numerics)",
    "scipy": "scipy         (signal processing)",
    "soundfile": "soundfile     (audio I/O)",
    "music21": "music21       (MIDI -> MusicXML/sheet, notation)",
    "basic_pitch": "basic-pitch   (audio -> MIDI piano transcription)",
}

SYS_BINS = {
    "ffmpeg": "ffmpeg        (required by librosa + yt-dlp for decoding)",
}


def main() -> int:
    missing_py, missing_bin = [], []

    print("=== music-motion-maestro dependency check ===\n")
    print("Python packages:")
    for mod, label in PY_DEPS.items():
        try:
            importlib.import_module(mod)
            print(f"  [ok]      {label}")
        except Exception:
            print(f"  [MISSING] {label}")
            missing_py.append(mod.replace("_", "-"))

    print("\nSystem binaries:")
    for binary, label in SYS_BINS.items():
        if shutil.which(binary):
            print(f"  [ok]      {label}")
        else:
            print(f"  [MISSING] {label}")
            missing_bin.append(binary)

    print()
    if not missing_py and not missing_bin:
        print("All dependencies present. You are good to go. ✅")
        return 0

    print("Some dependencies are missing. Install them:\n")
    if missing_py:
        # basic-pitch pulls a heavy TF/onnx backend; keep it explicit.
        print("  pip install " + " ".join(sorted(set(missing_py))))
    if missing_bin:
        print("  # ffmpeg (choose your platform):")
        print("  apt-get install -y ffmpeg      # Debian/Ubuntu")
        print("  brew install ffmpeg            # macOS")
    print("\nThen re-run this script to confirm.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
