# Actor Coach

Real-time facial-emotion practice for the webcam. Show an emotion, get scored
on whether the model *and* your Facial Action Units agree.

Built with:
- **HSEmotion** (AffectNet ENet-B0 ONNX) — 8-class emotion + valence/arousal
- **MediaPipe FaceLandmarker** — face detection + 52 blendshapes → FACS AUs
- **OpenCV** — webcam + overlay rendering
- Runs real-time on Apple Silicon via Metal/XNNPACK

## Modes

- **Classic Simon** — random emotion prompt, 5s to hit it, one miss ends the run
- **Practice** — pick a single emotion and drill it endlessly
- **Freeplay / Mirror** — live emotion bars, Russell circumplex, and active AUs

See [`guides.md`](guides.md) for the acting/FACS recipes behind each emotion,
and [`CUSTOMIZE.md`](CUSTOMIZE.md) for how to edit the GUI.

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
.venv/bin/python actor_coach.py           # default camera (index 0)
.venv/bin/python actor_coach.py 1         # camera index 1
.venv/bin/python actor_coach.py --list    # probe camera indices 0..5
```

Keys:
- `1` / `2` / `3` at the menu — pick a mode
- `Esc` — back to menu (from any sub-mode)
- `q` — quit
- `r` — restart after classic-mode game over

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
