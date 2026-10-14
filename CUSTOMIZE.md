# Customizing the GUI

The whole UI is rendered with OpenCV calls (`cv2.putText`, `cv2.rectangle`,
`cv2.circle`, etc.) inside [`actor_coach.py`](actor_coach.py). There's no web
layer or CSS — editing the GUI means editing Python.

This guide tells you where each piece lives so you can tweak without
spelunking.

## 1. Colors

All colors are BGR tuples at the top of `actor_coach.py` (around lines 32–42).

| Constant | Used for |
|---|---|
| `BG_OVERLAY` | Translucent strip behind menus and flash messages |
| `TEXT` | Default white body text |
| `MUTED` | Descriptions, hints, axis labels, "Esc back" footer |
| `ACCENT` | Key-binding hints and small callouts |
| `GREEN` | Success flash, healthy countdown bar |
| `RED` | Missed-round flash, low-time countdown |
| `AMBER` | Prompt "SHOW:" label, mid-time countdown |
| `BAR_BG` | Background track for the emotion bars |
| `BAR_FG` | Fill of the emotion bars / circumplex dot |
| `AU_COLOR` | Text color of the active AU list |
| `BOX` | Face bounding box in freeplay |

Change these and every call that references them updates automatically.
OpenCV uses **BGR** (blue, green, red) — not RGB. If you paste a hex color
from a design tool, convert it (`#FFC857` → `(87, 200, 255)`).

## 2. Menu layout and copy

The main menu entries are in the `MAIN_MENU` list. Each row is
`(key, name, description)`:

```python
MAIN_MENU = [
    ("1", "Classic Simon",             "Random prompt from the 7 core emotions. ..."),
    ("2", "Practice a single emotion", "Pick any of the 23. Drill it until you quit."),
    ("3", "Freeplay / Mirror",         "Live classes, AUs, head pose, and closest wheel emotion."),
    ("4", "Wheel Simon",               "Classic rules, all 23 emotions. Head pose counts. Hard."),
    ("q", "Quit",                      ""),
]
```

The emotion pick screen (`draw_pick_menu`) lays `ALL_TARGETS` out in two
columns and labels each with its key from `KEY_FOR_TARGET`. Keys are assigned
in `emotion_lib.TARGET_KEYS` (`1`-`7` core, then `a`-`s` skipping `b`/`q`).

To add a new mode: add a row here, add a new `S_*` state constant, handle it
in the main `if app["mode"] == ...` chain, and add a key branch in the
`S_MENU` block that switches to it.

`draw_main_menu` controls the look — title size, spacing, and colors are all
there. It's ~15 lines.

## 3. Per-emotion hints

