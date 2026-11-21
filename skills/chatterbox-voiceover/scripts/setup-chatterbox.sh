#!/usr/bin/env bash
# One-time setup for the chatterbox-voiceover skill.
# Creates .venv-chatterbox/ at the repo root and installs Chatterbox TTS (CPU build of PyTorch
# on Linux; the default build elsewhere, which uses Apple Silicon's GPU via MPS on Macs).
#
# Usage (from the repo root):
#   ./skills/chatterbox-voiceover/scripts/setup-chatterbox.sh
#   PYTHON=python3.11 ./skills/chatterbox-voiceover/scripts/setup-chatterbox.sh
#
# Chatterbox supports Python 3.10-3.12. The model weights (~1-2 GB) download from Hugging Face
# on first use, or ahead of time with --prefetch.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
VENV="$ROOT/.venv-chatterbox"

pick_python() {
  if [[ -n "${PYTHON:-}" ]]; then echo "$PYTHON"; return; fi
  for p in python3.11 python3.12 python3.10 python3; do
    if command -v "$p" >/dev/null 2>&1; then
      if "$p" -c 'import sys; sys.exit(0 if (3,10) <= sys.version_info[:2] <= (3,12) else 1)'; then
        echo "$p"; return
      fi
    fi
  done
  echo ""
}

PY="$(pick_python)"
if [[ -z "$PY" ]]; then
  echo "Chatterbox needs Python 3.10, 3.11 or 3.12. Install one (e.g. 'brew install python@3.11') and retry." >&2
  exit 1
fi
echo "Using $PY ($("$PY" --version))"

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "Note: ffmpeg not found. It's needed to convert voiceovers to MP3 (macOS: brew install ffmpeg)." >&2
fi

if [[ ! -x "$VENV/bin/python" ]]; then
  "$PY" -m venv "$VENV"
fi
"$VENV/bin/python" -m pip install --upgrade pip >/dev/null

if [[ "$(uname -s)" == "Linux" ]] && ! command -v nvidia-smi >/dev/null 2>&1; then
  # No NVIDIA GPU: the CPU wheels are ~200 MB instead of several GB. If the PyTorch download
  # server is unreachable (e.g. a locked-down network), fall back to the regular PyPI build below.
  "$VENV/bin/pip" install --retries 1 --timeout 20 torch torchaudio --index-url https://download.pytorch.org/whl/cpu \
    || echo "PyTorch CPU index unreachable; installing the default PyPI build (larger download)." >&2
fi
"$VENV/bin/pip" install chatterbox-tts

"$VENV/bin/python" -c "import chatterbox; print('chatterbox-tts installed')"

if [[ "${1:-}" == "--prefetch" ]]; then
  "$VENV/bin/python" -c "from huggingface_hub import snapshot_download as d; d('ResembleAI/chatterbox-turbo')"
  echo "Turbo model downloaded."
fi
echo "Done. Generate a voiceover with:"
echo "  .venv-chatterbox/bin/python skills/chatterbox-voiceover/scripts/tts.py --text \"Hello\" --out output/voiceovers/hello.wav"
