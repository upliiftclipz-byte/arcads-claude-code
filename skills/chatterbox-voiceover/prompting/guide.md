# Writing and tuning ad voiceovers for Chatterbox

## Script rules

Write for the ear rather than the page:

- **Short sentences.** One idea each. Chatterbox stays stable on short inputs and drifts or repeats itself on long ones.
- **One paragraph per beat**, with a blank line between beats. The CLI renders each paragraph separately and inserts a pause, so paragraphs control pacing.
  ```
  Okay, I need to tell you about this.

  I was spending forty dollars a week on coffee. Every. Single. Week.

  Then I found Arcads Cola. Same kick, half the sugar.

  Link's below. Try it.
  ```
- **Write numbers and symbols as words.** "forty dollars" not "$40", "twenty-four seven" not "24/7", "fifty percent off" not "50% off".
- **Spell brand names the way they're pronounced** when the model gets them wrong: "Arcads" → "Ar-cads", "Huel" → "Hugh-el". Keep a list of working spellings in `MASTER_CONTEXT.md`.
- **Punctuation is your direction.** Commas give short breaths, periods give full stops, "..." gives a trailing hesitation, and "?" makes an upward read. Avoid ALL CAPS, which doesn't add emphasis reliably.
- **Contractions and filler words** ("okay", "honestly", "like") make UGC sound real. Use one or two, not one per line.
- **Length budget:** about 2.5 words per second for casual UGC and about 2.2 for calm or premium reads.

| Ad length | Words |
|---|---|
| 6 s bumper | 12–15 |
| 15 s | 35–40 |
| 30 s | 70–80 |

## Paralinguistic tags (turbo / nano only)

`[laugh]` `[chuckle]` `[sigh]` `[gasp]` `[cough]` `[clear throat]` `[sniff]` `[groan]` `[shush]`

Put a tag where the sound would actually happen, and use at most one or two per 15 s:

- `I tried it expecting nothing [chuckle] and now I'm on my third case.`
- `[sigh] Another Monday, another eight a.m. meeting.`
- `Wait. [gasp] That's the price?`

The `original` and `multilingual` models read tags aloud as words. Strip them before rendering with those models.

## Tuning recipes

`--exaggeration` and `--cfg` only work with `original` and `multilingual`.

| Goal | Model | Settings |
|---|---|---|
| Natural UGC talk-to-camera | `turbo` | defaults |
| Fast drafts on a laptop CPU | `nano` | defaults |
| Hype, energetic, "you NEED this" | `original` | `--exaggeration 0.7 --cfg 0.3` |
| Calm, premium, ASMR-ish | `original` | `--exaggeration 0.3 --cfg 0.5 --pause-ms 500` |
| Testimonial, sincere | `original` | `--exaggeration 0.5 --cfg 0.4` |
| Fast-talking reference speaker | `original` / `multilingual` | `--cfg 0.3` |
| Localized read keeping one voice | `multilingual --lang xx` | defaults; `--cfg 0` if the accent bleeds through |

Higher exaggeration speeds speech up. Lower `--cfg` compensates with slower, more deliberate pacing.

`--temperature` (default 0.8) controls variation. Use 0.6–0.7 for a consistent brand voice across many renders and 0.9 for livelier, more varied takes.

## Takes and reproducibility

- Use `--takes 3 --seed N` for hooks. Each take uses seed N, N+1 and so on, and the `.json` sidecar records the seed.
- To regenerate a take the user liked, rerun with the same text, voice, settings and `--seed`. The `-takeK` file used seed `N+K-1`.
- If one paragraph is bad, re-render only that paragraph with `--text` and splice it in. Don't re-roll the whole script.

## Localization checklist

1. Translate the script yourself, then rewrite it for the spoken idiom of the target market. Don't translate word for word.
2. Recheck the length: German and Spanish usually run 15–25% longer than English. Trim to fit.
3. Render with `--model multilingual --lang <code>` and the same consented `--voice`.
4. Ask a native speaker to review it before it runs as a paid ad. Flag this to the user.
