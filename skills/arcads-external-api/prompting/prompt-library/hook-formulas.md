# Hook formulas (first 1-3 seconds)

The hook decides whether anyone sees the rest of the ad. Testing several hooks on one proven body
is the cheapest way to improve an ad. Used by the [ad-variations workflow](../ad-variations/SKILL.md);
works for any spoken UGC/talking-actor ad.

## Rules for every hook

- **Length:** 1 spoken line, about 5-9 words (2-3.5 s at ~2.5 words/s). Visual change in the first second.
- **Seamless hand-off:** the hook must lead naturally into the body's first remaining line. Read hook + next line out loud together.
- **One idea, no setup:** start mid-thought. Cut "Hi guys", "So", "Today I want to".
- **Same truth as the body:** hooks may reframe, never invent. No claims, numbers, results or reviews the product can't back up (ad platforms and consumer law both care). Prices, discounts and guarantees only if real.
- **Diversity beats polish:** in one test round, use hooks from **different archetypes** (below), not five rewordings of one.
- **Audience-native:** use the words the audience uses for their problem (pull from reviews, comments, the brief).

## Archetypes

Each: what it does, spoken template, visual direction, example (sunscreen).

| # | Archetype | Spoken template | Visual direction | Example |
|---|---|---|---|---|
| 1 | **Problem callout** | "If you [pain], watch this." | Close-up, direct eye contact, slight lean in | "If sunscreen makes you break out, watch this." |
| 2 | **Bold claim** (provable) | "This is the only [category] I [strong verb]." | Product held to lens, quick push-in | "This is the only sunscreen I actually reapply." |
| 3 | **Curiosity gap** | "Nobody told me [surprising truth]." | Mid-action, half-turned to camera | "Nobody told me sunscreen could feel like nothing." |
| 4 | **Question** | "Why does nobody talk about [thing]?" | Raised eyebrow, head tilt | "Why does nobody talk about white cast?" |
| 5 | **POV / relatable** | "POV: you finally found [desired outcome]." | Selfie, natural setting, small smile | "POV: you finally found a sunscreen you don't hate." |
| 6 | **Negative / warning** | "Stop [common mistake]." | Hand up "stop" gesture, firm tone | "Stop buying sunscreen that pills under makeup." |
| 7 | **Social proof** (real only) | "[Real number / group] switched to this for a reason." | Product in frame, confident nod | "My whole friend group switched to this for a reason." |
| 8 | **Before/after tease** | "Day one versus day fourteen." | Split moment or quick reveal | "Week one versus week three. Look at this." |
| 9 | **Unboxing / reveal** | "It finally came." / "Okay, it's here." | Package opening, excited energy | "Okay, it finally came. Let's try it." |
| 10 | **Reaction / pattern interrupt** | "Wait. [short exclamation]." | Sudden movement, double-take, whip to camera | "Wait. Why is nobody using this?" |
| 11 | **Direct address / targeting** | "[Audience], this one's for you." | Point to camera, warm | "Oily skin girls, this one's for you." |
| 12 | **Story open** | "I almost didn't [action]..." | Softer tone, looking off then back to camera | "I almost returned this. Then day three happened." |

## Picking a test set

- **3 hooks:** problem callout + curiosity gap + one of POV / reaction.
- **5 hooks:** add bold claim (if provable) + direct address.
- Keep the **original hook** in the test as the control.
- Keep everything else identical (body, voice, music, captions, ratio) so the hook is the only variable.

## Writing the visual for a generated hook clip

The new hook clip must look like the same video: **same person, outfit, setting, lighting, camera
style and audio level** as the body's first frame. In the generation prompt, describe the hook action
and line, then copy the body's setting/camera/lighting description word for word. Use the body's
first frame as the reference image or start frame (see the ad-variations workflow).

## Presenting hooks for approval

Use the main SKILL.md dialogue gate format, one numbered line per hook, with archetype and timing:

```
🪝 Hook variants (please confirm before I generate)

  0. [CONTROL]  "<original hook>"                                   (kept as is)
  1. [PROBLEM]  "If sunscreen makes you break out, watch this."     8 words ≈ 3.2s
  2. [CURIOSITY] "Nobody told me sunscreen could feel like nothing." 8 words ≈ 3.2s
  3. [REACTION] "Wait. Why is nobody using this?"                   6 words ≈ 2.4s

  → each flows into: "<body's first remaining line>"

Approve these hooks? (yes / edit / rewrite)
```
