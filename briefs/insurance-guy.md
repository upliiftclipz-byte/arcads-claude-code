# Ad brief — Insurance Guy

Paste everything inside the box below into Claude Code (or Cursor) from the root of this repo to
start the first batch of Insurance Guy video ads. It uses the talking-actor, Seedance 2.0 UGC,
hook-formulas, camera-presets and ad-variations workflows.

**Keep this brief current:** when premium-increase alerts, shopping-window reminders and the
$50/year Portfolio price are published in the app, remove them from the "Hard rules" list and add
them to `mainFeatures` / the offer.

````text
Create a first batch of video ads for my app "Insurance Guy" using the Arcads skills in this repo.

## Product (create it in Arcads first if it doesn't exist: POST /v1/products, then save the productId as the default product in MASTER_CONTEXT.md)
- name: Insurance Guy
- description: A web app (installable on your phone's home screen) that keeps all your insurance in one calm place — homeowners, auto, flood, umbrella and more. Track carrier, broker, policy number, premium, payment schedule, renewal date and the policy document itself. Upload a policy PDF and it reads the details for you. Email reminders before payments and renewals; red/amber/green status shows what's overdue, due soon or handled. Group policies by property; track escrow vs. pay-it-yourself.
- targetAudience: US homeowners 30-60, landlords and people with multiple properties/vehicles who juggle several policies and carriers.
- painPoint: Missed or surprise insurance payments, lapsed coverage, digging through email for a policy number, not knowing what's due when, escrow confusion.
- mainFeatures: all policies in one place; AI reads uploaded policy documents; payment & renewal email reminders; red/amber/green due-date status; group by property; escrow vs. direct tracking; secure document storage.
- perceived: Calm, organized, in control — "I have a guy for that."

## Brand voice
Calm, reassuring, plain-spoken, a little warm humor. Never fear-mongering. Tagline idea: "Know exactly what insurance is due, and when."

## Hard rules (insurance ads)
- Insurance Guy is an organizer and reminder tool — NOT an insurer, broker or agent. Never imply it sells insurance, gives advice, finds coverage or saves money on premiums.
- No made-up stats, reviews, ratings or user counts. No claims about specific insurers.
- Only advertise features that are live today (list above). Do not mention premium-increase alerts, shopping-window reminders or the new $50/year price — they aren't published yet.
- CTA: "Try Insurance Guy free" (Free plan exists). Don't speak URLs; I'll add the link in the ad platform.
- Follow the dialogue confirmation gate and credit cost gate for everything.

## Deliverables — 3 concepts, 9:16, ~15 s each
1. **Talking-actor testimonial** (talking-actor skill): an Adult homeowner, kitchen or home-office setting, warm voice. Story: "my renewal snuck up on me last year" → now everything's in one place with reminders → CTA. Shortlist 3 actor/voice pairs with previews for me to pick.
2. **UGC selfie demo** (Seedance 2.0 UGC formula): creator at the kitchen table with a stack of insurance mail, uploads a policy on her phone, relieved reaction. Camera: CAM-01 handheld selfie → CAM-05 POV hands on the phone → CAM-07 subtle push-in on the CTA line. Use an influencer from references/influencers/ that fits a 30-45 homeowner, or ask me.
3. **Problem/solution with a landlord angle** (Seedance or Veo): "three properties, nine policies, one app." Visual: papers and sticky notes → calm, organized phone screen moment. Keep any phone screen soft/out of focus (I'll composite the real app later).

For each concept: write the script with 3 hook options from hook-formulas.md (different archetypes), name the camera presets used, show me dialogue + cost before generating. After I approve a winner, run the ad-variations skill: 3 hooks × 9:16, 1:1, 4:5 with a manifest.

Save everything under outputs/insurance-guy/<date>/ and log learnings in MASTER_CONTEXT.md.
````

## Notes

- **Why the rules:** ad platforms reject, and insurance advertising rules restrict, ads that look like they sell insurance or promise savings. Positioning Insurance Guy as an organizer avoids both.
- **No spoken URLs:** AI voices mangle them; put the link (insurance.haveaguy.online) in the ad platform instead.
- **App screens:** AI models can't render the real app UI legibly. Keep screens soft in generation and overlay real screenshots or a screen recording in editing.
