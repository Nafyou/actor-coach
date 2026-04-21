# Emotion Performance Guide

Short, practical guide for showing emotion on camera. Each section pairs what's
physically happening on the face (Ekman's **Facial Action Units — AUs**) with
an approach to *produce* the feeling so the face does the right thing honestly.

## How to use this with the Actor Coach

```
cd /Users/sahil/Coding/faceemotion2013 && .venv/bin/python actor_coach.py 1
```

Pick **Freeplay** (option 3) from the menu — that's the mirror view these
guides are written for. What you'll see overlaid on the preview:
- **Top label on the face** — nuanced emotion word (intensity tier)
- **Second line** — raw class + % (or a Plutchik dyad name like *awe*, *remorse*)
- **Top-left bars** — all 8 class probabilities from HSEmotion
- **Top-right circle** — Russell circumplex: valence (pleasant↔unpleasant) × arousal (calm↔excited)
- **Bottom-left AU panel** — active Action Units derived from MediaPipe
  blendshapes. Match these numbers to the AU recipes below.

## Contents

- [The core principle](#the-core-principle)
- [How actors practice emotion](#how-actors-practice-emotion)
- [FACS AU cheat sheet](#facs-au-cheat-sheet)
- [Happiness](#happiness) — serene → happy → ecstatic
- [Sadness](#sadness) — pensive → sad → grieving
- [Anger](#anger) — annoyed → angry → enraged
- [Fear](#fear) — apprehensive → afraid → terrified
- [Surprise](#surprise) — distracted → surprised → amazed
- [Disgust](#disgust) — disinterested → disgusted → loathing
- [Contempt](#contempt) — dismissive → contemptuous → disdainful
- [Neutral](#neutral) — stillness as an active state
- [Blendshape → AU mapping reference](#blendshape--au-mapping-reference)

---

## The core principle

> Don't play emotion. Play the **action** under the emotion, and the emotion arrives.

Every section below offers a **memory** route (recall), a **body** route
(physical doors into the feeling), and an **action** route (pursue an
objective and let the feeling follow). Use whichever gets honest. The FACS
column is the diagnostic — if the webcam's AU overlay matches the guide, your
face is telling the truth.

Trying to force the face into a shape produces **indicating** — the camera
catches the lie immediately, and the tool will usually mis-classify it or
flag it as *neutral* because the AU pattern doesn't match any real emotion.

---

## How actors practice emotion

A compressed tour of the major traditions. They aren't mutually exclusive —
most working actors borrow from several.

### Stanislavski's system
The root of modern technique. Core tools:
- **Given circumstances** — who/where/when/why, read from the text. The more
  specific your circumstances, the more automatic the feeling.
- **Objective** — what the character *wants* in this moment. Phrase as an
  active verb ("to convince him", "to get her to stay"). Emotions are the
  by-product of pursuing an objective against an obstacle.
- **Emotional memory (affective memory)** — recall a real past experience
  with similar stakes; substitute its sensations into the scene.

### Lee Strasberg's Method
Intensifies Stanislavski's emotional-memory work:
- **Sense memory** — don't recall the event itself, recall its **physical
  sensations**: the smell of the room, the temperature of a hand, the sound
  of a door. Sensations are easier to conjure than emotions and they drag
  the feeling in behind them.
- Controversial because it can encourage dredging up trauma — use with care.

### Sanford Meisner
Rejects "thinking your way" into emotion:
- **"Live truthfully under imaginary circumstances."**
- **Repetition exercise** — two actors repeat each other's observations
  until something spontaneous cracks through. Strips away planning.
- Emotion lives in the **other person**, not in you. Focus outward.

### Michael Chekhov
Body-first:
- **Psychological gesture (PG)** — a stylized whole-body movement that
  embodies the character's inner drive (a grasping claw for greed, a
  pressed-down sphere for grief). Perform the PG once before the scene; the
  body carries the feeling in without you having to "play" it.
- **Atmosphere** — imagine the scene's *mood as a physical substance* in
  the air.

### Practical Aesthetics (Mamet / Macy)
Anti-emotional-memory:
- Don't reach for feeling at all. Define the **essential action** ("to
  refuse a bad deal"), pick an **as-if** (a real moment from your life that
  matches the stakes), and simply *do* the action. Emotion is not the job.

### General practice routines

**Warm-up (before emotional work):**
- 5 min breath — slow 4-in / 6-out, grounding the body
- 5 min body — shake out, roll shoulders, yawn, release jaw and tongue
- 5 min voice — hum, lip-trill, sirens up and down
- 5 min face — exaggerated AU drills: brows up/down/together, wide smile,
  lip-pucker, tongue stretches, gentle "lion" (mouth and eyes fully open)

**The daily five-minute emotion** — pick one from the guides. For a week:
1. One minute of body/breath prep matched to the emotion
2. One minute of memory — not forcing, just revisiting
3. Two minutes at the webcam, playing the suggested objective
4. One minute of release — shake out, breathe, step away

If you're hitting the expected AUs at ≥50% without straining, it's landing.

---

## FACS AU cheat sheet

| AU | Name | What it looks like |
|---|---|---|
| 1 | Inner brow raiser | Inside tips of eyebrows lift (sadness/fear) |
| 2 | Outer brow raiser | Outer brows lift (surprise) |
| 4 | Brow lowerer | Brows pull down and together (anger, concentration) |
| 5 | Upper lid raiser | Eyes widen (surprise, fear) |
| 6 | Cheek raiser | Crow's feet — the "Duchenne" marker of a genuine smile |
| 7 | Lid tightener | Lower-lid squint (anger, suspicion) |
| 9 | Nose wrinkler | Upper-lip pull / bunny nose (disgust) |
| 10 | Upper lip raiser | Sneer toward the nose (disgust / contempt) |
| 12 | Lip corner puller | Smile |
| 14 | Dimpler | Asymmetric lip corner (contempt when unilateral) |
| 15 | Lip corner depressor | Corners down (sadness) |
| 17 | Chin raiser | Pout / chin bunching (sadness, disgust) |
| 20 | Lip stretcher | Lips pulled sideways (fear) |
| 23 | Lip tightener | Pressed lips (anger, held-back) |
| 25 | Lips part | Mouth open slightly |
| 26 | Jaw drop | Jaw falls open (surprise, fear) |
| 27 | Mouth stretch | Wide-open mouth (fear, terror, shock) |
| 43 | Eyes closed | Squeezing or slow blink |

---

## Happiness

Serenity through ecstasy. The famous "Duchenne vs non-Duchenne" emotion —
the camera sees the difference between a real smile and a polite one
instantly.

### Facial signal (FACS)
**AU 6 + AU 12** is the **Duchenne smile** — the genuine one:
- **AU 12** Lip corner puller — mouth corners pull up and out. This is the
  part everyone can fake.
- **AU 6** Cheek raiser — the orbicularis oculi muscle pulls the cheek up,
  creating crow's feet and narrowing the eye slightly. **This is the part
  you cannot fake voluntarily** (most people can't; a small percentage can).

Without AU 6 you have a social smile, not a happy one. The webcam tool will
often classify AU 12 alone as *neutral* or weak *happy*.

Higher intensities add **AU 25/26** (lips part, teeth show), **AU 27** (mouth
stretches open — laughter), head tilt back, and sometimes eye closure (AU 43).

### Body & breath
- Breath: openly, fuller inhales. Ecstatic laughter is breath out of control.
- Chest: lifts. Shoulders ease back and down (not up; tense joy is anxiety).
- Eyes: brighten. The AU 6 crinkle is the tell.
- Weight: light; slight forward lean.
- Voice: pitch rises; vowels open.

### Intensity tiers
| Tier | Word | What's happening |
|---|---|---|
| Low | serene | Gentle AU 12, minimal AU 6. Soft, content |
| Mid | happy | Full Duchenne smile. Teeth visible |
| High | ecstatic | AU 12+6+25+26/27. Laugh-breath. Head back |

### Method approaches
**Memory route.** Don't recall a "happy" event (too abstract). Recall a
**specific joke** — a real one that made you laugh until you couldn't
breathe. The sense-memory of laughter-breath is more reliable than the
memory of being happy.

**Body route.** *Psychological gesture:* open arms expansively from chest
outward, palms up, like throwing petals. Three times with breath — the
chest-opening directly creates joy's breath pattern. Also: **smile first,
find the reason after**. The facial-feedback hypothesis is real — voluntary
AU 12+6 can nudge mood upward within about 30 seconds.

**Action route.** Play an objective of *sharing*. Happiness rarely exists
alone:
- "To make her laugh"
- "To show him what I found"
- "To celebrate this together"

### Exercises
- **Duchenne drill.** Produce AU 12 alone → watch the tool. Now activate AU 6
  (squint slightly, feel the cheeks rise). Hold 5s. Release. 10 reps.
- **Laugh-back-in.** Fake a laugh — "ha ha ha" with breath — for 20s past
  awkward. Around the 25s mark a real laugh usually breaks through.
- **"Something delightful" pivot.** List three specific, tiny delightful
  things in the room. Smile privately at one. Start the scene still seeing it.

### Common pitfalls
- Social-smile lockdown (AU 12 without AU 6). The camera knows.
- Smiling too long — happiness *pulses*, it doesn't sustain at max.
- Forcing the eye squint → tension reads as AU 7 (disgust/anger), not AU 6.
- Ignoring the breath — happy dialogue with held breath is a dead giveaway.

### Verify
- Top label: **serene → happy → ecstatic**
- Bar chart: happiness dominant; surprise as second when laughing
- Circumplex dot: **top-right** (positive valence, high arousal)
- Plutchik dyad: *delight* (happiness + surprise) appears during real laughter
- AU overlay: **both AU 6 and AU 12**. AU 12 without AU 6 ≈ fake

---

## Sadness

From pensiveness to grief. The hardest emotion for most actors because the
first instinct is to *push* — but real sadness is a collapse, not a
performance.

### Facial signal (FACS)
**AU 1 + AU 4 + AU 15** is the canonical sadness recipe:
- **AU 1** Inner brow raiser — the inside tips of the eyebrows lift.
  **Hardest AU to produce voluntarily** — most people can't. Its presence
  is a near-sure sign the emotion is real.
- **AU 4** Brow lowerer — brows draw down and together, creating the
  vertical crease between them.
- **AU 15** Lip corner depressor — mouth corners pull down.

Often accompanied by **AU 17** (chin raiser, slight pout) and **AU 43**
(droopy/closing eyes). Gaze drops; head lowers.

**What the webcam should show:** *sad* dominant, valence negative, arousal
low/negative. If you see *angry* instead, you're locking AU 4 without the
AU 1 lift — the brows are pressing down instead of being pulled in from
the inside.

### Body & breath
Sadness is a body that has given up holding itself up:
- Breath: short, shallow inhale; held for a beat; long sighing exhale. The
  inhale catches — that's the sob reflex, and it's what actors miss when
  they "play sad" with smooth breathing.
- Chest: collapses forward and down; shoulders round; sternum sinks.
- Eyes: soften and unfocus. Look through things, not at them.
- Weight: heavy. Limbs feel like they cost energy to move.
- Throat: tightens. Swallowing gets noisy.

Practical trick: **let your head get heavy** and stop supporting it fully.
Two millimeters of neck release is enough. The AUs follow.

### Intensity tiers
| Tier | Word | What's happening |
|---|---|---|
| Low | pensive | Awareness of a loss; thought-heavy. AU 1 only, faint |
| Mid | sad | Full AU 1+4+15. Breath catches |
| High | grieving | Collapse — body shakes; AUs deepen; eyes wet |

### Method approaches
**Memory route.** Don't reach for the *event*. Reach for the **sensations**
around it: the smell of the room, the texture of a fabric, the sound you
remember (a clock, a distant voice, silence), the temperature of your
hands. The senses sneak the feeling in.

**Body route.** *Psychological gesture:* both hands slowly press downward
from chest height to hips, as if lowering something heavy into water.
Three times with breath. Then begin the scene. The body remembers the weight.

**Action route.** Sadness is almost never the *objective*. Give yourself
an action the sadness can leak out from:
- "To say goodbye without breaking"
- "To convince her I'm fine"
- "To finish this sentence before I cry"

The struggle to hold composure produces more honest grief than trying to grieve.

### Exercises
- **One-sentence goodbye.** Write one sentence you'd say to someone you've
  actually lost. Say it to camera. Say it again, trying *not* to cry.
  Repeat for five minutes. Watch the AU 1 lift appear.
- **Heavy breath ladder.** (1) Normal breathing, neutral face — tool shows
  neutral. (2) Shallow top-of-chest breath, shoulders rounded — bars shift
  toward sad. (3) Caught inhale every third breath. (4) Audible sighing
  exhale. By stage 3–4 the face usually reads sad without acting.
- **Memory soak.** Pick a sad memory you've *already processed*. Sit with
  it (3-min timer), not performing. Immediately after, do a line. The
  residue stays in the face for 30–60 seconds.

### Common pitfalls
- Scrunching the whole brow instead of the inner lift → reads as angry.
- Forced lip tremor — let it quiver only if it actually wants to.
- Rushing to tears — the most powerful sad performances are on the *edge*.
- Looking up — almost always wrong. Sad eyes drop.
- Playing sad *through* the scene — exhausting. Let sadness rise and fall.

### Verify
- Top label: **pensive → sad → grieving**
- Bar chart: sadness dominant; neutral often second
- Circumplex dot: **bottom-left** (negative valence, low arousal). If
  bottom-right you're smiling politely — release the cheeks.
- AU overlay: **AU 1, 4, 15 active**. Bonus for AU 17.

---

## Anger

Annoyance through rage. Two common mistakes: playing *loud* instead of
*pressurized*, and playing anger as an explosion when it's usually a
restraint that's about to fail.

### Facial signal (FACS)
**AU 4 + AU 5 + AU 7 + AU 23** — the classic anger composite:
- **AU 4** Brow lowerer — brows pull down and together. The vertical crease.
- **AU 5** Upper lid raiser — eyes widen within the lowered brow (the
  "glare"). AU 4 + 5 together is what makes anger look predatory.
- **AU 7** Lid tightener — the lower lid tenses, narrowing the eye from below.
- **AU 23** Lip tightener — lips press together, turn pale-ish.

At higher intensities add **AU 10** (upper lip raised — sneer), **AU 17 + 24**
(chin up, lips pressed hard), and sometimes **AU 25/26** when shouting.

Anger has AU 4 **without** AU 1. Sadness has AU 4 **with** AU 1. That's
the webcam's tell.

### Body & breath
Anger is almost always a **contained pressure**:
- Breath: held or short, through the nose. Nostrils flare. Sudden audible
  exhales when the lid cracks.
- Jaw: clenched (AU 23 + masseter).
- Hands: close to fists or grip something. Whitened knuckles.
- Spine: lengthens, chest lifts. Anger stands *up* where sadness falls down.
- Temperature: neck and ears feel hot.
- Weight: forward onto the balls of the feet.

### Intensity tiers
| Tier | Word | What's happening |
|---|---|---|
| Low | annoyed | AU 4 flickers on/off. Jaw sets briefly |
| Mid | angry | Full composite held. Controlled breath. Voice compressed |
| High | enraged | Composite + AU 10 + open mouth. Breath ragged. Body heat |

### Method approaches
**Memory route.** Recall a time you were **wrongly accused** or
**interrupted repeatedly**. Injustice/violation flavors access more easily
than generic "mad". Sense-memory the heat in the chest and tightness in jaw.

**Body route.** *Psychological gesture:* one open hand chops downward from
overhead past the hip with a sharp exhale — a vertical strike. Three reps.
Drop the gesture and begin. The body is loaded. Also: grip a rolled towel
hard for 8s, release, start the scene within 10s. Residual muscle tension
produces anger's AUs naturally.

**Action route (often safest).** Anger comes from trying to *prevent*:
- "To stop her from leaving"
- "To force him to admit he lied"
- "To get in the last word before I lose it"

The character isn't trying to *be* angry; they're trying to *win*, and
failing to win produces the pressure that surfaces as anger.

### Exercises
- **Pressure cooker.** Pick a sentence ("I told you a hundred times"). Say
  it at 3/10 volume with full emotional cost. Then 4/10. Then 5. Most actors
  are more truthful at 3 than 9. Find the volume where AUs activate without
  shouting — that's your ceiling.
- **Jaw drill.** Clench jaw. Push tongue into roof of mouth. Hold 10s with
  nose-breath. Release. Notice AU 7 and AU 4 appeared.
- **The interruption.** Have a partner interrupt your line three times.
  The third almost always produces honest irritation.

### Common pitfalls
- Frowning without AU 5 → looks worried, not angry.
- Bugging eyes with slack brow → looks surprised.
- Shouting without the jaw — voice gets loud, face stays slack. Reads
  surprised or neutral.
- Sustained rage for >3 seconds — exhausting and cartoonish.
- Anger as default state — destroys dynamic. Let it *arrive*.

### Verify
- Top label: **annoyed → angry → enraged**
- Bar chart: anger dominant; disgust often second (shared AU 4 and 10)
- Circumplex dot: **top-left** (negative valence, high arousal)
- Plutchik dyad: *contempt* (anger + disgust) appears in cold, controlled anger
- AU overlay: **AU 4, 5, 7, 23**. AU 10 for the sneer.

---

## Fear

Apprehension through terror. Fear and surprise share AUs — the difference is
**duration** (surprise is brief, fear sustains) and **context** (surprise can
be positive; fear is always aversive).

### Facial signal (FACS)
**AU 1 + AU 2 + AU 4 + AU 5 + AU 20 + AU 26** — the canonical composite:
- **AU 1 + 2** Inner *and* outer brow raisers — the *entire* brow goes up
- **AU 4** Brow lowerer — brows pulled together *while* raised. Creates
  "horizontal wrinkles + vertical crease" (fear's signature)
- **AU 5** Upper lid raiser — whites visible above the iris
- **AU 20** Lip stretcher — lips pulled horizontally sideways (most people
  can't do this voluntarily)
- **AU 26/27** Jaw drop / mouth stretch — jaw falls open as intensity grows

**Fear vs surprise:** fear has AU 4 (brows together), surprise doesn't.
Fear has AU 20 (horizontal stretch), surprise has AU 27 (round open mouth).
**Fear vs sadness:** both have AU 1+4, but fear has AU 5 (wide eyes) while
sadness has AU 43 (droopy). Fear looks *up and out*; sadness *down and in*.

### Body & breath
Fear is the sympathetic nervous system on camera:
- Breath: held → short, shallow, fast. Freeze before flight.
- Eyes: wide, darting. Tracking exits.
- Skin: pales; may shine with sweat.
- Hands: up instinctively, or drawn close to body. Fine tremor.
- Voice: pitch up, volume down, breath ragged.
- Weight: backward, onto heels. Leaning away.

### Intensity tiers
| Tier | Word | What's happening |
|---|---|---|
| Low | apprehensive | AU 1+2+4 flickers. Scanning. Breath quickens |
| Mid | afraid | Full composite. Body still or trembling. Held breath |
| High | terrified | Add AU 27 (open mouth). Breath ragged. Tremor visible |

### Method approaches
**Memory route.** Don't go for big-trauma fear — sense-memory
**anticipatory** fear: waiting for a phone call with bad news, realizing
you're about to be caught in a lie, turbulence on a plane. Easier and
more truthful on camera.

**Body route.** *Psychological gesture:* arms cross protectively over
chest, head lowers slightly *but eyes stay up and wide*. Freeze, hold
breath, release. Also: **hyperventilate for 30 seconds** in a safe place —
AUs 1+2+5 appear naturally. Use sparingly.

**Action route.** Fear is usually attached to a protective objective:
- "To get to the door before he does"
- "To keep her from finding out"
- "To figure out if I'm about to die or not"

Play the calculation; the fear leaks through.

### Exercises
- **Startle ladder.** (1) Partner claps loudly without warning → note AUs
  (AU 1+2+5+26 — startle, which is surprise). (2) Partner tells you they
  heard a sound in your house → fear-proper develops: AU 4 joins. Stage 2
  is what we want on camera.
- **Slow-threat imagery.** Close eyes. Imagine a slow-motion threat
  approaching from peripheral vision. Open eyes at the moment of arrival.
  Face holds held-breath, wide-eyed, pulled-brow for ~2s.
- **Breath freeze.** Speak a line while holding breath its whole duration.
  Breath-starvation produces physiological fear cues even when the scene
  is neutral.

### Common pitfalls
- Eyes wide + flat brow → reads as surprise or ecstasy. Add AU 4.
- Shaking first — real fear freezes first, trembles after.
- Darting eyes everywhere — real fear often fixes on the threat with tiny
  micro-darts around it.
- Screaming early — fear is mostly silent at its most truthful.
- "Brave face"-ing it — hidden fear still needs the physiological signs.

### Verify
- Top label: **apprehensive → afraid → terrified**
- Bar chart: fear dominant; surprise usually second. If surprise tops fear,
  you're in startle — add AU 4 for sustained fear.
- Circumplex dot: **top-left** (negative valence, high arousal), but often
  more central on valence than anger
- Plutchik dyad: *awe* (fear + surprise) appears in dread tinged with wonder
- AU overlay: **AU 1, 2, 4, 5, 20** (if possible), **26**

---

## Surprise

Distraction through amazement. The shortest-lasting emotion — real surprise
peaks in about a second and is gone. Anything you sustain for longer is
something else (fear, shock, confusion) wearing surprise's mask.

### Facial signal (FACS)
**AU 1 + AU 2 + AU 5 + AU 26** — the clean surprise composite:
- **AU 1 + 2** — full brow goes straight up. **No AU 4** (no drawing
  together — that'd make it fear).
- **AU 5** Upper lid raiser — whites visible above the iris.
- **AU 26** Jaw drop — mouth opens, relaxed, lips in a loose "O"-ish shape.
  At high intensities → **AU 27** (full mouth stretch).

The *lack* of AU 4 separates surprise from fear. Pure surprise is also
**symmetric** — asymmetric brow raise reads as skepticism.

### Body & breath
- Breath: sudden sharp inhale (the gasp). Held briefly at the top.
- Head: jerks back slightly. Chin may rise.
- Eyes: focus hard on the source.
- Hands: may come up protectively or to the mouth ("oh!").
- Body: frozen for a half-second. Posture resets.

### Intensity tiers
| Tier | Word | What's happening |
|---|---|---|
| Low | distracted | Brief AU 1+2 flicker. Head turns. Eyes refocus |
| Mid | surprised | Full composite for ~1 second. Gasp. Jaw drop |
| High | amazed | AU 27 opens fully. "Wow" escapes |

### Method approaches
**Memory route.** Sense-memory the *moment of information arrival* — the
instant before you understood what you were seeing. The feeling is **the
jolt before the interpretation**.

**Body route.** Surprise is mostly breath-driven. Sharp audible inhale
through an open mouth; eyes and brows up on the inhale; freeze at the top.
Do this without emotion and the AUs appear.

**Action route.** Surprise isn't an objective — it's a **response** that
interrupts an objective. In rehearsal, have a partner deliver one piece of
unexpected text (unwritten) during the scene. Your genuine surprise to
*their* choice is what to capture.

### Exercises
- **One-second rule.** Hold surprise for exactly 1s then move on to another
  emotion. The move-on is the part actors forget. Held surprise reads as
  comedy.
- **Gasp drill.** Inhale sharply through an open mouth at the webcam. AUs
  1+2+5+26 should activate automatically. If not, you're holding tension in
  the brow.
- **"What is that" game.** Partner points somewhere unexpected and asks
  "what is that?". The first 0.5-1s of your turn is real surprise.

### Common pitfalls
- Holding the look too long — #1 surprise mistake. Decays fast.
- Brows together (AU 4) → becomes fear. Keep them *parallel*.
- No inhale → reads performative.
- Brows up, no jaw drop → reads as mild *interest*, not surprise.

### Verify
- Top label: **distracted → surprised → amazed**
- Bar chart: surprise dominant, usually followed by happiness (positive
  surprise) or fear (negative)
- Circumplex dot: **high arousal** (top), valence variable
- Plutchik dyads: *delight* (surprise + happiness), *awe* (surprise + fear),
  *disapproval* (surprise + sadness)
- AU overlay: **AU 1, 2, 5, 26**. **No AU 4** if pure surprise.

---

## Disgust

Disinterest through loathing. Almost purely physical — it evolved from the
food-rejection reflex. Your job is usually to **find the bad taste** in the
situation rather than indicate revulsion.

### Facial signal (FACS)
**AU 9 + AU 10 + AU 17 + AU 25/26** — canonical composite:
- **AU 9** Nose wrinkler — the "bunny nose". Upper lip and nose wrinkle
  upward. Hard to fake convincingly.
- **AU 10** Upper lip raiser — lip pulls up toward the nose, exposing
  upper teeth.
- **AU 17** Chin raiser — chin pushes up; lower lip may protrude.
- **AU 25/26** — mouth parts slightly; tongue retracts.

**Disgust vs contempt:** contempt is asymmetric (one-sided lip raise —
AU 14 or unilateral 12), disgust is symmetric.
**Disgust vs anger:** anger has AU 4 (brow down) + AU 23 (lips tight);
disgust has AU 9 + open-ish lips.

### Body & breath
Disgust is the body trying to reject something:
- Breath: exhale-heavy. Nose wrinkle closes the nostrils. Sometimes a gag.
- Head: turns *away* or pulls back. Never toward the source.
- Eyes: narrow (AU 7); sometimes close entirely at peak.
- Tongue: retracts. The mouth tastes something unpleasant.
- Shoulders: rise and protect.
- Hands: may come up to push away or cover the mouth.

### Intensity tiers
| Tier | Word | What's happening |
|---|---|---|
| Low | disinterested | Faint AU 9 + mild head-turn. Reads as boredom |
| Mid | disgusted | Full composite. Nose wrinkle visible. Exhale-sigh |
| High | loathing | AU 9+10+17+25 strong. Gagging reflex. Body recoiling |

### Method approaches
**Memory route.** **Sense-memory a specific bad taste or smell.** Don't try
to remember being disgusted — remember: food gone bad in the fridge, a
cleaning chemical spilled in a warm room, something you cleaned up you
wish you hadn't, a dentist's suction tool. Olfactory/gustatory memory is
the fastest route to the AUs.

**Body route.** *Psychological gesture:* hands push outward and down from
face, like sweeping something off a table, with an "ugh" exhale. Also:
touch your tongue to something slightly uncomfortable (raised tongue
pressing the palate, or a sour taste) — the body does disgust without you
asking.

**Action route.** Disgust is often a *moral* rejection, not literal:
- "To refuse to be in the same room with him"
- "To make her see how disgraceful this is"
- "To not touch this, ever"

Moral disgust produces the same AUs as food disgust — they share the
neural pathway.

### Exercises
- **Rotten fridge.** Imagine in detail opening a fridge that's been off for
  a week. The specific sweet-sour-rot smell. Narrate what you'd do. AUs
  fire automatically.
- **Moral disgust pivot.** Read a news story that genuinely offends you.
  Describe it to camera *without trying to show disgust*. The AUs appear
  as your honest reaction — truer than any technique.
- **Tongue retract.** Try to pull your upper lip up with your upper teeth
  (AU 10). Hold 5s. Add nose wrinkle (AU 9). Training muscles most people
  don't use.

### Common pitfalls
- Frowning instead of nose wrinkle → reads as anger or sad.
- Sticking tongue out → cartoony. Real disgust *retracts* the tongue.
- Sustained loathing — physically exhausting.
- Playing only the reaction when disgust is moral — body still reacts as
  if tasting something bad.
- Confusing with contempt — contempt is cooler, asymmetric, looks *down on*;
  disgust is hotter, symmetric, looks *away from*.

### Verify
- Top label: **disinterested → disgusted → loathing**
- Bar chart: disgust dominant; contempt often second. If contempt tops
  disgust, you're doing one-sided lip raise — symmetric for disgust.
- Circumplex dot: **left side** (negative valence). Low-arousal cold
  disgust → mid-left; high-arousal loathing → top-left.
- Plutchik dyad: *remorse* (sadness + disgust) — disgust at oneself
- AU overlay: **AU 9, 10, 17, 25**. Without AU 9 you don't have disgust.

---

## Contempt

The asymmetric emotion. The only emotion with a distinctive *one-sided*
facial signal — which is both what makes it readable on camera and what
makes it hard to fake. Cold where anger is hot, *looks down on* where
disgust *pushes away*.

### Facial signal (FACS)
**Unilateral AU 12 or AU 14** — the signature:
- **AU 14 Dimpler** — corner of the mouth pulls inward and slightly up,
  creating a dimple on *one side only*. The classic smirk.
- Or **one-sided AU 12** — smile-corner on one side only, with the other
  corner neutral.

Often combined with **AU 7** (lid tightener — cool assessment), **AU 10**
on the same side (partial sneer), and a slight **head tilt** upward — the
character is literally looking *down*.

Symmetric smirk (both corners) reads as amusement or smugness, not
contempt. Unilateral is what the model and humans key on.

### Body & breath
Contempt is quiet:
- Breath: normal, even; maybe a small nasal exhale ("tch" or silent).
- Head: tilted back and slightly away. Gaze from under lowered lids.
- Shoulders: relaxed, one may be higher.
- Hands: loose; sometimes a dismissive half-gesture.
- Voice: pitch drops; pace slows. Contempt doesn't raise its voice.
- Weight: back. Contempt pulls away while staying present.

### Intensity tiers
| Tier | Word | What's happening |
|---|---|---|
| Low | dismissive | Brief unilateral lip corner. Quick glance and look-away |
| Mid | contemptuous | Held smirk + AU 7. Still body. Silent |
| High | disdainful | Smirk + nasal exhale + slow shake of head |

### Method approaches
**Memory route.** Recall someone whose opinion you **stopped caring about**.
Not someone you hate — hate is anger. Someone whose *seriousness* you
couldn't take seriously anymore. The internal phrase is often *"oh, please"*.

**Body route.** *Psychological gesture:* one shoulder lifts and rolls back,
turning the body a quarter-turn away. Small nasal exhale. Head stays up.
The "I'm done here" gesture.

**Action route.**
- "To end this conversation without engaging"
- "To make her realize she isn't in my league"
- "To refuse to dignify this with a reply"

The key action-verb is often **to dismiss** — not to argue, not to refute.

### Exercises
- **Half-smile drill.** Pull only the *right* lip corner up. Hold 5s.
  Release. Switch sides. Most people have a dominant side — learn yours.
- **The audit.** Recall three things/people you find beneath your
  engagement. "Audit" each one mentally at the camera. Don't perform. If
  contempt appears at all, that's your honest contempt.
- **Silent reply.** Partner says something provocative. You reply *only
  with your face*. Forces honesty — can't hide behind words.

### Common pitfalls
- **Symmetric** smirk → smugness, not contempt. Asymmetry required.
- Angry-face as contempt → furrowed brow. Release AU 4.
- Open contempt (eyes wide, mouth open) → reads as disgust.
- Playing it cartoonishly — sitcom contempt is a wink. Film contempt is
  smaller and colder. If visible from the back of the room, too much.
- Sustained longer than 2–3 seconds → becomes mugging.

### Verify
- Top label: **dismissive → contemptuous → disdainful**
- Bar chart: contempt dominant; happiness often second (AU 12 is a smile-
  component). If happiness tops, your smile-corner is bilateral.
- Circumplex dot: **left side, middle-to-low arousal**. Top-left = anger,
  not contempt.
- AU overlay: **AU 14 on one side** (R14 or L14, not both), often with
  AU 7. Symmetric 14 ≈ amusement.

### A note on reading contempt in others
Ekman flagged contempt as uniquely universal *and* uniquely asymmetric —
most other emotions produce symmetric faces. Microexpressions of contempt
(quarter-second flashes) are considered particularly reliable signals in
behavioral analysis. If you catch yourself micro-flashing contempt in a
real conversation, it's worth asking what you actually think of the person.

---

## Neutral

The "no emotion" face, which is almost never actually neutral. Stillness is
the most demanding facial state to hold honestly — the camera catches every
twitch, and the *wrong* neutral reads as bored, lying, or dead-eyed.

### Facial signal (FACS)
No active AUs, or tiny fluctuations:
- Brow relaxed, not raised or lowered
- Eyes open at normal aperture, neither wide nor narrowed
- Lips closed softly, corners level
- Jaw relaxed but not slack
- Regular blinks (~every 3–5 seconds)

The goal is **soft tone everywhere** — not a dead face, but one not
committed to any emotional direction.

### Why "neutral" isn't really neutral
A *neutral* reading during a scene doesn't mean the character feels nothing
— it means the camera can't decide. Useful neutral happens when:
- The character is **thinking** (active mental state, low facial commitment)
- The character is **listening** (attention outward, self receded)
- The character is **concealing** (emotion is present but held behind the face)

### Body & breath
Neutral is **available**, not absent:
- Breath: steady, through the nose. Diaphragmatic, not high chest.
- Eyes: focused on a specific point or person. Unfocused eyes → daydreaming.
- Shoulders: down. Tension in shoulders always leaks into the face.
- Jaw: released. Teeth not touching. Tongue resting on the palate.
- Weight: balanced, centered. No leaning.

Tell of **fake** neutral: tension somewhere — tight jaw, frozen shoulder,
still eyes. Real neutral moves quietly: small eye adjustments, small breath
changes, soft micro-blinks.

### The three kinds of neutral to practice
**1. Thinking neutral — active inner life.** Still face, eyes working. Tiny
left/right flicks as the mind scans. Blinks slightly less frequent. How to
produce it: *actually think* about something (multiply in your head).

**2. Listening neutral — receptive.** Attention on the scene partner; self
quiet. Eyes track. Small nods. Blinks fall on beat with partner's pauses.
How to produce it: listen as if you'll have to repeat what was said.

**3. Concealing neutral — held emotion.** A small amount of jaw/eye tension
betrays effort. Occasional micro-expressions (quarter-second flashes of the
real emotion). Breath control that's *slightly* too even. You have to
actually play the hidden emotion inside and then *fail to fully suppress*
it — too-perfect suppression is fake.

### Exercises
- **60-second camera test.** Sit for a minute without a task. The tool will
  swing between neutral and small pulses as your face relaxes and
  re-engages. Note which emotions leak — that's your resting bias.
- **Receptive listening drill.** Listen to a podcast for 2 min as if you'll
  summarize. Record yourself. Compare to a take where you're *not*
  actually listening — the difference on the face is striking.
- **Micro-hold.** Pick a strong emotion. Feel it fully for 10s. Hold it
  *inside* while presenting a neutral face for another 10s. Residual AUs
  leak for 2–3s after the switch — realistic.

### Common pitfalls
- Dead-eye neutral (unfocused gaze) → absent, not neutral.
- Jaw-clenched neutral → reading shifts toward anger.
- Over-blinking → anxiety/lying. Normal is ~15/min in conversation.
- Smiling at rest (AU 12 bias) → reads as serene/happy. Many actors have
  this habit; the webcam surfaces it.
- Treating neutral as "do nothing" — it's an active receptive state.

### Verify
- Top label: **neutral**
- Bar chart: neutral dominant, ideally ≥60%. Runner-up reveals your bias.
- Circumplex dot: **near the center**, neither positive nor aroused.
- When playing **concealing neutral**, expect occasional flashes of the
  hidden emotion — that's not a bug, that's microexpressions doing their
  job. Good actors leak.

### A note on "resting face"
What's colloquially called "resting bitch face" or "resting sad face" is
just an AU bias at rest — some faces have anatomy that pulls toward AU 15
(corners down) or AU 4 (brow furrowed) even when relaxed. Can't fight
biology, but you can introduce **micro-motion** (occasional small smile,
brow-lift, head-tilt) to keep the face reading as *alive and neutral*
rather than committed to an emotion you don't mean.

---

## Blendshape → AU mapping reference

The webcam tool detects 52 ARKit-style **blendshapes** via MediaPipe and
aggregates them into FACS Action Units for the on-screen AU panel. This is
the mapping used:

| AU | Blendshapes (averaged when multiple) |
|---|---|
| AU 1 Inner brow raiser | `browInnerUp` |
| AU 2 Outer brow raiser | `browOuterUpLeft`, `browOuterUpRight` |
| AU 4 Brow lowerer | `browDownLeft`, `browDownRight` |
| AU 5 Upper lid raiser | `eyeWideLeft`, `eyeWideRight` |
| AU 6 Cheek raiser | `cheekSquintLeft`, `cheekSquintRight` |
| AU 7 Lid tightener | `eyeSquintLeft`, `eyeSquintRight` |
| AU 9 Nose wrinkler | `noseSneerLeft`, `noseSneerRight` |
| AU 10 Upper lip raiser | `mouthUpperUpLeft`, `mouthUpperUpRight` |
| AU 12 Lip corner puller | `mouthSmileLeft`, `mouthSmileRight` |
| AU 12L / AU 12R | `mouthSmileLeft` only / `mouthSmileRight` only |
| AU 14 Dimpler | `mouthDimpleLeft`, `mouthDimpleRight` |
| AU 14L / AU 14R | `mouthDimpleLeft` / `mouthDimpleRight` (for contempt) |
| AU 15 Lip corner depressor | `mouthFrownLeft`, `mouthFrownRight` |
| AU 17 Chin raiser | `mouthShrugUpper` |
| AU 20 Lip stretcher | `mouthStretchLeft`, `mouthStretchRight` |
| AU 23 Lip tightener | `mouthPressLeft`, `mouthPressRight` |
| AU 25/26 Jaw drop | `jawOpen` (thresholded by magnitude) |
| AU 43 Eyes closed | `eyeBlinkLeft`, `eyeBlinkRight` |

Caveats:
- Blendshapes are a proxy for true FACS. They're calibrated for 3D avatars,
  not for coders-of-FACS precision. But for performance feedback they're
  plenty accurate enough to tell "the AU recipe is in the ballpark" vs
  "you're doing something else entirely."
- **Asymmetry detection** (important for contempt) works because blendshapes
  are per-side — if `mouthDimpleLeft - mouthDimpleRight` is large, that's
  asymmetric and flagged as AU 14L or AU 14R.
- The overlay shows AUs that are active at ≥ threshold (default 0.25).
  Tweak `AU_DISPLAY_THRESHOLD` in `webcam_emotion.py` if the panel is too
  empty or too busy.
