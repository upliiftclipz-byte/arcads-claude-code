# Camera preset library

Named, reusable camera moves for ad video prompts. Instead of writing "cinematic" (which models
ignore), pick a preset and paste its **prompt block** into the `Camera:` slot of the model template
you're using. Same preset name = same look across ads, models and team members.

Presets are prompt language, not API parameters: the model interprets them. The phrasing follows each
vendor guide's advice (explicit framing + movement + speed). How faithfully a model follows a given
move varies; when you confirm or disprove one, note it in `MASTER_CONTEXT.md` (API learnings) and in
the preset's notes here.

## How to use

1. **Pick by job, not taste:** use the [quick picker](#quick-picker) or an [ad recipe](#ad-recipes).
2. **One move per shot.** One camera move per clip, or per timestamped segment on Seedance. Two moves
   in one sentence ("orbit while zooming in") usually produces warping or neither.
3. **Paste the prompt block** into the template's camera slot, filling `{{SUBJECT}}` etc. Put camera
   direction **before** style words; models weigh earlier text more.
4. **Say the speed.** Every block includes a speed adverb (slowly, steadily, quickly). Product and
   premium moves: slow, 3-5 s minimum. UGC: casual, slightly unsteady.
5. **Lock what shouldn't move:** add "the {{SUBJECT}} stays still / centered" when only the camera
   should move, or the model may move both.
6. In the prompt you show the user, name the preset ("Camera: CAM-03 slow push-in") so it can be reused or swapped in variations.

## Model support

| Model | Camera control | Notes |
|---|---|---|
| **Seedance 2.0** | Strong; follows explicit moves and **timestamped** camera changes | Structure: Subject + Action + **Camera** + Style + Constraints. Use `[00:00]` segments to change moves within a clip |
| **Veo 3.1** | Good; template has a `Camera:` slot | With `startFrame`, keep moves modest (push-in, handheld, slow pan) so the start image stays recognisable |
| **Kling 3.0** | Good at smooth moves (orbit, dolly, crane) | Silent: best for B-roll and product moves |
| **Sora 2** | Follows "camera behavior" descriptions | Longer clips (up to 20 s) can hold one slow move, or 2-3 moves via sequential sentences |
| **Grok Video** | General prompt following | Keep to simple moves; test before relying on complex ones |
| **Nano Banana** (stills) | Framing, angle and lens only | Use the [framing and lens cheat sheet](#framing-and-lens-cheat-sheet); no movement words |
| **Talking actors** | Camera is part of the chosen situation | Filter situations by `cameraAngle` (`front`, `close_up`, `low_angle`, `depth`); see [Arcads native camera movement](#arcads-native-camera-movement) |

## Presets

Format: **ID — name** · use for · speed · prompt block · notes.

### UGC / phone (authentic, creator-style)

**CAM-01 — Handheld selfie**
- *Use for:* testimonials, reviews, talking to camera.
- *Prompt block:* `Filmed on a smartphone held at arm's length in selfie mode, slightly above eye level, casual handheld with small natural wobble and micro-adjustments as she talks.`
- *Notes:* the UGC default. Pair with the camera-flaw block from `ugc-selfie-style.md`.

**CAM-02 — Phone propped, static**
- *Use for:* routines, tutorials, "get ready with me", hands-busy demos.
- *Prompt block:* `Phone propped up on the {{SURFACE}} at chest height, static locked-off frame, {{SUBJECT}} moves in and out of frame naturally, slightly off-center framing.`
- *Notes:* the static frame makes the subject's movement the focus. Good for longer clips.

**CAM-03 — Mirror selfie**
- *Use for:* outfit, fit and body-product reveals.
- *Prompt block:* `Mirror selfie, phone visible in her hand covering part of her face, filmed in the {{ROOM}} mirror, slight handheld sway, natural room light.`
- *Notes:* tell the model the phone is visible; otherwise it may render an impossible angle.

**CAM-04 — Walk-and-talk**
- *Use for:* energetic hooks, day-in-my-life, outdoor products.
- *Prompt block:* `Selfie-mode phone held in one hand while walking forward, camera bobbing gently with each step, background moving past, {{SUBJECT}} talking to the lens.`
- *Notes:* moving backgrounds hide AI artifacts well. Keep under ~8 s.

**CAM-05 — POV hands**
- *Use for:* product demos, unboxing, apps, food, "how I use it".
- *Prompt block:* `First-person POV from chest height looking down at her hands, handheld, {{HANDS_ACTION}}, the product fills the lower half of the frame.`
- *Notes:* no face means fewer consistency problems. Spell out what the hands do, step by step.

**CAM-06 — Over-the-shoulder screen**
- *Use for:* apps, websites, "look at this" moments on a phone or laptop.
- *Prompt block:* `Over-the-shoulder shot from behind {{SUBJECT}}, looking at the {{DEVICE}} screen in her hand, slight handheld drift, screen content softly visible.`
- *Notes:* AI screens rarely render legible UI. Plan to composite the real screen recording, or keep the screen soft.

### Product / commercial

**CAM-07 — Slow push-in**
- *Use for:* the key line, product hero, building intimacy. The most versatile move.
- *Prompt block:* `The camera slowly and steadily pushes in from a medium shot to a close-up on {{SUBJECT}}, smooth dolly motion, {{SUBJECT}} stays still and centered.`
- *Notes:* works with a start frame. For UGC, a "subtle push-in" on the punchline adds energy without breaking authenticity.

**CAM-08 — Slow orbit**
- *Use for:* premium products and showing every side.
- *Prompt block:* `The camera slowly orbits 180 degrees around the {{PRODUCT}} at eye level, smooth and steady, the product stays perfectly still and centered, consistent lighting.`
- *Notes:* use 180°, not 360°: full orbits often warp labels and shapes. Keep labels simple, or accept that they'll be soft.

**CAM-09 — Macro detail sweep**
- *Use for:* texture, material, finish, ingredients, stitching.
- *Prompt block:* `Extreme macro close-up, the camera glides slowly sideways across the {{SURFACE_DETAIL}}, very shallow depth of field, focus sliding across the texture.`
- *Notes:* great 2-3 s inserts between talking beats.

**CAM-10 — Top-down overhead**
- *Use for:* flat lays, food, desk setups, unboxing contents.
- *Prompt block:* `Directly overhead top-down shot looking straight down at {{SCENE}}, static or very slow rotation, hands enter frame to {{ACTION}}.`
- *Notes:* say "directly overhead, looking straight down" or the model drifts to a 45° angle.

**CAM-11 — Lateral slide (truck)**
- *Use for:* product lineups, comparisons, revealing a set.
- *Prompt block:* `The camera slides slowly from left to right along the {{LINEUP}} at product height, smooth track, products stay still, gentle parallax with the background.`

**CAM-12 — Pull-back reveal**
- *Use for:* context reveals (product → person using it → setting), endings.
- *Prompt block:* `Starting on a close-up of {{DETAIL}}, the camera slowly pulls back to a medium-wide shot revealing {{CONTEXT}}, smooth and steady.`
- *Notes:* reverse of CAM-07. Good last beat before the CTA.

**CAM-13 — Tilt-up reveal**
- *Use for:* tall products, outfits (shoes → face), buildings, bottles.
- *Prompt block:* `The camera starts low on {{START}} and slowly tilts up to reveal {{END}}, steady motion.`

**CAM-14 — Low-angle hero**
- *Use for:* making a product or person feel powerful and premium.
- *Prompt block:* `Low-angle shot looking up at the {{PRODUCT}} placed on {{SURFACE}}, slight slow push-in, dramatic {{LIGHT}} from behind.`

**CAM-15 — Rack focus**
- *Use for:* switching attention (product → face, foreground → background).
- *Prompt block:* `Locked-off shot, focus starts on {{FOREGROUND}} in the foreground with the background blurred, then focus smoothly shifts to {{BACKGROUND}}.`
- *Notes:* models follow this inconsistently. Test before relying on it; a cut between two shots is the fallback.

### Energetic / social

**CAM-16 — Snap zoom**
- *Use for:* hooks, reactions, emphasis on one word.
- *Prompt block:* `Sudden fast snap zoom in on {{SUBJECT}}'s face as she says "{{WORD}}", then holds.`
- *Notes:* tie it to a word or moment, otherwise it fires at a random time. Max one per clip.

**CAM-17 — Whip pan**
- *Use for:* transitions between two beats or locations, high-energy edits.
- *Prompt block:* `The camera whip-pans quickly to the right with motion blur, revealing {{NEW_SCENE}}.`
- *Notes:* on Seedance, place it between two timestamped segments. Elsewhere, generate two clips and cut on the blur.

**CAM-18 — Jump-cut punch-in**
- *Use for:* UGC pacing, emphasizing a line without a camera move.
- *Prompt block:* `Jump cut to a tighter framing on {{SUBJECT}}, same angle, closer.`
- *Notes:* really an edit, not a move. On Seedance use timestamps (`[00:04] Jump cut, closer framing.`); otherwise crop in post.

**CAM-19 — Dutch tilt**
- *Use for:* playful, chaotic or "something's off" moments; gaming and youth audiences.
- *Prompt block:* `Slightly tilted dutch angle, handheld energy, {{SUBJECT}} leaning into frame.`
- *Notes:* use sparingly; it reads as unprofessional in premium ads.

### Cinematic

**CAM-20 — Tracking follow**
- *Use for:* lifestyle, sport, motion products.
- *Prompt block:* `The camera tracks smoothly alongside {{SUBJECT}} as she {{ACTION}}, keeping her at the same size in frame, steady gimbal motion, background streaming past.`

**CAM-21 — Crane up**
- *Use for:* openers, establishing shots, endings with scale.
- *Prompt block:* `The camera rises slowly and smoothly upward from ground level to a high angle above {{SCENE}}, revealing the surroundings.`
- *Notes:* Kling and Sora handle this best. Keep subjects simple.

**CAM-22 — Locked-off tripod**
- *Use for:* clean demos, premium testimonials, interviews.
- *Prompt block:* `Static locked-off tripod shot, no camera movement, {{FRAMING}}, steady and composed.`
- *Notes:* say "no camera movement" explicitly; models add drift by default.

**CAM-23 — Dolly zoom (vertigo)**
- *Use for:* dramatic realisations, pattern-interrupt hooks.
- *Prompt block:* `Dolly zoom: the camera moves forward while the lens zooms out, {{SUBJECT}} stays the same size while the background stretches away dramatically.`
- *Notes:* experimental; models often render it as a plain zoom. Test once and note the result.

## Quick picker

| Need | Preset |
|---|---|
| Talking to camera, authentic | CAM-01 handheld selfie (or CAM-02 propped) |
| Show the product in use | CAM-05 POV hands |
| Make the key line land | CAM-07 slow push-in (subtle) or CAM-18 jump-cut punch-in |
| Premium product hero | CAM-08 slow orbit → CAM-07 push-in |
| Texture / quality proof | CAM-09 macro sweep |
| Scroll-stopping hook | CAM-16 snap zoom, CAM-04 walk-and-talk, CAM-23 dolly zoom |
| Transition between beats | CAM-17 whip pan |
| Ending / CTA | CAM-12 pull-back reveal or CAM-22 locked-off |
| Starting from an approved still (`startFrame`) | CAM-01, CAM-07, CAM-22 (modest moves keep the start image intact) |

## Ad recipes

Proven shot sequences built from presets. Each beat is one clip, or one timestamped segment on Seedance.

| Recipe | Beats |
|---|---|
| **UGC testimonial** (15 s) | Hook: CAM-01 + CAM-16 on the first word → Body: CAM-01 → Proof insert: CAM-05 or CAM-09 → CTA: CAM-01 with CAM-07 subtle push-in |
| **Product demo** (15 s) | Hook: CAM-04 → Demo: CAM-05 → Detail: CAM-09 → Result: CAM-02 |
| **Premium reveal** (10-15 s) | Open: CAM-14 in low light → Reveal: CAM-08 → Detail: CAM-09 → End: CAM-07 on the logo/product |
| **Unboxing** (10-15 s) | Hook: CAM-10 sealed box → Open: CAM-05 → Reveal: CAM-13 → Reaction: CAM-01 |
| **App / software** | Hook: CAM-01 → Screen: CAM-06 (composite the real recording) → Result: CAM-02 |
| **Lifestyle** | Open: CAM-21 or CAM-20 → Use: CAM-20 → Close: CAM-12 |

## Framing and lens cheat sheet

Use for stills (Nano Banana) and to add precision to any video prompt.

| Shot size | Phrase | Use |
|---|---|---|
| Extreme close-up | `extreme close-up on her eyes / the label` | Detail, emotion |
| Close-up | `close-up, face fills the frame` | Talking, reactions |
| Medium close-up | `medium close-up, chest up` | Default talking head |
| Medium | `medium shot, waist up` | Gestures + product in hand |
| Wide | `wide shot, full body with surroundings` | Context, outfits, establishing |

| Lens feel | Phrase | Look |
|---|---|---|
| Phone front camera | `smartphone front camera, slight wide-angle distortion` | UGC selfie |
| 24 mm | `24mm wide lens` | Environment, energy, slight distortion |
| 35 mm | `35mm lens, natural perspective` | Documentary, lifestyle |
| 50 mm | `50mm lens` | Neutral, human-eye |
| 85 mm | `85mm portrait lens, shallow depth of field, creamy background blur` | Flattering faces, premium |
| 100 mm macro | `100mm macro lens, extremely shallow depth of field` | Product detail |

| Angle | Phrase | Feeling |
|---|---|---|
| Eye level | `eye-level camera` | Neutral, trustworthy |
| High angle | `camera slightly above, looking down` | Approachable, selfie-like |
| Low angle | `low angle looking up` | Powerful, heroic |
| Overhead | `directly overhead, looking straight down` | Flat lay, organised |

## Arcads native camera movement

Arcads also has a **camera-movement preset** that adds movement to an actor situation server-side,
with no prompt writing. From the API spec; not yet tested in this repo:

- `GET /v1/presets` → preset types; then `GET /v1/presets/{presetType}/templates` with the camera-movement type's exact value from that list → available motion templates.
- `POST /v1/presets/camera-movement/generate` → `StartCameraMovementDto`: `productId`*, `situationId`*, `referenceImages`* (avatar image upload path), optional `projectId`, `aspectRatio` (`21:9`, `16:9`, `4:3`, `1:1`, `3:4`, `9:16`), `strength` (movement intensity).
- Situations with `cameraMovementEnabled: true` carry a `cameraMovementMotionId`; list them with `arcads_voice.py actors --json` or `GET /v1/situations?cameraMovementEnabled=true`.

Use it when the shot is an Arcads actor situation and you want motion without re-prompting. On first
use, record what the templates look like and what `strength` values do in `MASTER_CONTEXT.md`.

## Troubleshooting

| Problem | Fix |
|---|---|
| Model ignores the move | Move the camera sentence earlier; use one move only; add a speed adverb; say "the camera moves, the subject stays still" |
| Product warps during an orbit | Shorten to 90-180°, slow it down, simplify the label, or switch to CAM-11 slide |
| Jittery or "floaty" motion | Add `smooth, stabilized, steady gimbal motion` (or remove it for UGC, where some shake is desired) |
| Camera drifts on a static shot | Add `static locked-off shot, no camera movement` |
| Move happens at the wrong time | Seedance: put it in its own `[00:0X]` segment. Others: generate shorter clips and cut |
| UGC looks too polished | Use CAM-01/02/04 phrasing plus the camera-flaw block; avoid "cinematic", "gimbal" and "dolly" |
