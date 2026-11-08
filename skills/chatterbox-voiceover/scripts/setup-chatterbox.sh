#!/usr/bin/env bash
# One-time setup: creates a local Python venv with Chatterbox TTS.
# Chatterbox is archived (Aug 2026) — we pin an exact commit so installs stay reproducible.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
VENV="${CHATTERBOX_VENV:-$ROOT/.venv-chatterbox}"
COMMIT="ab55923c27757c90cfcc407baa57dc25a7d25217"
PY="${PYTHON:-python3.11}"
command -v "$PY" >/dev/null 2>&1 || PY=python3

"$PY" -c 'import sys; v=sys.version_info; sys.exit(0 if (3,10)<=v[:2]<(3,14) else 1)' || {
  echo "Chatterbox needs Python 3.10–3.13 (3.11 recommended). Set PYTHON=/path/to/python3.11" >&2; exit 1; }

if [[ ! -d "$VENV" ]]; then "$PY" -m venv "$VENV"; fi
"$VENV/bin/pip" install --upgrade pip
"$VENV/bin/pip" install "chatterbox-tts @ git+https://github.com/resemble-ai/chatterbox.git@$COMMIT"

command -v ffmpeg >/dev/null 2>&1 || echo "Note: ffmpeg not found — needed only for --mp3 output (brew install ffmpeg / apt-get install ffmpeg)."
echo "Chatterbox installed in $VENV"
echo "Try: $VENV/bin/python skills/chatterbox-voiceover/scripts/voiceover.py --text 'Hello there.' --out outputs/voiceovers/test.wav"
