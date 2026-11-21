#!/usr/bin/env python3
"""Generate a voiceover locally with Chatterbox TTS (free, no Arcads credits).

Run with the skill's virtualenv (created by setup-chatterbox.sh):

    .venv-chatterbox/bin/python skills/chatterbox-voiceover/scripts/tts.py \
        --text "I tried this for two weeks and honestly? [chuckle] I'm obsessed." \
        --voice references/voices/sofia.wav \
        --out output/voiceovers/sofia-hook.wav --mp3

Options:
  --text / --text-file   What to say. Turbo understands tags like [laugh], [chuckle], [sigh].
  --voice                Optional 5-15 s clean WAV/MP3 of the target voice (zero-shot cloning).
                         Only use voices you own or have permission to clone.
  --model                turbo (default, fast, English) | standard (more expressive controls)
                         | multilingual (pass --language, e.g. es, fr, de)
  --exaggeration, --cfg  Emotion intensity / pacing (standard + multilingual only).
  --mp3                  Also write an .mp3 next to the .wav (needs ffmpeg). Arcads accepts both.
  --seed                 Fix the random seed for repeatable takes.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def pick_device() -> str:
    import torch

    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def load_model(kind: str, device: str):
    if kind == "turbo":
        from chatterbox.tts_turbo import ChatterboxTurboTTS

        return ChatterboxTurboTTS.from_pretrained(device=device)
    if kind == "multilingual":
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS

        return ChatterboxMultilingualTTS.from_pretrained(device=device)
    from chatterbox.tts import ChatterboxTTS

    return ChatterboxTTS.from_pretrained(device=device)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--text")
    src.add_argument("--text-file", type=Path)
    ap.add_argument("--voice", type=Path, help="reference clip of the target voice (optional)")
    ap.add_argument("--out", type=Path, required=True, help="output .wav path")
    ap.add_argument("--model", choices=["turbo", "standard", "multilingual"], default="turbo")
    ap.add_argument("--language", default="en", help="language code for --model multilingual")
    ap.add_argument("--exaggeration", type=float, default=0.5)
    ap.add_argument("--cfg", type=float, default=0.5)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--mp3", action="store_true", help="also write an .mp3 (needs ffmpeg)")
    ap.add_argument("--device", help="cpu | cuda | mps (auto-detected by default)")
    args = ap.parse_args()

    text = args.text if args.text is not None else args.text_file.read_text(encoding="utf-8")
    text = " ".join(text.split())
    if not text:
        ap.error("text is empty")
    if args.voice and not args.voice.is_file():
        ap.error(f"voice reference not found: {args.voice}")

    import torch
    import torchaudio as ta

    if args.seed is not None:
        torch.manual_seed(args.seed)
    device = args.device or pick_device()
    print(f"Loading Chatterbox {args.model} on {device} (first run downloads the model)...", file=sys.stderr)
    model = load_model(args.model, device)

    kwargs = {}
    if args.voice:
        kwargs["audio_prompt_path"] = str(args.voice)
    if args.model in ("standard", "multilingual"):
        kwargs.update(exaggeration=args.exaggeration, cfg_weight=args.cfg)
    if args.model == "multilingual":
        kwargs["language_id"] = args.language

    wav = model.generate(text, **kwargs)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    ta.save(str(args.out), wav, model.sr)
    seconds = wav.shape[-1] / model.sr
    print(f"Wrote {args.out} ({seconds:.1f}s)")

    if args.mp3:
        if not shutil.which("ffmpeg"):
            print("ffmpeg not found; skipped MP3 conversion", file=sys.stderr)
        else:
            mp3 = args.out.with_suffix(".mp3")
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error", "-i", str(args.out), "-codec:a", "libmp3lame", "-q:a", "2", str(mp3)],
                check=True,
            )
            print(f"Wrote {mp3}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