`TARGET_HINTS` is defined in [`emotion_lib.py`](emotion_lib.py) for all 23
targets. Edit the text there to change what shows up under the prompt ("brows
up, eyes wide, jaw drop", etc.). Keep them short — they render on one line,
and on the pick screen they're truncated by the column width.

## 4. Game difficulty knobs

Near the top of `actor_coach.py`:

```python
CLASS_PROB_THRESHOLD = 0.35    # min P(target) for a hit
AU_FRACTION_THRESHOLD = 0.50   # fraction of target AUs that must be active
HOLD_DURATION = 0.25           # seconds the match must sustain
ROUND_TIMEOUT = 5.0            # seconds per classic-mode round
READY_DURATION = 1.0           # pause between classic rounds
FLASH_DURATION = 1.0           # how long the +1 / missed banner lingers
```

Raise `CLASS_PROB_THRESHOLD` or `AU_FRACTION_THRESHOLD` for a harder game.
Lower them when building a demo where you want generous scoring.

Wheel targets have their own `min_frac` inside `WHEEL_SPECS` (how many of the
recipe's soft cues must be present), and the head-pose cues read these
constants in `emotion_lib.py`:

```python
HEAD_TILT_DEG = 8.0      # ear toward shoulder
HEAD_PITCH_DEG = 8.0     # chin up / chin down
HEAD_TURN_DEG = 10.0     # head turned
GAZE_THRESHOLD = 0.30    # eyeLook* level that counts as a gaze shift
```

If your camera sits off-axis (laptop on a desk, you looking down at it) the
freeplay head readout will show a resting chin-down of several degrees. Raise
`HEAD_PITCH_DEG` or tilt the camera up to compensate.

## 5. Per-emotion difficulty (advanced)

Currently every target uses the same thresholds. Some emotions (sad, disgust,
contempt) are genuinely harder for the model to detect than happy or surprise.
To give each emotion its own bar, replace the constants with a dict:

```python
# in actor_coach.py
PER_EMOTION = {
    "Happiness": {"prob": 0.45, "au": 0.50},
    "Sadness":   {"prob": 0.30, "au": 0.50},
    # ...
}
```

Then in `match_progress` pull the numbers from `PER_EMOTION[target]` instead
of the globals.

## 6. HUD panels in Freeplay

Three draw functions control the mirror mode:

- `draw_bars` — the 8 emotion probability bars, top-left.
  - `bar_w`, `bar_h`, `gap` control the size.
  - Sort order is by probability; change `sorted(..., reverse=True)` to fix
    the class order if you want them locked.
- `draw_circumplex` — Russell's valence/arousal disc, top-right.
  - `radius` controls the circle size.
  - Labels are `"excited", "calm", "neg", "pos"` — change those strings
    freely.
- `draw_aus` — active-AU list, bottom-left.
  - `AU_DISPLAY_THRESHOLD` (in `emotion_lib.py`) controls when an AU is
    considered "active".
  - `active[:8]` in `compute_active_aus` caps the list; raise/lower it to
    show more or fewer.
- `draw_head_and_wheel` — head pose (chin/tilt/turn in degrees), gaze, and
  the closest of the 23 targets with its match %, top-center. Goes green
  with `MATCH` when that target would score in game mode. Pass a `targets=`
  subset to `best_wheel_match` if you only want the wheel emotions ranked.

## 7. Prompt HUD (Classic + Practice)

`draw_prompt_hud` renders the target word, hint, countdown bar, score, and
match-progress bar. Notable tweaks:

- The big target uses `scale=1.6, thickness=3` — bump up for bigger text.
- Countdown color flips at `time_left > 2` (green), `> 1` (amber), else red.
  Adjust those cutoffs to change when the countdown goes orange/red.
- The match bar sits at `my = 150`. Move it if you enlarge the title strip.

## 8. Camera + window size

The window is fixed at whatever resolution your webcam returns. To force a
different size, modify `open_camera` in `emotion_lib.py`:

```python
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
```

Not every camera honors every resolution — OpenCV silently picks the nearest
supported mode.

## 9. Flip / mirror

`frame = cv2.flip(frame, 1)` in the main loop mirrors the camera so your
movements feel natural. Remove this line if you want "true" orientation
(faces appear reversed to the actor, which is occasionally useful for
training asymmetry awareness).

## 10. Adding a new emotion

The classifier outputs a fixed 8 classes — you can't add a class to
detection. Wheel emotions are instead **recipes** in `emotion_lib.WHEEL_SPECS`,
scored from blendshapes, head pose, and gaze, with the classifier used only as
a valence gate. To add one, append an entry:

```python
"Skeptical": dict(
    wheel="where it sits on the wheel (for the guide)",
    family=["Neutral", "Contempt"],          # any of these must clear CLASS_PROB_THRESHOLD
    soft=[("au", ["mouthPressLeft", "mouthPressRight"]),
          ("au", ["eyeSquintLeft", "eyeSquintRight"])],
    hard=[("asym", ("browOuterUpLeft", "browOuterUpRight"), 0.20)],  # one brow up
    min_frac=0.5,                            # fraction of soft cues required
),
```

Cue vocabulary (see the comment above `WHEEL_SPECS`):

| Cue | Passes when |
|---|---|
| `("au", [names])` | any listed blendshape ≥ `AU_DISPLAY_THRESHOLD`; `(name, thr)` overrides the threshold per blendshape |
| `("not", [names])` | all listed blendshapes below threshold |
| `("tilt", deg)` / `("turn", deg)` | head roll / yaw magnitude ≥ deg |
| `("chin_up", deg)` / `("chin_down", deg)` | head pitch ≥ deg / ≤ −deg |
| `("gaze", "down" \| "up" \| "averted", thr)` | eyeLook* level ≥ thr |
| `("asym", (left, right), thr)` | left/right blendshape difference ≥ thr |
| `("any", [cues])` | at least one sub-cue passes |

`hard` cues must all pass; `soft` cues must reach `min_frac`. Then add a
line to `TARGET_HINTS`, and it appears on the pick screen, in Practice, in
Wheel Simon, and in the freeplay "closest" readout automatically (keys come
from `TARGET_KEYS` — extend the key string there if you run out). Document the
AU recipe and its source in `guides.md`.

For a **derived label** in freeplay (e.g. "frustrated" = Anger ≥ 0.3 AND
Disgust ≥ 0.2), add a branch in `describe` before it falls back to
`intensity_label`, or add the pair to `DYADS`.

## 11. Where inference lives

You probably don't need to touch this, but for completeness:

- `emotion_lib.analyze_frame` runs both models and returns a dict with
  `bbox`, `class_probs`, `valence`, `arousal`, `blendshapes`, `head`
  (`pitch`/`yaw`/`roll` in degrees, from MediaPipe's facial transformation
  matrix) and `gaze` (`down`/`up`/`averted`, 0..1).
- `emotion_lib.compute_active_aus` turns blendshapes into active AUs.
- `emotion_lib.match_score` does the game's scoring logic for any target
  (core or wheel); `best_wheel_match` ranks all targets for freeplay.

To swap the emotion model (e.g. `enet_b2_8` for higher accuracy, slower),
edit the `HSEmotionRecognizer(model_name=...)` call in `emotion_lib.load_models`.
Note: `enet_b2_8` does **not** output valence/arousal — the circumplex will
stop working.
