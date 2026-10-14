# Actor Coach

Real-time facial-emotion practice for the webcam. Show an emotion, get scored
on whether the model *and* your Facial Action Units agree.

Built with:
- **HSEmotion** (AffectNet ENet-B0 ONNX) — 8-class emotion + valence/arousal
- **MediaPipe FaceLandmarker** — face detection, 52 blendshapes → FACS AUs,
  gaze, and head pose (tilt / chin up-down / turn)
- **OpenCV** — webcam + overlay rendering
- Runs real-time on Apple Silicon via Metal/XNNPACK

## Emotions

Two layers:

- **7 core classes** the classifier sees directly — Happiness, Sadness, Anger,
  Fear, Surprise, Disgust, Contempt.
- **16 emotion-wheel targets** scored from published FACS recipes plus head
  pose and gaze, gated by the classifier's valence — Curious, Excited, Amused,
  Content, Proud, Loving, Awe, Relieved, Bored, Confused, Embarrassed, Ashamed,
  Sympathetic, Pain, Coy, Anxious.

The recipes come from Cordaro et al. 2018 (22 emotions × 5 cultures), Keltner
et al. 2019, and Shiota et al. 2003 — see the wheel section of
[`guides.md`](guides.md) for the AUs, sources, and how each maps onto
Plutchik's wheel and the Willcox feelings wheel.

## Modes

- **Classic Simon** — random core-emotion prompt, 5s to hit it, one miss ends the run
- **Practice** — pick any of the 23 emotions and drill it endlessly
- **Freeplay / Mirror** — live emotion bars, Russell circumplex, active AUs,
  head pose + gaze readout, and the closest wheel emotion
- **Wheel Simon** — classic rules, prompts drawn from all 23 (head pose counts)

See [`guides.md`](guides.md) for the acting/FACS recipes behind each emotion,
and [`CUSTOMIZE.md`](CUSTOMIZE.md) for how to edit the GUI or add an emotion.

## Setup

Tested on macOS (Apple Silicon) with Python 3.11.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Download the MediaPipe FaceLandmarker model
mkdir -p models
curl -L 'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task' \
  -o models/face_landmarker.task
```

The HSEmotion ONNX model downloads itself on first run to `~/.hsemotion/`.

## Run

```bash
./run.sh            # default camera (index 0)
./run.sh 1          # camera index 1
./run.sh --list     # probe camera indices 0..5
```

`run.sh` is a thin wrapper around `.venv/bin/python actor_coach.py` that also
repairs the venv if Homebrew has swapped in a `python@3.13` whose `pyexpat`
can't load (that breaks `import mediapipe`).

Keys:
- `1` / `2` / `3` / `4` at the menu — pick a mode
- `b` — back to menu (from any sub-mode)
- `1`-`7` (core) and `a`-`s` (wheel) — pick an emotion; also switches
  mid-practice. The pick screen shows each emotion's key.
- `q` — quit
- `r` — restart after game over

If macOS asks for camera permission and you see "not authorized to capture
video", grant the requesting app access in **System Settings → Privacy &
Security → Camera**, fully quit and relaunch it, then run again.

## Repo layout

```
.
├── actor_coach.py       # main app with mode menu
├── emotion_lib.py       # shared inference + analysis helpers
├── guides.md            # per-emotion acting guides tied to FACS AUs
├── CUSTOMIZE.md         # how to edit the GUI
├── requirements.txt
└── models/              # MediaPipe .task file (gitignored)
```

## Credits

- HSEmotion — Andrey Savchenko, HSE University
  ([GitHub](https://github.com/HSE-asavchenko/face-emotion-recognition))
- MediaPipe FaceLandmarker — Google
  ([docs](https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker))
- FACS — Paul Ekman & Wallace Friesen
