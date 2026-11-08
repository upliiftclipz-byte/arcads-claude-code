---
name: chatterbox-voiceover
description: >-
  Generate ad voiceovers locally and for free with Chatterbox TTS (open-source, MIT, by Resemble AI). Covers English Turbo/Nano reads with paralinguistic tags ([laugh], [sigh]), expressive reads with exaggeration/CFG control, zero-shot voice cloning from a 10s clip (with consent), and 23-language localization via Multilingual V3. Can time a voiceover to an existing video's captions, add an original synthesized music bed ducked under the voice, and normalize loudness for social. Output WAV/MP3 can be uploaded to Arcads as Seedance 2.0 referenceAudios or used in audio-driven / edit workflows. Use when the user asks for a voiceover, VO, narration, TTS, a cloned voice, a localized read of an ad script, background music for a video, or audio for a video ad.
---

# Chatterbox Voiceover

Local text-to-speech for ad scripts using [resemble-ai/chatterbox](https://github.com/resemble-ai/chatterbox). Runs on the user's machine and costs no Arcads credits.

> **Status:** Resemble AI retired Chatterbox in August 2026. The repo is an MIT-licensed archive with no updates or support. Setup pins an exact commit (`ab55923`) so installs stay reproducible. Weights download from Hugging Face (`ResembleAI/*`) on the first run.

## When to use this skill

- "Write and voice a 20s VO for this ad"
- "Clone my voice from this clip and read the script"
- "Give me 3 takes of the hook"
- "Localize this ad script into Spanish / French / German"
- "I need an audio track to drive / reference in Seedance"

If the user wants Arcads' built-in actors and voices (talking avatar), use `arcads-external-api` → `POST /v1/scripts` instead. Use this skill for a standalone audio file.

## Read order

1. **This file**: setup, model choice, workflow
2. **[prompting/guide.md](prompting/guide.md)**: writing for TTS, tags, tuning recipes, troubleshooting
3. **[scripts/voiceover.py](scripts/voiceover.py)**: the CLI (`--help` lists every flag)
4. **[scripts/voiceover-to-video.sh](scripts/voiceover-to-video.sh)** and **[scripts/make-music.py](scripts/make-music.py)**: put a timed voiceover (and optional music) onto an existing video

## Setup (one time)

```bash
./skills/chatterbox-voiceover/scripts/setup-chatterbox.sh
```

- Needs **Python 3.10–3.13** (3.11 recommended). Set `PYTHON=/path/to/python3.11` if your default python is a different version.
- Creates `.venv-chatterbox/` at the repo root. It is gitignored.
- PyTorch is ~2 GB and model weights are 0.5–2 GB, so the first run is slow.
- `ffmpeg` is only needed for `--mp3`.
- Optional: set `HF_TOKEN` if Hugging Face rate-limits anonymous downloads.
- **Claude Code cloud sessions:** the network must allow `huggingface.co`, `us.aws.cdn.hf.co` and `cas-server.xethub.hf.co` (model files redirect to the last two). Without them, setup succeeds but the first render fails with `ProxyError: 403`. `download.pytorch.org` may also be blocked; the setup script installs PyTorch from PyPI, which works.
- Speed on a cloud CPU (measured): Turbo about 6 s per line, original about 10 s per line, plus about 5 s to load the model for each line.

Always run the CLI with the venv's python:

```bash
.venv-chatterbox/bin/python skills/chatterbox-voiceover/scripts/voiceover.py --help
```

## Model choice

| `--model` | Size | Languages | Controls | Pick when |
|---|---|---|---|---|
| `turbo` (default) | 350M | English | Paralinguistic tags `[laugh]` `[chuckle]` `[sigh]` `[gasp]` `[cough]` `[clear throat]` `[sniff]` `[groan]` `[shush]` | Most English UGC/ad VO. Fast, natural, conversational |
| `nano` | 110M | English | Same tags as Turbo | CPU-only machines or quick drafts (~3x realtime on 8 CPU cores) |
| `original` | 500M | English | `--exaggeration`, `--cfg` | Hype or dramatic reads where you need to dial emotion |
| `multilingual` | 500M (V3) | 23 languages via `--lang` | `--exaggeration`, `--cfg` | Localizing an ad into another language |

Turbo and Nano ignore `--exaggeration`/`--cfg`. The original and multilingual models do not understand the bracket tags. Remove the tags for those models or they get read aloud.

Multilingual languages: ar da de el en es fi fr he hi it ja ko ms nl no pl pt ru sv sw tr zh.

Hardware: CUDA is fastest. Apple Silicon uses `mps`. CPU works but is slow for anything except `nano`. The script picks a device automatically. Override it with `--device`.

## Voice cloning: consent rule

`--voice` clones whoever is speaking in the reference clip. **Only clone a voice when the user owns it or has the speaker's explicit permission.** Do not clone celebrities, public figures, competitors' spokespeople, or voices taken from someone else's ads, even if the user asks. Put a consented `--voice` clip in `references/voices/<name>.wav` (gitignored, like other references).

Every Chatterbox output carries an imperceptible **PerTh watermark** that survives MP3 compression and editing. Tell the user this if they plan to run paid ads with the audio.

Good reference clips:
- 10–20 s, one speaker, no music or background noise, no reverb. Must be longer than 5 s or the model refuses it.
- Same language as the output, or the accent carries over. For cross-language cloning, set `--cfg 0` to reduce that.
- Delivery matches the target. A calm clip gives a calm clone.

## Workflow

### 1. Gather requirements

Ask only for what's missing:
1. **Script**, or the brief to write one from. Pull brand voice from `MASTER_CONTEXT.md`.
2. **Length target.** Most UGC ads run 15–30 s. Budget about 2.5 words per second, so a 15 s ad is about 35–40 words.
3. **Voice**: built-in default, or a consented reference clip on disk. A clip pasted into chat is not on disk; ask the user to save the file.
4. **Language(s)** and **tone** (casual UGC, hype, calm/premium, testimonial).
5. **Number of takes.** Default to 3 for a hook and 1 for the full read.

### 2. Write the script for TTS

Follow [prompting/guide.md](prompting/guide.md): short sentences, numbers and brand names spelled the way they're said, one paragraph per beat (hook / problem / product / CTA). Show the script to the user and get approval before rendering.

### 3. Render

Save the approved script to `outputs/voiceovers/<YYYY-MM-DD>/<slug>.txt`, then:

```bash
.venv-chatterbox/bin/python skills/chatterbox-voiceover/scripts/voiceover.py \
  --script outputs/voiceovers/2026-11-07/cola-hook.txt \
  --voice references/voices/sofia.wav \
  --model turbo --takes 3 --seed 7 --mp3 \
  --out outputs/voiceovers/2026-11-07/cola-hook.wav
```

The script generates each paragraph separately, joins them with `--pause-ms` of silence, writes `-takeN.wav` files plus a `.json` sidecar (model, settings, durations), and prints the JSON on stdout.

### 4. Review

- Report each take's duration against the target length. If a take runs long, trim the script. Don't speed up the audio.
- Ask the user to listen and pick a take. You can't judge audio quality yourself; say so rather than claiming a take "sounds great".
- Fix specific problems with the recipes in the guide (mispronunciations, rushed pacing, flat delivery).

### 5. Voiceover onto an existing video (optional)

Use this when the user already has a cut video (for example a motion-graphics reel with captions) and wants narration timed to it.

1. Write a `beats.tsv` with one line per caption or beat. Columns are separated by tabs: `start_s  end_s  name  spoken line`. Lines starting with `#` are comments. Take the start and end times from the video's script or captions, and write the spoken line the way it should be said ("thirty dollars a month", not "$30/month").
   ```
   # start	end	name	line
   0.2	4.0	hook	Never miss a renewal again.
   4.0	7.6	promise	Every policy. Every document. Every renewal date.
   ```
2. Optional music: `.venv-chatterbox/bin/python skills/chatterbox-voiceover/scripts/make-music.py outputs/.../bed.wav --seconds <video length> --mood warm|bright|calm`. It synthesizes an original bed from scratch (soft pad, plucked arpeggio, light drums), so there's no licensing to check. Use `warm` (100 BPM) for trust and finance, `bright` (118 BPM) for energetic consumer products, and `calm` (84 BPM, no kick) for premium or ASMR. Don't download music from the web unless the user supplies a track they have rights to.
3. Render and mux:
   ```bash
   skills/chatterbox-voiceover/scripts/voiceover-to-video.sh \
     --video in.mp4 --beats beats.tsv --out outputs/voiceovers/<date>/<slug>/out.mp4 \
     --model original --exaggeration 0.6 --cfg 0.4 --seed 7 \
     --music outputs/voiceovers/<date>/<slug>/bed.wav --music-db -14 --lufs -14
   ```
   - Each line is placed at its start time. The script prints each line's length against its window and flags overruns with `WARN`.
   - Lines are cached in `<out>-beats/`. To re-roll one line, delete its `.wav` and rerun with another `--seed`. `--rerender` redoes all of them.
   - The music ducks under the voice through a sidechain compressor. The final mix is normalized to `--lufs` (−14 suits Instagram, TikTok and YouTube Shorts). Expect about −15 LUFS measured, because loudnorm runs in a single pass. The original video audio is replaced, not mixed.
4. Report each line's fit and the measured loudness. Send the video and ask the user to listen. You can't judge how it sounds.

Measured on a 24 s, 7-line reel: Turbo's default read ran 0.4 s over on one 3.6 s window. The original model at exaggeration 0.6 / cfg 0.4 reads faster and punchier, and every line fit with 0.2–2 s to spare. For tight caption timing, try the expressive original model before shortening lines.

### 6. Hand off to Arcads (optional)

Upload the chosen take with the presigned-URL flow in `arcads-external-api/reference.md` (`POST /v1/file-upload/get-presigned-url`, `fileType: "audio/wav"` or `"audio/mpeg"`), then:

- **Seedance 2.0**: pass the returned `filePath` in `referenceAudios` (max 3). It can be combined with `referenceImages` or `referenceVideos`. Follow the Seedance audio confirmation gate in the Arcads skill.
- **Audio-driven** (`POST /v1/audio-driven`): this repo has not verified the request fields. Check the live API schema before calling it, and log the result in `MASTER_CONTEXT.md` once it works.

Log the Arcads call in `logs/arcads-api.jsonl` as usual. Local Chatterbox renders cost no credits and are not logged there.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Audio prompt must be longer than 5 seconds!` | Use a longer reference clip (10 s+) |
| Tags like `[laugh]` read aloud | You're on `original`/`multilingual`. Switch to `turbo`/`nano` or remove the tags |
| Rambling, repeated words, or extra speech at the end | Split long paragraphs. Keep each under about 40 words. Try a different `--seed` |
| Rushed delivery (original/multilingual) | Lower `--cfg` to about 0.3 |
| Wrong accent in localized read | Use a reference clip in the target language, or `--cfg 0` |
| Hugging Face download fails or 429 | Set `HF_TOKEN`. The library already falls back from Xet to HTTP |
| `httpx.ProxyError: 403 Forbidden` in a cloud session | The network blocks Hugging Face. Allow `huggingface.co`, `us.aws.cdn.hf.co` and `cas-server.xethub.hf.co` (see Setup) |
| Download hangs at a few MB | `cas-server.xethub.hf.co` is blocked, so the Xet transfer stalls without an error. Allow it, or set `HF_HUB_DISABLE_XET=1` (then `us.aws.cdn.hf.co` must be allowed) |
| A line overruns its window in `voiceover-to-video.sh` | Re-roll that line with a new `--seed`, switch to `--model original --exaggeration 0.6 --cfg 0.4`, or shorten the line |
| Final video too quiet or loud | Adjust `--lufs` (default −14). Adjust music against voice with `--music-db` (default −14; lower is quieter) |
| `numpy` / `torch` install errors | Python version outside 3.10–3.13. Use 3.11 |
