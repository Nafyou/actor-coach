"""Real-time webcam emotion detection on Apple Silicon (M-series).

Stack:
  - HSEmotion (enet_b0_8_va_mtl, ONNX) -> 8 emotion classes + valence/arousal
  - MediaPipe FaceLandmarker (Metal/XNNPACK) -> face detection + 52 blendshapes
  - Blendshapes aggregated into FACS Action Units for actor-facing feedback

See guides.md for the AU recipes per emotion.

Run:  .venv/bin/python webcam_emotion.py 1          # camera index 1 (default 0)
      .venv/bin/python webcam_emotion.py --list     # probe indices 0..5
Quit: 'q' in the preview window.
"""
import sys
import urllib.request  # noqa: F401  # hsemotion_onnx has a missing-import bug

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
from hsemotion_onnx.facial_emotions import HSEmotionRecognizer

# --- tuning ---------------------------------------------------------------
DETECT_EVERY_N = 2          # HSEmotion frequency (MediaPipe runs every frame)
FACE_PAD = 0.15             # pad the face crop by % of box edge before emotion inference
AU_DISPLAY_THRESHOLD = 0.25 # blendshape score required to list an AU
AU_ASYMMETRY_THRESHOLD = 0.20  # |L - R| required to flag AU 12L/R or AU 14L/R

FACE_LANDMARKER_TASK = "models/face_landmarker.task"

# --- color palette --------------------------------------------------------
BOX = (0, 255, 0)
BAR_BG = (60, 60, 60)
BAR_FG = (0, 200, 255)
TEXT = (255, 255, 255)
AXIS = (180, 180, 180)
AU_COLOR = (140, 230, 255)

# --- label tables ---------------------------------------------------------
INTENSITY_TIERS = {
    "Anger":     ("annoyed",       "angry",         "enraged"),
    "Contempt":  ("dismissive",    "contemptuous",  "disdainful"),
    "Disgust":   ("disinterested", "disgusted",     "loathing"),
    "Fear":      ("apprehensive",  "afraid",        "terrified"),
    "Happiness": ("serene",        "happy",         "ecstatic"),
    "Neutral":   ("neutral",       "neutral",       "neutral"),
    "Sadness":   ("pensive",       "sad",           "grieving"),
    "Surprise":  ("distracted",    "surprised",     "amazed"),
}

DYADS = {
    frozenset(["Happiness", "Surprise"]): "delight",
    frozenset(["Fear",      "Surprise"]): "awe",
    frozenset(["Surprise",  "Sadness"]):  "disapproval",
    frozenset(["Sadness",   "Disgust"]):  "remorse",
}
DYAD_MIN_TOP = 0.30
DYAD_MIN_SEC = 0.20

# Map FACS AU -> list of (blendshape name(s), aggregation).
# "avg": average the listed blendshapes. Side-specific AUs handled separately below.
AU_FROM_BLENDSHAPES = {
    "AU1  inner brow raise":  (["browInnerUp"], "avg"),
    "AU2  outer brow raise":  (["browOuterUpLeft", "browOuterUpRight"], "avg"),
    "AU4  brow lowerer":      (["browDownLeft", "browDownRight"], "avg"),
    "AU5  upper lid raiser":  (["eyeWideLeft", "eyeWideRight"], "avg"),
    "AU6  cheek raiser":      (["cheekSquintLeft", "cheekSquintRight"], "avg"),
    "AU7  lid tightener":     (["eyeSquintLeft", "eyeSquintRight"], "avg"),
    "AU9  nose wrinkler":     (["noseSneerLeft", "noseSneerRight"], "avg"),
    "AU10 upper lip raiser":  (["mouthUpperUpLeft", "mouthUpperUpRight"], "avg"),
    "AU12 lip corner puller": (["mouthSmileLeft", "mouthSmileRight"], "avg"),
    "AU14 dimpler":           (["mouthDimpleLeft", "mouthDimpleRight"], "avg"),
    "AU15 lip corner down":   (["mouthFrownLeft", "mouthFrownRight"], "avg"),
    "AU17 chin raiser":       (["mouthShrugUpper"], "avg"),
    "AU20 lip stretcher":     (["mouthStretchLeft", "mouthStretchRight"], "avg"),
    "AU23 lip tightener":     (["mouthPressLeft", "mouthPressRight"], "avg"),
    "AU26 jaw drop":          (["jawOpen"], "avg"),
    "AU43 eyes closed":       (["eyeBlinkLeft", "eyeBlinkRight"], "avg"),
}


# --- helpers --------------------------------------------------------------
def intensity_label(cls: str, prob: float) -> str:
    tiers = INTENSITY_TIERS.get(cls, (cls, cls, cls))
    if prob < 0.50:
        return tiers[0]
    if prob < 0.80:
        return tiers[1]
    return tiers[2]


