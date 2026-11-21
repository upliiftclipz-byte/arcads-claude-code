---
name: ad-variations
description: >
  Turn one approved video ad into a test-ready set: several new hooks spliced onto the same body,
  in every aspect ratio (9:16, 1:1, 4:5, 16:9), with consistent file names and a manifest for upload.
  Use when someone says "make variations of this ad", "test different hooks", "give me 5 hooks",
  "ad multiplier", "resize this ad for all placements", "make square / landscape / vertical versions",
  or wants to A/B test an existing ad (including one made with clone-ad, talking-actor or Seedance).
---

# Ad variations — hooks × aspect ratios

One proven ad body, many openings, every placement. New hooks are short generated clips (3-5 s)
spliced onto the original body, so each variant costs a short generation instead of a whole new ad.
Resizing and splicing are local and free.

Helper (ffmpeg, no credits): `skills/arcads-external-api/scripts/ad_variants.py`

```bash
S=skills/arcads-external-api/scripts/ad_variants.py
python3 $S --help      # probe, suggest-cut, frame, trim, splice, reframe, matrix
```

Requires ffmpeg on PATH (`brew install ffmpeg`).

## What the user gets

```
outputs/ad-variations/2026-11-21/
  sunscreen-ugc_h0-original_9x16.mp4    ← control
  sunscreen-ugc_h1-problem_9x16.mp4
  sunscreen-ugc_h1-problem_1x1.mp4
  ...
  manifest.csv / manifest.json          ← one row per file: hook, ratio, size, duration, placements
  hooks/                                ← final hook clips (raw generations in hooks/raw/)
```

The `variant_id` in the manifest is designed to be pasted as the ad name in Meta/TikTok so results map
back to the hook and ratio.

## Workflow

### 0. Gather inputs

| Input | Required | Notes |
|---|---|---|
| Approved ad video | Yes | Local file, or an Arcads asset/talking-actor ID (download it first; see step 1) |
| How it was made | Strongly preferred | Model, prompt, references, actor/voice; from `logs/arcads-api.jsonl`, the session, or the user. Needed to make hooks that match |
| Number of hooks | Yes | Default 3 new + the original as control |
| Ratios | Yes | Default `9:16,1:1,4:5,16:9`; ask which platforms they run on and drop unused ratios |
| Product / audience | Yes | `MASTER_CONTEXT.md` default product and brand voice |

If the user only wants resizes (no new hooks), skip to step 6 with `reframe`; nothing is generated
and no credit gate is needed.

### 1. Get the ad locally and inspect it

- Arcads talking actor: `python3 skills/arcads-external-api/scripts/arcads_voice.py fetch <id> --out outputs/ad-variations/<date>`.
- Other Arcads assets: download from the asset's `url`/watch link (see reference.md).

```bash
python3 $S probe outputs/ad-variations/2026-11-21/approved.mp4
```

### 2. Find where the original hook ends

```bash
python3 $S suggest-cut outputs/ad-variations/2026-11-21/approved.mp4
```

It lists scene changes and pauses in speech in the first 8 s. If the ad has dialogue, transcribe it
(whisper, as in the clone-ad skill) and pick the pause right after the hook line. **Confirm the cut
time with the user** ("the hook is 'Okay, I need to talk about this', ending at 2.9 s"). The body is
everything after the cut; it is reused unchanged.

### 3. Write the hooks

Read [hook-formulas.md](../prompt-library/hook-formulas.md). Write N hooks from **different
archetypes**, each one line of ~5-9 words that flows into the body's next line, using only claims the
product can support. Present them with the hook approval block from that file and wait for `yes`.

### 4. Plan how each hook clip is generated (match the body's look)

| The approved ad is… | Generate hook clips with | Continuity method |
|---|---|---|
| **Talking actor** (Arcads actor) | `arcads_voice.py talk` with the **same situation and voice**, `--script "<hook line>"` | Same actor, setting and voice: near-perfect match |
| **Seedance 2.0** UGC | `POST /v2/videos/generate`, `seedance-2.0`, `duration: 4`, `audioEnabled: true` | Body's first frame (`frame --at <cut>`) as `referenceImages`, plus the original person/product references; copy the original prompt's setting/camera/lighting and swap in the hook line |
| **Veo 3.1 / Kling** with a start frame | Same model; body's first frame as `startFrame` | Check reference.md for the current image-input status per model; Kling is silent, so spoken hooks need Seedance, Veo or a talking actor |
| **Sora 2** text-only | Same model, `duration: 4`, original prompt with the hook line | Weakest continuity; warn the user and prefer one of the above |
| Voiceover over B-roll | New voiceover line (chatterbox-voiceover, free) over a 3-4 s clip | Reuse the body's music/voice style; B-roll can be a different shot |

