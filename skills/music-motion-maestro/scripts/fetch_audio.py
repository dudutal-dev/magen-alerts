#!/usr/bin/env python3
"""Fetch audio from a YouTube URL (or search string) into a clean WAV.

Why this bypasses ads: yt-dlp downloads the video's own audio stream
straight from the CDN. YouTube ads are injected by the player at watch
time and are NOT part of the content stream, so they simply never exist
in the downloaded file. There is nothing to "block" — the ad was never
in the bytes we pull.

Usage:
    python fetch_audio.py "https://www.youtube.com/watch?v=..." --out work/
    python fetch_audio.py "daft punk get lucky" --out work/   # search
"""
import argparse
import json
import os
import subprocess
import sys


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("query", help="YouTube URL or search string")
    ap.add_argument("--out", default="work", help="output directory")
    ap.add_argument("--sr", type=int, default=44100, help="sample rate")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)

    try:
        import yt_dlp  # noqa: F401
    except ImportError:
        print("yt-dlp not installed. Run: pip install yt-dlp", file=sys.stderr)
        return 1

    # A bare search string -> take the first result deterministically.
    target = args.query
    if not target.strip().lower().startswith(("http://", "https://", "ytsearch")):
        target = f"ytsearch1:{args.query}"

    wav_path = os.path.join(args.out, "audio.wav")
    tmpl = os.path.join(args.out, "audio.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": tmpl,
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "wav"},
        ],
        # Downsample/monoize at the ffmpeg step for consistent analysis.
        "postprocessor_args": ["-ac", "1", "-ar", str(args.sr)],
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }

    import yt_dlp

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(target, download=True)
        if "entries" in info:  # search result wrapper
            info = info["entries"][0]

    meta = {
        "title": info.get("title"),
        "channel": info.get("channel") or info.get("uploader"),
        "duration_sec": info.get("duration"),
        "webpage_url": info.get("webpage_url"),
        "audio_path": wav_path,
        "sample_rate": args.sr,
    }
    with open(os.path.join(args.out, "source.json"), "w") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    if not os.path.exists(wav_path):
        print("Download completed but audio.wav not found — check ffmpeg.", file=sys.stderr)
        return 1

    print(json.dumps(meta, ensure_ascii=False, indent=2))
    print(f"\nSaved audio -> {wav_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
