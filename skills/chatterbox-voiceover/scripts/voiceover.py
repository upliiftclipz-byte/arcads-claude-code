#!/usr/bin/env python3
"""Generate an ad voiceover locally with Chatterbox TTS (resemble-ai/chatterbox).

Examples
  # Quick English read with the built-in Turbo voice
  voiceover.py --text "This changed my mornings. Seriously." --out outputs/voiceovers/hook.wav

  # Clone a voice (you must have the speaker's consent) from a clean 10s+ clip, 3 takes
  voiceover.py --script script.txt --voice references/voices/sofia.wav --takes 3 --out outputs/voiceovers/sofia.wav

  # Expressive read with the original model (supports exaggeration / cfg)
  voiceover.py --model original --exaggeration 0.7 --cfg 0.3 --text "..." --out vo.wav

  # Localize into Spanish with Multilingual V3
  voiceover.py --model multilingual --lang es --voice ref.wav --text "..." --out vo-es.wav

Script files: each paragraph (blank-line separated) is generated separately, then joined
with --pause-ms of silence. That keeps long scripts stable; Chatterbox drifts on long inputs.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

MODELS = ("turbo", "nano", "original", "multilingual")
# Turbo/Nano ignore exaggeration, cfg_weight and min_p (they warn if you pass them).
TUNABLE = ("original", "multilingual")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--text", help="Text to speak")
    src.add_argument("--script", type=Path, help="Text file; paragraphs are generated separately")
    p.add_argument("--out", type=Path, required=True, help="Output .wav path (take numbers are appended when --takes > 1)")
    p.add_argument("--model", choices=MODELS, default="turbo")
    p.add_argument("--voice", type=Path, help="Reference clip for voice cloning (.wav/.mp3, >5s, 10s+ recommended)")
    p.add_argument("--lang", default="en", help="Language id for --model multilingual (e.g. es, fr, de, pt, ja)")
    p.add_argument("--exaggeration", type=float, default=0.5, help="Emotion intensity, original/multilingual only (0.25-2.0)")
    p.add_argument("--cfg", type=float, default=0.5, help="cfg_weight, original/multilingual only. Lower = slower, more deliberate")
    p.add_argument("--temperature", type=float, default=0.8)
    p.add_argument("--seed", type=int, help="Base seed; take N uses seed+N-1")
    p.add_argument("--takes", type=int, default=1, help="Number of variations to render")
    p.add_argument("--pause-ms", type=int, default=350, help="Silence between paragraphs")
    p.add_argument("--mp3", action="store_true", help="Also write an .mp3 next to each .wav (needs ffmpeg)")
    p.add_argument("--device", choices=("auto", "cuda", "mps", "cpu"), default="auto")
    return p.parse_args()


def pick_device(torch, wanted: str) -> str:
    if wanted != "auto":
        return wanted
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def load_model(name: str, device: str, lang: str):
    if name in ("turbo", "nano"):
        from chatterbox.tts_turbo import ChatterboxTurboTTS
        return ChatterboxTurboTTS.from_pretrained(device=device, nano=(name == "nano"))
    if name == "original":
        from chatterbox.tts import ChatterboxTTS
        return ChatterboxTTS.from_pretrained(device=device)
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS, SUPPORTED_LANGUAGES
    if lang.lower() not in SUPPORTED_LANGUAGES:
        sys.exit(f"Unsupported --lang {lang!r}. Supported: {', '.join(SUPPORTED_LANGUAGES)}")
    return ChatterboxMultilingualTTS.from_pretrained(device=device, t3_model="v3")


def chunks_from(args) -> list[str]:
    raw = args.text if args.text is not None else args.script.read_text(encoding="utf-8")
    parts = [" ".join(block.split()) for block in raw.split("\n\n")]
    parts = [p for p in parts if p]
    if not parts:
        sys.exit("No text to speak.")
    return parts


def main() -> None:
    args = parse_args()
    if args.voice and not args.voice.is_file():
        sys.exit(f"--voice file not found: {args.voice}")
    if args.model == "multilingual" and args.lang.lower() == "en":
        print("Note: --model multilingual with --lang en; 'turbo' is usually better for English.", file=sys.stderr)

    try:
        import torch
        import torchaudio as ta
    except ImportError:
        sys.exit("Chatterbox is not installed. Run ./skills/chatterbox-voiceover/scripts/setup-chatterbox.sh "
                 "and call this script with .venv-chatterbox/bin/python")

    device = pick_device(torch, args.device)
    chunks = chunks_from(args)
    print(f"Loading {args.model} on {device} (first run downloads weights from Hugging Face)...", file=sys.stderr)
    model = load_model(args.model, device, args.lang)
    if args.voice:
        # Condition once; every chunk and take then reuses the same voice.
        kw = {"exaggeration": args.exaggeration} if args.model in TUNABLE else {}
        model.prepare_conditionals(str(args.voice), **kw)

    gen_kw: dict = {"temperature": args.temperature}
    if args.model in TUNABLE:
        gen_kw.update(exaggeration=args.exaggeration, cfg_weight=args.cfg)
    if args.model == "multilingual":
        gen_kw["language_id"] = args.lang.lower()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    silence = torch.zeros(1, int(model.sr * args.pause_ms / 1000))
    written = []
    for take in range(1, args.takes + 1):
        if args.seed is not None:
            torch.manual_seed(args.seed + take - 1)
        t0 = time.time()
        pieces = []
        for i, text in enumerate(chunks):
            wav = model.generate(text, **gen_kw).detach().cpu()
            if wav.dim() == 1:
                wav = wav.unsqueeze(0)
            pieces.append(wav)
            if i < len(chunks) - 1:
                pieces.append(silence)
        audio = torch.cat(pieces, dim=1)
        out = args.out if args.takes == 1 else args.out.with_name(f"{args.out.stem}-take{take}{args.out.suffix or '.wav'}")
        out = out.with_suffix(".wav")
        ta.save(str(out), audio, model.sr)
        seconds = audio.shape[1] / model.sr
        print(f"Wrote {out} ({seconds:.1f}s audio, {time.time() - t0:.1f}s to render)", file=sys.stderr)
        if args.mp3:
            if shutil.which("ffmpeg"):
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(out), "-b:a", "192k",
                                str(out.with_suffix(".mp3"))], check=True)
            else:
                print("ffmpeg not found; skipped mp3", file=sys.stderr)
        written.append({"file": str(out), "seconds": round(seconds, 2), "take": take})

    meta = {
        "model": args.model, "device": device, "voice": str(args.voice) if args.voice else None,
        "lang": args.lang if args.model == "multilingual" else "en",
        "exaggeration": args.exaggeration if args.model in TUNABLE else None,
        "cfg": args.cfg if args.model in TUNABLE else None,
        "temperature": args.temperature, "seed": args.seed, "chunks": len(chunks), "outputs": written,
    }
    args.out.with_suffix(".json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
