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
    ("1", "Classic Simon",             "Random prompt. 5s to hit. One miss = game over."),
    ("2", "Practice a single emotion", "Pick one. Drill it until you quit."),
    ("3", "Freeplay / Mirror",         "Just show what the model sees on you."),
    ("q", "Quit",                      ""),
]
```

To add a new mode: add a row here, add a new `S_*` state constant, handle it
in the main `if app["mode"] == ...` chain, and add a key branch in the
`S_MENU` block that switches to it.

`draw_main_menu` controls the look — title size, spacing, and colors are all
there. It's ~15 lines.

## 3. Per-emotion hints

`TARGET_HINTS` is defined in [`emotion_lib.py`](emotion_lib.py). Edit the
text there to change what shows up under the prompt ("brows up, eyes wide,
jaw drop", etc.). Keep them short — they render on one line.

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

The model outputs a fixed 8 classes — you can't *add* an emotion to
detection. But you can:

- Add a **derived label** by combining existing classes. Example: define
  "frustrated" as Anger ≥ 0.3 AND Disgust ≥ 0.2. Add a branch in `describe`
  that checks this combo before falling back to `intensity_label`.
- Add a new **target phrase** for practice mode. Drop an entry into
  `TARGET_BLENDSHAPES` with the AU recipe and `TARGET_HINTS` with the copy.
  The target dropdown will pick it up via `EMOTION_TARGETS` — just add the
  name to that list too.

## 11. Where inference lives

You probably don't need to touch this, but for completeness:

- `emotion_lib.analyze_frame` runs both models and returns a dict with
  `bbox`, `class_probs`, `valence`, `arousal`, `blendshapes`.
- `emotion_lib.compute_active_aus` turns blendshapes into active AUs.
- `emotion_lib.target_match` does the game's scoring logic.

To swap the emotion model (e.g. `enet_b2_8` for higher accuracy, slower),
edit the `HSEmotionRecognizer(model_name=...)` call in `emotion_lib.load_models`.
Note: `enet_b2_8` does **not** output valence/arousal — the circumplex will
stop working.
