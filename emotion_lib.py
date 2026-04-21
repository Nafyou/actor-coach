"""Shared inference + analysis helpers for the webcam emotion tools.

Two scripts use this:
  - webcam_emotion.py  (the mirror/viewer)
  - emotion_simon.py   (the game with modes)

The goal of this file is to keep inference, AU computation, and emotion
labeling in one place so the UI scripts only have to render.
"""
from __future__ import annotations

import urllib.request  # noqa: F401 — hsemotion_onnx package has a missing-import bug

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
from hsemotion_onnx.facial_emotions import HSEmotionRecognizer

# --- constants the UIs reuse ---------------------------------------------
FACE_LANDMARKER_TASK = "models/face_landmarker.task"
FACE_PAD = 0.15
AU_DISPLAY_THRESHOLD = 0.25
AU_ASYMMETRY_THRESHOLD = 0.20

# The 7 acting-relevant emotion classes (Neutral excluded from game targets).
EMOTION_TARGETS = ["Happiness", "Sadness", "Anger", "Fear", "Surprise", "Disgust", "Contempt"]
ALL_EMOTIONS = EMOTION_TARGETS + ["Neutral"]

# Plutchik-style intensity tiers per HSE class label.
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

# Plutchik dyads computable from HSE's 8-class output.
DYADS = {
    frozenset(["Happiness", "Surprise"]): "delight",
    frozenset(["Fear",      "Surprise"]): "awe",
    frozenset(["Surprise",  "Sadness"]):  "disapproval",
    frozenset(["Sadness",   "Disgust"]):  "remorse",
}
DYAD_MIN_TOP = 0.30
DYAD_MIN_SEC = 0.20

# FACS AU -> blendshape names (averaged across the listed names).
AU_FROM_BLENDSHAPES = {
    "AU1  inner brow raise":  ["browInnerUp"],
    "AU2  outer brow raise":  ["browOuterUpLeft", "browOuterUpRight"],
    "AU4  brow lowerer":      ["browDownLeft", "browDownRight"],
    "AU5  upper lid raiser":  ["eyeWideLeft", "eyeWideRight"],
    "AU6  cheek raiser":      ["cheekSquintLeft", "cheekSquintRight"],
    "AU7  lid tightener":     ["eyeSquintLeft", "eyeSquintRight"],
    "AU9  nose wrinkler":     ["noseSneerLeft", "noseSneerRight"],
    "AU10 upper lip raiser":  ["mouthUpperUpLeft", "mouthUpperUpRight"],
    "AU12 lip corner puller": ["mouthSmileLeft", "mouthSmileRight"],
    "AU14 dimpler":           ["mouthDimpleLeft", "mouthDimpleRight"],
    "AU15 lip corner down":   ["mouthFrownLeft", "mouthFrownRight"],
    "AU17 chin raiser":       ["mouthShrugUpper"],
    "AU20 lip stretcher":     ["mouthStretchLeft", "mouthStretchRight"],
    "AU23 lip tightener":     ["mouthPressLeft", "mouthPressRight"],
    "AU26 jaw drop":          ["jawOpen"],
    "AU43 eyes closed":       ["eyeBlinkLeft", "eyeBlinkRight"],
}

# Per-target blendshape groups for game match scoring. Each group must have
# at least one active blendshape for the group to count. Happiness requires
# multiple groups so it can't be hit with a non-Duchenne smile alone.
TARGET_BLENDSHAPES = {
    "Happiness": [["mouthSmileLeft", "mouthSmileRight"], ["cheekSquintLeft", "cheekSquintRight"]],
    "Sadness":   [["browInnerUp"], ["browDownLeft", "browDownRight"], ["mouthFrownLeft", "mouthFrownRight"]],
    "Anger":     [["browDownLeft", "browDownRight"], ["eyeSquintLeft", "eyeSquintRight"], ["mouthPressLeft", "mouthPressRight"]],
    "Fear":      [["browInnerUp"], ["browOuterUpLeft", "browOuterUpRight"], ["eyeWideLeft", "eyeWideRight"], ["jawOpen"]],
    "Surprise":  [["browInnerUp"], ["browOuterUpLeft", "browOuterUpRight"], ["eyeWideLeft", "eyeWideRight"], ["jawOpen"]],
    "Disgust":   [["noseSneerLeft", "noseSneerRight"], ["mouthUpperUpLeft", "mouthUpperUpRight"]],
    "Contempt":  [["mouthDimpleLeft", "mouthDimpleRight"]],  # asymmetry enforced in target_match
}

TARGET_HINTS = {
    "Happiness": "big smile + cheeks up",
    "Sadness":   "inner brows up, corners down",
    "Anger":     "brows together, jaw clenched, lips pressed",
    "Fear":      "brows up and together, eyes wide, jaw open",
    "Surprise":  "brows up, eyes wide, jaw drop (brows parallel)",
    "Disgust":   "wrinkle the nose, upper lip up",
    "Contempt":  "one-sided smirk (asymmetric)",
}


# --- model + camera loading ----------------------------------------------
def load_models(task_path: str = FACE_LANDMARKER_TASK):
    """Load HSEmotion (ONNX) + MediaPipe FaceLandmarker. Returns (recognizer, landmarker)."""
    recognizer = HSEmotionRecognizer(model_name="enet_b0_8_va_mtl")
    landmarker = mp_vision.FaceLandmarker.create_from_options(
        mp_vision.FaceLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=task_path),
            output_face_blendshapes=True,
            num_faces=1,
            running_mode=mp_vision.RunningMode.VIDEO,
        )
    )
    return recognizer, landmarker


