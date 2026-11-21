---
name: talking-actor
description: >
  Voice + lip-sync videos with Arcads talking actors: an actor says your script (or lip-syncs to
  a voiceover file) in a chosen or cloned voice. Use when someone asks for a talking avatar, a
  talking-head / testimonial / spokesperson ad, "make this person say ...", lip-sync, a voiceover
  read by an AI actor, voice cloning, or the same script read by several actors or in several voices.
---

# Talking actor — voice + lip-sync (Arcads)

Arcads' **talking-actor** endpoint turns a script, or an audio file, into lip-synced video of an
Arcads actor. Each actor is a *situation* (an actor filmed in a specific setting). Voices come from
the Arcads voice library, a voice you clone, or an ElevenLabs voice imported into Arcads.

Helper script (standard library only, reads `.env`, logs to `logs/arcads-api.jsonl`):

```bash
python3 skills/arcads-external-api/scripts/arcads_voice.py --help
```

Use the helper rather than hand-written curl: it handles upload, polling, logging and download.

## Pick the path

| User has / wants | Path | Command |
|---|---|---|
| A script, any Arcads actor, an Arcads voice | **A. Script → talking actor** | `talk --script "..."` |
| A finished voiceover (recorded, or made free with the **chatterbox-voiceover** skill) | **B. Audio → lip-sync** | `talk --audio file.mp3` |
| Their own voice / a brand voice they have rights to | **C. Clone the voice**, then A | `clone-voice ...` then `talk --actor sit:voice` |
| One of the repo's own influencers (`references/influencers/`) speaking | **D. Own character** | See [Own influencers](#d-own-influencers) |
| Same script, several actors or voices (A/B testing) | A with repeated `--actor` | `talk --actor s1:v1 --actor s2:v2 ...` |

## Models (`--model`)

| Model | What it is | Use when |
|---|---|---|
| `arcads_1.0` *(default)* | Arcads' own talking-actor model | Standard UGC talking-head ads |
| `audio_driven` | Animation driven by the audio track | Lip-syncing to an existing voiceover (path B) |
| `omnihuman` | OmniHuman: more body and gesture motion | When more expressive, full-upper-body movement is wanted |

The API documents these three values but not their differences in quality, price or speed. On the
first real use of each, generate one short clip, then record observations and the credits charged
in `MASTER_CONTEXT.md` (Credit costs + API learnings) so later sessions can choose with evidence.

## Workflow

### 1. Gather inputs

- **Product:** `productId` from `MASTER_CONTEXT.md` (required by the API).
- **Session project:** reuse today's "Arcads API - YYYY-MM-DD" project (see the main SKILL.md) and pass `--project`.
- **Script** (path A/C/D) or **audio file** (path B). Exactly one; the API accepts max 1 audio file.
- **Actor brief:** gender, age bracket (`Young Adult`, `Adult`, `Senior`), setting/vibe, camera angle.
- **Voice brief:** language, gender, accent, energy. Or a cloned/imported voice ID.

### 2. Choose the actor

```bash
python3 skills/arcads-external-api/scripts/arcads_voice.py actors --gender Female --age "Young Adult"
python3 skills/arcads-external-api/scripts/arcads_voice.py actors --name Ava
python3 skills/arcads-external-api/scripts/arcads_voice.py actors --mine      # your workspace's own actors
```

Results are lip-sync-ready situations (`talkingActorEnabled=true`). Each line shows ID, actor, angle,
tags (setting/scenario), emotions and a **preview URL**. Shortlist 2-3 that match the brief (tags and
emotions matter: an excited bedroom selfie reads very differently from a calm kitchen talk), and show
the user the preview links to pick from. Use `--json` for the full records.

### 3. Choose the voice

```bash
python3 skills/arcads-external-api/scripts/arcads_voice.py voices --language English --gender Female
```

Each voice has a sample URL; let the user listen before choosing. If no `voiceId` is given for an
actor, Arcads uses that actor's default voice.

**Cloning (path C):** only clone a voice the user owns or has written permission to use. Ask once,
explicitly: "Is this your voice, or do you have the speaker's permission to clone it?" Do not clone
celebrities, public figures or anyone who hasn't consented. Then:

```bash
python3 skills/arcads-external-api/scripts/arcads_voice.py clone-voice --name "Brand narrator" \
    --language English --gender Female references/voices/narrator-1.mp3 references/voices/narrator-2.mp3
```

Samples can be audio or video (the API isolates the voice from music and noise). 30-90 seconds of
clean speech across 1-3 files works best. **API-cloned voices are temporary**: note the `expiresAt`
date for the user and record the voice ID in `MASTER_CONTEXT.md`. For a permanent voice, clone it in
the Arcads dashboard or import it from ElevenLabs (`/v1/elevenlabs/*`).

### 4. Write and confirm the script

