---
name: chatterbox-voiceover
description: >
  Free local voiceovers with Chatterbox TTS (open source, runs on your machine, no Arcads credits).
  Use when someone wants a voiceover, narration, text-to-speech, a voice track for an ad, a voiceover
  in a specific (owned) voice from a short sample, or audio to lip-sync with an Arcads talking actor
  (talking-actor skill, path B) or to pass to Seedance 2.0 as referenceAudios.
---

# Chatterbox voiceover (local, free)

[Chatterbox](https://github.com/resemble-ai/chatterbox) (Resemble AI, MIT licence) generates natural
speech locally. It is free per take, so iterate on wording and delivery here, then spend Arcads
credits only on the lip-synced video.

Outputs carry Resemble AI's built-in Perth watermark (inaudible); leave it in place.

## Setup (once)

```bash
./skills/chatterbox-voiceover/scripts/setup-chatterbox.sh            # creates .venv-chatterbox/
./skills/chatterbox-voiceover/scripts/setup-chatterbox.sh --prefetch # also downloads the Turbo model now
```

Needs Python 3.10-3.12 and ffmpeg (for MP3). Runs on CPU, Apple Silicon (MPS) or an NVIDIA GPU.
The first generation downloads the model (~1-2 GB) from Hugging Face. On CPU, expect roughly a few
seconds of compute per second of speech; GPU/MPS is much faster.

## Generate

```bash
.venv-chatterbox/bin/python skills/chatterbox-voiceover/scripts/tts.py \
    --text "Okay, I need to talk about this. [chuckle] I've used it every day for two weeks." \
    --out outputs/voiceovers/2026-11-21/hook.wav --mp3
```

| Option | Use |
|---|---|
| `--text` / `--text-file` | What to say |
| `--voice clip.wav` | 5-15 s of clean speech to copy a voice (zero-shot). **Owned or permitted voices only** |
| `--model turbo` *(default)* | Fast, English, supports tags like `[laugh]`, `[chuckle]`, `[sigh]`, `[gasp]`, `[cough]` |
| `--model standard` | Adds `--exaggeration` (0.25 calm … 0.5 default … 0.8+ dramatic) and `--cfg` (lower = slower, more deliberate) |
| `--model multilingual --language es` | 23 languages (es, fr, de, it, pt, ja, ko, zh, hi, ar, …) |
| `--seed 42` | Repeatable takes, e.g. when only tweaking wording |
| `--mp3` | Also write an MP3; Arcads accepts WAV and MP3 |

## Workflow

1. **Script:** apply the main skill's dialogue confirmation gate (numbered beats, word count, `yes`).
   About 2.5 words per second.
2. **Voice:** default Chatterbox voice, or `--voice` with a sample. Before using a sample, confirm the
   user owns the voice or has the speaker's permission. Never imitate a real person without consent.
   Keep samples in `references/voices/` (gitignored: voice samples are personal data).
3. **Takes:** generate 2-3 takes (different `--seed`, or tweak punctuation or tags), play them, and
   let the user pick. Delivery tips: commas and full stops control pauses; `...` trails off; a single
   tag per sentence reads naturally, more sounds forced.
4. **Use it:**
   - **Lip-sync with an Arcads actor:** `arcads_voice.py talk --audio <file>.mp3 --model audio_driven ...` (see `skills/arcads-external-api/prompting/talking-actor/SKILL.md`).
   - **Seedance 2.0:** upload and pass it in `referenceAudios` with `audioEnabled: true`.
   - **Narration over B-roll:** mix with ffmpeg, e.g.
     `ffmpeg -i broll.mp4 -i vo.mp3 -map 0:v -map 1:a -c:v copy -shortest out.mp4`
5. Save under `outputs/voiceovers/<YYYY-MM-DD>/` and open the folder for the user.

## Troubleshooting

- `ModuleNotFoundError: chatterbox`: run the setup script; always use `.venv-chatterbox/bin/python`.
- Slow on CPU: keep clips short (one ad beat per file), or run on a Mac with Apple Silicon or a GPU.
- Words garbled: shorten sentences, spell out numbers and acronyms, remove unusual symbols.
- Voice doesn't match the sample: use a cleaner 10-15 s sample (one speaker, no music, little reverb).