def describe(class_probs: dict) -> tuple[str, str]:
    ranked = sorted(class_probs.items(), key=lambda kv: kv[1], reverse=True)
    (top, top_p), (second, second_p) = ranked[0], ranked[1]
    base = f"{top.lower()} {top_p * 100:.0f}%"
    if top_p >= DYAD_MIN_TOP and second_p >= DYAD_MIN_SEC:
        dyad = DYADS.get(frozenset([top, second]))
        if dyad is not None:
            return dyad, f"{top.lower()}+{second.lower()}"
    return intensity_label(top, top_p), base


def face_bbox_from_landmarks(landmarks, frame_w: int, frame_h: int, pad: float = FACE_PAD):
    xs = [lm.x for lm in landmarks]
    ys = [lm.y for lm in landmarks]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    w = x1 - x0
    h = y1 - y0
    x0 -= w * pad
    x1 += w * pad
    y0 -= h * pad
    y1 += h * pad
    return (
        max(0, int(x0 * frame_w)),
        max(0, int(y0 * frame_h)),
        min(frame_w - 1, int(x1 * frame_w)),
        min(frame_h - 1, int(y1 * frame_h)),
    )


def blendshapes_to_dict(blendshapes_list) -> dict:
    return {b.category_name: float(b.score) for b in blendshapes_list}


def compute_active_aus(bs: dict) -> list:
    """Return [(label, score)] for AUs at or above the display threshold."""
    active = []
    for au_label, (names, _mode) in AU_FROM_BLENDSHAPES.items():
        scores = [bs.get(n, 0.0) for n in names]
        val = sum(scores) / len(scores) if scores else 0.0
        if val >= AU_DISPLAY_THRESHOLD:
            active.append((au_label, val))

    # Asymmetry checks — important for contempt (AU 14L/R) and unilateral AU 12L/R.
    lr_pairs = [
        ("AU12L lip corner (L)", "AU12R lip corner (R)", "mouthSmileLeft",  "mouthSmileRight"),
        ("AU14L dimpler (L)",    "AU14R dimpler (R)",    "mouthDimpleLeft", "mouthDimpleRight"),
    ]
    for left_label, right_label, left_name, right_name in lr_pairs:
        left_val = bs.get(left_name, 0.0)
        right_val = bs.get(right_name, 0.0)
        if abs(left_val - right_val) >= AU_ASYMMETRY_THRESHOLD:
            if left_val > right_val:
                active.append((left_label, left_val))
            else:
                active.append((right_label, right_val))

    active.sort(key=lambda t: t[1], reverse=True)
    return active[:8]  # top-8 to fit on screen


# --- drawing --------------------------------------------------------------
def draw_bars(frame, probs: dict, origin=(10, 30)):
    x0, y0 = origin
    bar_w, bar_h, gap = 160, 14, 4
    for i, (name, p) in enumerate(sorted(probs.items(), key=lambda kv: kv[1], reverse=True)):
        y = y0 + i * (bar_h + gap)
        cv2.rectangle(frame, (x0, y), (x0 + bar_w, y + bar_h), BAR_BG, -1)
        filled = int(bar_w * max(0.0, min(p, 1.0)))
        cv2.rectangle(frame, (x0, y), (x0 + filled, y + bar_h), BAR_FG, -1)
        cv2.putText(frame, f"{name:<10}{p * 100:5.1f}%", (x0 + 4, y + bar_h - 3),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, TEXT, 1, cv2.LINE_AA)


def draw_circumplex(frame, valence: float, arousal: float, radius: int = 60):
    _, w = frame.shape[:2]
    cx = w - radius - 20
    cy = radius + 30
    cv2.circle(frame, (cx, cy), radius, AXIS, 1)
    cv2.line(frame, (cx - radius, cy), (cx + radius, cy), AXIS, 1)
    cv2.line(frame, (cx, cy - radius), (cx, cy + radius), AXIS, 1)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, "excited", (cx - 22, cy - radius - 4), font, 0.35, AXIS, 1, cv2.LINE_AA)
    cv2.putText(frame, "calm",    (cx - 14, cy + radius + 12), font, 0.35, AXIS, 1, cv2.LINE_AA)
    cv2.putText(frame, "neg",     (cx - radius - 22, cy + 4), font, 0.35, AXIS, 1, cv2.LINE_AA)
    cv2.putText(frame, "pos",     (cx + radius + 4, cy + 4), font, 0.35, AXIS, 1, cv2.LINE_AA)
    v = max(-1.0, min(1.0, float(valence)))
    a = max(-1.0, min(1.0, float(arousal)))
    cv2.circle(frame, (int(cx + v * radius), int(cy - a * radius)), 5, BAR_FG, -1)
    cv2.putText(frame, f"v={v:+.2f} a={a:+.2f}", (cx - radius, cy + radius + 28),
                font, 0.4, TEXT, 1, cv2.LINE_AA)