Get the body's first frame for continuity:

```bash
python3 $S frame outputs/ad-variations/2026-11-21/approved.mp4 --at 2.9 --out outputs/ad-variations/2026-11-21/body-start.jpg
```

Upload it with the presigned-URL flow (reference.md), then follow the model's prompt-library file.
Ask for the **shortest duration** the model allows; trim later.

### 5. Credit gate, then generate

- Estimate: N hook clips × the short-clip cost for that model (logs first, then `MASTER_CONTEXT.md`, then ask). Splicing and resizing are free. Show the estimate and wait for `yes` (main SKILL.md rules).
- Generate all hooks in parallel, log each to `logs/arcads-api.jsonl`, poll, and save the raw clips to `outputs/ad-variations/<date>/hooks/raw/`. Final (trimmed) clips go in `hooks/` named after the archetype (`problem.mp4`, `curiosity.mp4`, …): file names become the hook labels, and `matrix` picks up every `.mp4` in `hooks/`.
- **Review every hook clip** before splicing: same person/outfit/setting, lighting, voice and loudness, clean lip-sync, no captions burned in. Regenerate a bad one (counts against the confirmed budget; tell the user).
- Trim each clip to just after its line ends:

```bash
python3 $S trim outputs/ad-variations/2026-11-21/hooks/raw/problem.mp4 --end 3.1 --out outputs/ad-variations/2026-11-21/hooks/problem.mp4
```

### 6. Build every combination

```bash
python3 $S matrix --body outputs/ad-variations/2026-11-21/approved.mp4 --cut 2.9 \
    --hooks outputs/ad-variations/2026-11-21/hooks/*.mp4 --include-original \
    --ratios 9:16,1:1,4:5,16:9 --mode blur --name sunscreen-ugc --out outputs/ad-variations/2026-11-21
```

- Each hook is spliced onto the body (matched to the body's size, frame rate and audio format), then every ratio is rendered.
- **Resize modes:** `blur` (default) keeps the full frame and fills the empty space with a blurred copy, which is safe for any content. `crop` fills the frame by cropping; use `--focus-x/--focus-y` to keep the subject (e.g. `--focus-y 0.3` keeps faces near the top). `pad` adds black bars.
- Resizes only reframe the shot. For a hero placement where reframing isn't good enough, offer to regenerate natively in that ratio (`aspectRatio` on the model, extra credits).

### 7. QA

Check every file before delivering, not just one:
- **The join:** watch half a second either side of the cut. No jump in lighting, framing or loudness, and no clipped words.
- **Crops:** product, face and any on-screen text fully visible in every ratio, especially 1:1 and 16:9 from vertical footage.
- **Safe zones:** in 9:16, key content stays out of the bottom ~20% and right edge (TikTok/Reels UI).
- **Length:** a long hook pushes the ad over a placement limit; check the manifest's `duration_s`.

### 8. Deliver

- Open the output folder (`open "<dir>"` on macOS) and show the manifest as a table (hooks × ratios).
- **Testing advice:** test hooks first, in the main placement ratio only (usually 9:16), with the same budget, audience and dates. Keep the original as control. Once a hook wins, roll it out to the other ratios.
- Record the hooks tested, and later the winner, in `MASTER_CONTEXT.md` (Changelog or a "Winning hooks" note) so future ads start from what worked.

## Related

- [hook-formulas.md](../prompt-library/hook-formulas.md) — hook archetypes, rules and the approval block
- [clone-ad](../clone-ad/SKILL.md) — make the first ad from a reference ad
- [talking-actor](../talking-actor/SKILL.md) — talking-actor ads and hook clips in the same voice
- [chatterbox-voiceover](../../../chatterbox-voiceover/SKILL.md) — free voiceover lines for B-roll hooks
