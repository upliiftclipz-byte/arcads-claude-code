#!/usr/bin/env bash
# Voice a timed script with Chatterbox and lay it onto a video, optionally over ducked background music.
#
# Usage (from the repo root):
#   skills/chatterbox-voiceover/scripts/voiceover-to-video.sh --video in.mp4 --beats beats.tsv --out out.mp4 \
#     [--model turbo|nano|original|multilingual] [--seed 7] [--voice ref.wav] [--lang es] \
#     [--exaggeration 0.6 --cfg 0.4] [--music bed.wav] [--music-db -14] [--lufs -14] [--rerender]
#
# beats.tsv: one line per beat, tab-separated: start_s <TAB> end_s <TAB> name <TAB> spoken line
# (lines starting with # are comments). Each line is rendered once and cached in <out>-beats/<name>.wav;
# delete one file (or pass --rerender) to re-roll it. Lines longer than their window print a WARN.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
PY="${CHATTERBOX_PY:-$ROOT/.venv-chatterbox/bin/python}"
VO="$ROOT/skills/chatterbox-voiceover/scripts/voiceover.py"

VIDEO=""; BEATS=""; OUT=""; MODEL="turbo"; SEED="7"; MUSIC=""; MUSIC_DB="-14"; LUFS="-14"; RERENDER=0
VO_ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --video) VIDEO="$2"; shift 2;;
    --beats) BEATS="$2"; shift 2;;
    --out) OUT="$2"; shift 2;;
    --model) MODEL="$2"; shift 2;;
    --seed) SEED="$2"; shift 2;;
    --music) MUSIC="$2"; shift 2;;
    --music-db) MUSIC_DB="$2"; shift 2;;
    --lufs) LUFS="$2"; shift 2;;
    --rerender) RERENDER=1; shift;;
    --voice|--lang|--exaggeration|--cfg|--temperature|--device) VO_ARGS+=("$1" "$2"); shift 2;;
    -h|--help) sed -n '2,12p' "$0"; exit 0;;
    *) echo "Unknown option: $1" >&2; exit 2;;
  esac
done
[[ -f "$VIDEO" && -f "$BEATS" && -n "$OUT" ]] || { echo "Need --video, --beats and --out (see --help)" >&2; exit 2; }
[[ -z "$MUSIC" || -f "$MUSIC" ]] || { echo "--music file not found: $MUSIC" >&2; exit 2; }
[[ -x "$PY" ]] || { echo "Chatterbox not installed. Run skills/chatterbox-voiceover/scripts/setup-chatterbox.sh" >&2; exit 1; }
command -v ffmpeg >/dev/null || { echo "ffmpeg is required" >&2; exit 1; }

DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VIDEO")
CACHE="${OUT%.*}-beats"; mkdir -p "$CACHE" "$(dirname "$OUT")"
[[ $RERENDER -eq 1 ]] && rm -f "$CACHE"/*.wav "$CACHE"/*.json

inputs=(); filters=""; labels=""; n=0; warn=0
while IFS=$'\t' read -r start end beat line; do
  [[ -z "${start// }" || "$start" == \#* ]] && continue
  wav="$CACHE/$beat.wav"
  [[ -f "$wav" ]] || "$PY" "$VO" --model "$MODEL" --seed "$SEED" "${VO_ARGS[@]}" --text "$line" --out "$wav" >/dev/null
  len=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$wav")
  win=$(awk -v a="$start" -v b="$end" 'BEGIN{print b-a}')
  flag="ok"
  if awk -v l="$len" -v w="$win" 'BEGIN{exit !(l>w)}'; then flag="WARN: over by $(awk -v l="$len" -v w="$win" 'BEGIN{printf "%.2f", l-w}')s"; warn=1; fi
  printf "%-12s %5.2fs / %4.1fs  %-22s %s\n" "$beat" "$len" "$win" "$flag" "$line"
  n=$((n+1)); inputs+=(-i "$wav")
  ms=$(awk -v s="$start" 'BEGIN{printf "%d", s*1000}')
  filters+="[$n:a]aresample=48000,adelay=${ms}|${ms}[a$n];"; labels+="[a$n]"
done < "$BEATS"
[[ $n -gt 0 ]] || { echo "No beats found in $BEATS" >&2; exit 2; }

filters+="${labels}amix=inputs=$n:normalize=0,apad,atrim=0:$DUR"
if [[ -n "$MUSIC" ]]; then
  m=$((n+1)); inputs+=(-i "$MUSIC")
  # One copy of the voice keys a sidechain compressor that ducks the music while someone speaks.
  filters+=",asplit=2[vo][key];"
  filters+="[$m:a]aresample=48000,aloop=-1:size=2e9,atrim=0:$DUR,volume=${MUSIC_DB}dB[mus];"
  filters+="[mus][key]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=400[duck];"
  filters+="[vo][duck]amix=inputs=2:normalize=0"
fi
filters+=",loudnorm=I=$LUFS:TP=-1.5:LRA=11[mix]"

ffmpeg -y -loglevel error -i "$VIDEO" "${inputs[@]}" -filter_complex "$filters" \
  -map 0:v -map "[mix]" -c:v copy -c:a aac -b:a 192k -ar 48000 -shortest "$OUT"
I=$(ffmpeg -hide_banner -i "$OUT" -vn -af ebur128 -f null - 2>&1 | awk '/ I:/{v=$2} END{print v}')
echo "Wrote $OUT (${DUR}s, ${I} LUFS)"
[[ $warn -eq 1 ]] && echo "Some lines overrun their window: shorten them, or delete their wav in $CACHE and rerun with another --seed."
exit 0