def draw_aus(frame, active_aus: list):
    if not active_aus:
        return
    h = frame.shape[0]
    x0, y0 = 10, h - 20 - len(active_aus) * 18
    cv2.putText(frame, "Active AUs", (x0, y0 - 6),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, TEXT, 1, cv2.LINE_AA)
    for i, (label, val) in enumerate(active_aus):
        y = y0 + (i + 1) * 18 - 4
        cv2.putText(frame, f"{label} {val:.2f}", (x0, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, AU_COLOR, 1, cv2.LINE_AA)


def probe_cameras(max_index: int = 5) -> None:
    print(f"Probing camera indices 0..{max_index} (AVFoundation)...")
    for i in range(max_index + 1):
        c = cv2.VideoCapture(i, cv2.CAP_AVFOUNDATION)
        ok = c.isOpened()
        frame_ok = False
        if ok:
            frame_ok, _ = c.read()
        c.release()
        print(f"  index {i}: opened={ok}, frame_read={frame_ok}")
    print("Pick an index that shows frame_read=True and rerun: .venv/bin/python webcam_emotion.py <index>")


# --- main -----------------------------------------------------------------
if len(sys.argv) > 1 and sys.argv[1] == "--list":
    probe_cameras()
    sys.exit(0)

camera_index = int(sys.argv[1]) if len(sys.argv) > 1 else 0

print("Loading HSEmotion + MediaPipe FaceLandmarker...")
recognizer = HSEmotionRecognizer(model_name="enet_b0_8_va_mtl")
landmarker = mp_vision.FaceLandmarker.create_from_options(
    mp_vision.FaceLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=FACE_LANDMARKER_TASK),
        output_face_blendshapes=True,
        output_facial_transformation_matrixes=False,
        num_faces=1,
        running_mode=mp_vision.RunningMode.VIDEO,
    )
)

cap = cv2.VideoCapture(camera_index, cv2.CAP_AVFOUNDATION)
if not cap.isOpened():
    raise SystemExit(
        f"Could not open webcam (index {camera_index}). "
        "Try: .venv/bin/python webcam_emotion.py --list"
    )
print(f"Using camera index {camera_index}. Press 'q' in the preview window to quit.")

frame_idx = 0
last_emotion = None  # (nuanced, base, probs, valence, arousal)

while True:
    ok, frame = cap.read()
    if not ok:
        break
    frame = cv2.flip(frame, 1)
    h, w = frame.shape[:2]

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC)) or (frame_idx * 33)
    lm_result = landmarker.detect_for_video(mp_img, timestamp_ms)

    active_aus = []
    bbox = None
    if lm_result.face_landmarks:
        landmarks = lm_result.face_landmarks[0]
        bbox = face_bbox_from_landmarks(landmarks, w, h)
        if lm_result.face_blendshapes:
            bs = blendshapes_to_dict(lm_result.face_blendshapes[0])
            active_aus = compute_active_aus(bs)

    # HSEmotion runs at lower frequency to save CPU
    if bbox is not None and frame_idx % DETECT_EVERY_N == 0:
        try:
            x0, y0, x1, y1 = bbox
            face_bgr = frame[y0:y1, x0:x1]
            if face_bgr.size > 0:
                face_rgb = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2RGB)
                _label, scores = recognizer.predict_emotions(face_rgb, logits=False)
                class_probs = {recognizer.idx_to_class[i]: float(scores[i])
                               for i in range(len(recognizer.idx_to_class))}
                valence, arousal = float(scores[-2]), float(scores[-1])
                nuanced, base = describe(class_probs)
                last_emotion = (nuanced, base, class_probs, valence, arousal)
        except Exception as e:
            print(f"emotion error: {e}")

    # draw
    if bbox is not None:
        x0, y0, x1, y1 = bbox
        cv2.rectangle(frame, (x0, y0), (x1, y1), BOX, 2)
        if last_emotion is not None:
            nuanced, base, *_ = last_emotion
            cv2.putText(frame, nuanced, (x0, max(y0 - 28, 22)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, BOX, 2, cv2.LINE_AA)
            cv2.putText(frame, base, (x0, max(y0 - 8, 42)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, BOX, 1, cv2.LINE_AA)

    if last_emotion is not None:
        _, _, probs, v, a = last_emotion
        draw_bars(frame, probs)
        draw_circumplex(frame, v, a)

    draw_aus(frame, active_aus)

    cv2.imshow("Emotion + AUs (press q to quit)", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
    frame_idx += 1

cap.release()
cv2.destroyAllWindows()