def open_camera(index: int):
    cap = cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION)
    if not cap.isOpened():
        raise SystemExit(
            f"Could not open webcam (index {index}). "
            "On macOS, grant camera permission to your terminal app in "
            "System Settings -> Privacy & Security -> Camera, then relaunch it."
        )
    return cap


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


# --- inference + analysis -------------------------------------------------
def face_bbox_from_landmarks(landmarks, w: int, h: int, pad: float = FACE_PAD):
    xs = [lm.x for lm in landmarks]
    ys = [lm.y for lm in landmarks]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    bw, bh = x1 - x0, y1 - y0
    return (
        max(0, int((x0 - bw * pad) * w)),
        max(0, int((y0 - bh * pad) * h)),
        min(w - 1, int((x1 + bw * pad) * w)),
        min(h - 1, int((y1 + bh * pad) * h)),
    )


def blendshapes_to_dict(blendshapes_list) -> dict:
    return {b.category_name: float(b.score) for b in blendshapes_list}


def analyze_frame(frame, recognizer, landmarker, ts_ms: int) -> dict | None:
    """Run both models on a BGR frame. Returns None if no face is detected.

    Result dict has: bbox, class_probs, valence, arousal, blendshapes.
    """
    h, w = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    lm_result = landmarker.detect_for_video(mp_img, ts_ms)

    if not lm_result.face_landmarks:
        return None

    landmarks = lm_result.face_landmarks[0]
    x0, y0, x1, y1 = face_bbox_from_landmarks(landmarks, w, h)
    face_bgr = frame[y0:y1, x0:x1]
    if face_bgr.size == 0:
        return None

    face_rgb = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2RGB)
    _, scores = recognizer.predict_emotions(face_rgb, logits=False)
    class_probs = {recognizer.idx_to_class[i]: float(scores[i])
                   for i in range(len(recognizer.idx_to_class))}
    valence, arousal = float(scores[-2]), float(scores[-1])

    blendshapes = {}
    if lm_result.face_blendshapes:
        blendshapes = blendshapes_to_dict(lm_result.face_blendshapes[0])

    return {
        "bbox": (x0, y0, x1, y1),
        "class_probs": class_probs,
        "valence": valence,
        "arousal": arousal,
        "blendshapes": blendshapes,
    }


# --- emotion labeling -----------------------------------------------------
def intensity_label(cls: str, prob: float) -> str:
    tiers = INTENSITY_TIERS.get(cls, (cls, cls, cls))
    if prob < 0.50:
        return tiers[0]
    if prob < 0.80:
        return tiers[1]
    return tiers[2]


def describe(class_probs: dict) -> tuple[str, str]:
    """Return (nuanced_word, base_summary). base_summary is 'sad 42%' or 'sadness+disgust'."""
    ranked = sorted(class_probs.items(), key=lambda kv: kv[1], reverse=True)
    (top, top_p), (second, second_p) = ranked[0], ranked[1]
    base = f"{top.lower()} {top_p * 100:.0f}%"
    if top_p >= DYAD_MIN_TOP and second_p >= DYAD_MIN_SEC:
        dyad = DYADS.get(frozenset([top, second]))
        if dyad is not None:
            return dyad, f"{top.lower()}+{second.lower()}"
    return intensity_label(top, top_p), base


# --- AU computation -------------------------------------------------------
def compute_active_aus(bs: dict) -> list[tuple[str, float]]:
    """Top-N active FACS-style AUs derived from MediaPipe blendshapes."""
    active: list[tuple[str, float]] = []
    for au_label, names in AU_FROM_BLENDSHAPES.items():
        scores = [bs.get(n, 0.0) for n in names]
        val = sum(scores) / len(scores) if scores else 0.0
        if val >= AU_DISPLAY_THRESHOLD:
            active.append((au_label, val))

    # Asymmetry checks — for contempt (AU 14L/R) and unilateral AU 12L/R.
    pairs = [
        ("AU12L lip corner (L)", "AU12R lip corner (R)", "mouthSmileLeft", "mouthSmileRight"),
        ("AU14L dimpler (L)",    "AU14R dimpler (R)",    "mouthDimpleLeft", "mouthDimpleRight"),
    ]
    for left_label, right_label, left_name, right_name in pairs:
        left_val = bs.get(left_name, 0.0)
        right_val = bs.get(right_name, 0.0)
        if abs(left_val - right_val) >= AU_ASYMMETRY_THRESHOLD:
            if left_val > right_val:
                active.append((left_label, left_val))
            else:
                active.append((right_label, right_val))

    active.sort(key=lambda t: t[1], reverse=True)
    return active[:8]


# --- game match scoring ---------------------------------------------------
def target_match(
    target: str,
    class_probs: dict,
    bs: dict,
    class_prob_threshold: float,
    au_fraction_threshold: float,
    au_active_threshold: float = AU_DISPLAY_THRESHOLD,
) -> tuple[bool, float, float]:
    """Return (is_match, class_prob, au_fraction) for the given target emotion."""
    p = class_probs.get(target, 0.0)
    groups = TARGET_BLENDSHAPES.get(target, [])
    active = sum(
        1 for g in groups if any(bs.get(n, 0.0) >= au_active_threshold for n in g)
    )
    frac = active / len(groups) if groups else 1.0

    # Contempt: require asymmetry in dimplers or smile corners.
    if target == "Contempt":
        asym = max(
            abs(bs.get("mouthDimpleLeft", 0.0) - bs.get("mouthDimpleRight", 0.0)),
            abs(bs.get("mouthSmileLeft", 0.0) - bs.get("mouthSmileRight", 0.0)),
        )
        if asym < 0.15:
            frac = 0.0

    is_match = (p >= class_prob_threshold) and (frac >= au_fraction_threshold)
    return is_match, p, frac