Follow the main SKILL.md **dialogue confirmation gate** exactly (numbered beats, word count, explicit
`yes`). Talking-actor specifics:

- **Pace:** ~2.5 spoken words per second. 15 s ≈ 35-40 words; 30 s ≈ 70-80 words.
- **Write for the ear:** short sentences, contractions, one idea per line. Punctuation drives
  delivery: commas = short pause, full stop = longer pause, "?" lifts the ending, "..." trails off.
- **Spell out** numbers, prices, symbols and abbreviations the way they should be said
  ("twenty-nine ninety-nine", "S-P-F fifty").
- **No stage directions** in the script; the actor will read them aloud. For emotional delivery,
  pass `--emotion` (`autoAddScriptEmotion`).
- **Hook in the first line** (pattern interrupt, bold claim, relatable problem); **CTA in the last.**
- Long script → split into separate clips at sentence boundaries and stitch later with ffmpeg.

### 5. Cost gate

Follow the main SKILL.md cost-estimation rules. Look for earlier `POST /v2/talking-actors/generate`
entries in `logs/arcads-api.jsonl` first, then the talking-actor rows in `MASTER_CONTEXT.md`;
otherwise ask the user. Each actor in a request is a separate video and is billed separately.
Always show the estimate and wait for `yes`.

### 6. Generate

Preview the exact request first (no credentials needed, nothing is sent):

```bash
python3 skills/arcads-external-api/scripts/arcads_voice.py talk --product <productId> --project <projectId> \
    --actor <situationId>:<voiceId> --script "<approved script>" --dry-run
```

Then run it for real with `--wait --out outputs/talking-actor/<YYYY-MM-DD>`:

```bash
# Path A / C: script
python3 skills/arcads-external-api/scripts/arcads_voice.py talk --product <productId> --project <projectId> \
    --actor <situationId>:<voiceId> --script "<approved script>" --wait --out outputs/talking-actor/2026-11-21

# Path B: lip-sync to a voiceover file
python3 skills/arcads-external-api/scripts/arcads_voice.py talk --product <productId> --project <projectId> \
    --actor <situationId> --audio outputs/voiceovers/hook.mp3 --model audio_driven --wait --out outputs/talking-actor/2026-11-21

# A/B test: same script, three actor/voice pairs (3 videos, 3x the cost)
python3 skills/arcads-external-api/scripts/arcads_voice.py talk --product <productId> \
    --actor s1:v1 --actor s2:v2 --actor s3 --script "..." --wait --out outputs/talking-actor/2026-11-21
```

The helper starts one generation per actor, appends each to `logs/arcads-api.jsonl`, polls
`GET /v2/talking-actors/{id}` until `completed`/`failed`, updates the log with time (and credits when
the asset reports them), then saves the video, or prints the watch URL if it can't be downloaded.
If you stop waiting, resume later with `status <id>` and `fetch <id> --out <dir>`.

### 7. Deliver

- Make sure the videos are in the session project (`POST /v1/assets/add-to-project` if the API did not file them).
- Give the watch URLs, save files under `outputs/talking-actor/`, and **open the output folder** (`open "<dir>"` on macOS).
- Check each video: lip-sync on plosives (p/b/m), mispronounced brand names, awkward pauses. To fix a
  brand name, respell it phonetically in the script ("Arcads" → "Ar-kads") and regenerate.
- Record learnings (model differences, credits, good situation/voice pairings) in `MASTER_CONTEXT.md`.

## D. Own influencers

The API cannot create a talking actor from an image; actors come from Arcads. To make one of the
repo's own characters (e.g. `references/influencers/sofia-.../01-hero-front.jpg`) speak:

1. **Best lip-sync and voice control:** create a custom actor from the hero image in the Arcads
   dashboard. It then appears in `actors --mine` and works with paths A-C.
2. **No dashboard step, existing workflow:** Veo 3.1 with the hero (or an approved UGC still) as
   `startFrame` and the dialogue in the prompt (see `prompt-library/veo-3-1.md`). Good motion, but you
   can't choose the voice.
3. **Your own voice track:** Seedance 2.0 image-to-video with the hero in `referenceImages`, the
   voiceover in `referenceAudios` and `audioEnabled: true` (see `prompt-library/seedance-2-ugc.md`).
   How closely Seedance lip-syncs to a supplied track is unconfirmed; test one short clip first and
   record the result.

## Errors

- **403:** credentials or workspace access; run `./scripts/check-arcads-env.sh`.
- **402 on clone-voice:** plan or credit limit; tell the user, don't retry.
- **422:** missing `script`/`referenceAudios`, more than one audio file, unknown situation or voice
  ID, or moderation. Re-fetch IDs with `actors` / `voices` and check the script.
- **`failed` status:** the helper prints the API's error. Shorten or simplify the script, try another
  situation, then report.
