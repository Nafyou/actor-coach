"""Shared inference + analysis helpers for the webcam emotion tools.

actor_coach.py renders; this module does inference, AU computation, emotion
labeling, and target scoring.

Two layers of emotion live here:
  - the 8 HSEmotion classes (what the classifier sees), and
  - the extended "emotion wheel" targets, scored from FACS-style blendshape
    recipes plus head pose and gaze — see WHEEL_SPECS and guides.md.
"""
from __future__ import annotations

import math
import urllib.request  # noqa: F401 — hsemotion_onnx package has a missing-import bug

import cv2
import numpy as np
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

# Head-pose thresholds (degrees) used by the wheel recipes.
HEAD_TILT_DEG = 8.0      # ear toward shoulder (FACS 55/56)
HEAD_PITCH_DEG = 8.0     # chin up (53) / chin down (54)
HEAD_TURN_DEG = 10.0     # head turned (51/52)
GAZE_THRESHOLD = 0.30    # eyeLook* blendshape level that counts as a gaze shift

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
    # wheel targets
    "Curious":      "brows up, hint of a smile, tilt the head",
    "Excited":      "brows up, eyes wide, big smile, mouth open",
    "Amused":       "laugh: cheeks up, jaw open, head back",
    "Content":      "soft closed-mouth smile, heavy lids, slow breath",
    "Proud":        "small smile, lips pressed, chin up",
    "Loving":       "warm Duchenne smile, head tilted",
    "Awe":          "brows up, eyes wide, jaw open, chin up, half-smile",
    "Relieved":     "exhale through puckered lips, lids soften",
    "Bored":        "heavy lids, head tilted or dropped, no smile",
    "Confused":     "brows down, eyes narrowed, head tilted",
    "Embarrassed":  "suppressed smile, head down, look away",
    "Ashamed":      "head down, eyes down, brows down, chin pushed up",
    "Sympathetic":  "inner brows up, lips pressed, chin raised, lean in",
    "Pain":         "brows down, eyes clamped, nose wrinkled, lips stretched",
    "Coy":          "Duchenne smile, head down + turned, eyes peek",
    "Anxious":      "inner brows up + together, lips stretched, eyes dart",
}

# --- extended "emotion wheel" targets --------------------------------------
# Each wheel target is a recipe of cues scored against the analysis dict:
#   ("au",   [names])         any listed blendshape active; (name, thr) overrides
#   ("not",  [names])         all listed blendshapes inactive
#   ("tilt" | "turn" | "chin_up" | "chin_down", degrees)   head pose
#   ("gaze", "down"|"up"|"averted", thr)
#   ("asym", (left, right), thr)   left/right difference
#   ("any",  [cues])          at least one sub-cue passes
# `hard` cues must all pass; `soft` cues must reach min_frac (default
# AU_FRACTION_THRESHOLD). `family` lists HSE classes any of which must clear
# CLASS_PROB_THRESHOLD — a valence/arousal sanity gate, since the classifier
# has no "curious" class of its own.
# AU sources: Cordaro et al. 2018 (Emotion 18:75) international core
# sequences; Keltner, Sauter, Tracy & Cowen 2019 (J Nonverbal Behav 43:133)
# Table 2; Shiota, Campos & Keltner 2003 — details per emotion in guides.md.
_SMILE = ["mouthSmileLeft", "mouthSmileRight"]
_SLIGHT_SMILE = [("mouthSmileLeft", 0.12), ("mouthSmileRight", 0.12)]
_CHEEK = ["cheekSquintLeft", "cheekSquintRight"]
_SQUINT = ["eyeSquintLeft", "eyeSquintRight"]
_WIDE = ["eyeWideLeft", "eyeWideRight"]
_BROW_UP = ["browInnerUp", "browOuterUpLeft", "browOuterUpRight"]
_BROW_DOWN = ["browDownLeft", "browDownRight"]
_PRESS = ["mouthPressLeft", "mouthPressRight"]
_STRETCH = ["mouthStretchLeft", "mouthStretchRight"]
_NOSE = ["noseSneerLeft", "noseSneerRight"]
_LIDS_DROOP = [("eyeBlinkLeft", 0.20), ("eyeBlinkRight", 0.20)]   # partial AU 43
_JAW = ["jawOpen"]
_PUCKER = ["mouthPucker", "mouthFunnel"]
# "control smile" (Cordaro): AU 12 + a dampener (14/15/23/24, lip roll)
_DAMPENER = ["mouthDimpleLeft", "mouthDimpleRight", "mouthFrownLeft", "mouthFrownRight",
             "mouthPressLeft", "mouthPressRight", "mouthRollLower", "mouthRollUpper"]
_LOOK_AWAY = ("any", [("gaze", "down", GAZE_THRESHOLD), ("gaze", "averted", GAZE_THRESHOLD),
                      ("turn", HEAD_TURN_DEG)])

WHEEL_SPECS = {
    "Curious": dict(
        wheel="Plutchik: anticipation petal, low tier (interest)",
        family=["Neutral", "Happiness", "Surprise"],
        soft=[("au", _BROW_UP), ("au", _SLIGHT_SMILE), ("tilt", HEAD_TILT_DEG)],
        hard=[("not", [("jawOpen", 0.40)]), ("not", [("eyeWideLeft", 0.50), ("eyeWideRight", 0.50)])],
        min_frac=0.67,
    ),
    "Excited": dict(
        wheel="Plutchik dyad joy + surprise (delight); feelings wheel: happy -> excited",
        family=["Happiness", "Surprise"],
        soft=[("au", _BROW_UP), ("au", _WIDE), ("au", _SMILE), ("au", _JAW)],
        hard=[],
        min_frac=0.75,
    ),
    "Amused": dict(
        wheel="feelings wheel: happy -> amused / playful",
        family=["Happiness"],
        soft=[("au", _CHEEK), ("au", _SMILE), ("chin_up", HEAD_PITCH_DEG)],
        hard=[("au", [("jawOpen", 0.20)])],
        min_frac=0.67,
    ),
    "Content": dict(
        wheel="Plutchik: joy petal, low tier (serenity); feelings wheel: peaceful -> content",
        family=["Happiness", "Neutral"],
        soft=[("au", _SLIGHT_SMILE), ("au", _LIDS_DROOP)],
        hard=[("not", [("jawOpen", 0.30)])],
        min_frac=1.0,
    ),
    "Proud": dict(
        wheel="feelings wheel: powerful -> proud / confident",
        family=["Happiness", "Neutral"],
        soft=[("au", _SLIGHT_SMILE), ("au", _PRESS), ("au", _CHEEK)],
        hard=[("chin_up", HEAD_PITCH_DEG)],
        min_frac=0.67,
    ),
    "Loving": dict(
        wheel="Plutchik dyad joy + trust (love); feelings wheel: peaceful -> loving",
        family=["Happiness"],
        soft=[("au", _SMILE), ("au", _CHEEK)],
        hard=[("tilt", HEAD_TILT_DEG)],
        min_frac=1.0,
    ),
    "Awe": dict(
        wheel="Plutchik dyad fear + surprise (awe); feelings wheel: surprised -> amazed",
        family=["Surprise", "Happiness", "Fear"],
        soft=[("au", _BROW_UP), ("au", _WIDE), ("au", _SLIGHT_SMILE), ("au", _JAW),
              ("chin_up", 6.0)],
        hard=[],
        min_frac=0.60,
    ),
    "Relieved": dict(
        wheel="feelings wheel: peaceful -> relieved",
        family=["Happiness", "Neutral"],
        soft=[("au", _LIDS_DROOP), ("au", _SLIGHT_SMILE), ("au", [("jawOpen", 0.15)])],
        # AU 18 is unique to relief among Cordaro's 22 — make it the gate.
        hard=[("au", _PUCKER)],
        min_frac=0.34,
    ),
    "Bored": dict(
        wheel="Plutchik: disgust petal, low tier (boredom); feelings wheel: sad -> bored",
        family=["Neutral", "Sadness", "Contempt", "Disgust"],
        soft=[("au", _LIDS_DROOP), ("any", [("tilt", HEAD_TILT_DEG), ("chin_down", HEAD_PITCH_DEG)])],
        hard=[("not", [("mouthSmileLeft", 0.20), ("mouthSmileRight", 0.20)]),
              ("not", [("browInnerUp", 0.30)])],
        min_frac=1.0,
    ),
    "Confused": dict(
        wheel="feelings wheel: surprised -> confused; scared -> bewildered",
        family=["Anger", "Neutral", "Sadness", "Disgust", "Fear"],
        soft=[("au", _BROW_DOWN), ("au", _SQUINT)],
        hard=[("tilt", HEAD_TILT_DEG), ("not", [("mouthSmileLeft", 0.20), ("mouthSmileRight", 0.20)])],
        min_frac=0.50,
    ),
    "Embarrassed": dict(
        wheel="feelings wheel: scared -> embarrassed; Plutchik tertiary dyad fear + disgust",
        family=["Happiness", "Neutral", "Fear"],
        soft=[("au", _SMILE), ("au", _DAMPENER), ("au", _SQUINT), _LOOK_AWAY],
        hard=[("chin_down", HEAD_PITCH_DEG)],
        min_frac=0.50,
    ),
    "Ashamed": dict(
        wheel="feelings wheel: sad -> ashamed / guilty",
        family=["Sadness", "Neutral", "Fear", "Disgust"],
        soft=[("au", _BROW_DOWN), ("au", ["mouthShrugUpper"]), ("gaze", "down", GAZE_THRESHOLD)],
        hard=[("chin_down", HEAD_PITCH_DEG), ("not", [("mouthSmileLeft", 0.20), ("mouthSmileRight", 0.20)])],
        min_frac=0.34,
    ),
    "Sympathetic": dict(
        wheel="feelings wheel: peaceful -> nurturing / caring",
        family=["Sadness", "Neutral"],
        soft=[("au", ["mouthShrugUpper"]), ("au", _PRESS), ("chin_down", HEAD_PITCH_DEG)],
        # AU 1 (the "oblique brow") is the signature; without it a resting face passes.
        hard=[("au", ["browInnerUp"]), ("not", [("mouthSmileLeft", 0.25), ("mouthSmileRight", 0.25)])],
        min_frac=0.34,
    ),
    "Pain": dict(
        wheel="feelings wheel: sad -> hurt",
        family=["Disgust", "Anger", "Sadness", "Fear"],
        soft=[("au", _BROW_DOWN), ("au", _CHEEK), ("au", _SQUINT), ("au", _NOSE),
              ("au", _STRETCH), ("au", _LIDS_DROOP)],
        hard=[],
        min_frac=0.50,
    ),
    "Coy": dict(
        wheel="feelings wheel: happy -> playful",
        family=["Happiness"],
        soft=[("au", _SMILE), ("au", _CHEEK), _LOOK_AWAY],
        hard=[("chin_down", HEAD_PITCH_DEG)],
        min_frac=0.67,
    ),
    "Anxious": dict(
        wheel="Plutchik: fear petal, low tier (apprehension); feelings wheel: scared -> anxious",
        family=["Fear", "Sadness", "Neutral"],
        soft=[("au", ["browInnerUp"]), ("au", _BROW_DOWN), ("au", _STRETCH + _PRESS), _LOOK_AWAY],
        hard=[("not", [("mouthSmileLeft", 0.20), ("mouthSmileRight", 0.20)])],
        min_frac=0.50,
    ),
}

WHEEL_TARGETS = list(WHEEL_SPECS)
ALL_TARGETS = EMOTION_TARGETS + WHEEL_TARGETS

# Keyboard keys for the pick menu / practice switching. 'b' (back) and 'q'
# (quit) are deliberately absent.
TARGET_KEYS = dict(zip("1234567" + "acdefghijklmnoprs", ALL_TARGETS))
KEY_FOR_TARGET = {name: key for key, name in TARGET_KEYS.items()}


# --- model + camera loading ----------------------------------------------
def load_models(task_path: str = FACE_LANDMARKER_TASK):
    """Load HSEmotion (ONNX) + MediaPipe FaceLandmarker. Returns (recognizer, landmarker)."""
    recognizer = HSEmotionRecognizer(model_name="enet_b0_8_va_mtl")
    landmarker = mp_vision.FaceLandmarker.create_from_options(
        mp_vision.FaceLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=task_path),
            output_face_blendshapes=True,
            output_facial_transformation_matrixes=True,
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


def head_pose_from_matrix(matrix) -> dict:
    """Head angles in degrees from MediaPipe's facial transformation matrix.

    The matrix maps the canonical face model into camera space (OpenGL-style:
    +Y up, +Z toward the camera), so its columns are the face's local axes.
      pitch  > 0 chin up (FACS 53), < 0 chin down (54)
      roll   tilt ear-to-shoulder (55/56) — sign depends on side, use abs()
      yaw    head turned (51/52) — sign depends on side, use abs()
    """
    rot = np.asarray(matrix, dtype=float)[:3, :3]
    fwd, up = rot[:, 2], rot[:, 1]
    clamp = lambda v: max(-1.0, min(1.0, float(v)))
    return {
        "pitch": math.degrees(math.asin(clamp(fwd[1]))),
        "yaw": math.degrees(math.asin(clamp(fwd[0]))),
        "roll": math.degrees(math.atan2(up[0], up[1])),
    }


def gaze_from_blendshapes(bs: dict) -> dict:
    """Gaze direction 0..1 from the eyeLook* blendshapes (FACS 61-64)."""
    avg = lambda a, b: (bs.get(a, 0.0) + bs.get(b, 0.0)) / 2
    return {
        "down": avg("eyeLookDownLeft", "eyeLookDownRight"),
        "up": avg("eyeLookUpLeft", "eyeLookUpRight"),
        # both eyes swinging the same way: one looks out while the other looks in
        "averted": max(avg("eyeLookOutLeft", "eyeLookInRight"),
                       avg("eyeLookInLeft", "eyeLookOutRight")),
    }


def analyze_frame(frame, recognizer, landmarker, ts_ms: int) -> dict | None:
    """Run both models on a BGR frame. Returns None if no face is detected.

    Result dict has: bbox, class_probs, valence, arousal, blendshapes,
    head (pitch/yaw/roll degrees, or None), gaze (down/up/averted 0..1).
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
    head = None
    if lm_result.facial_transformation_matrixes:
        head = head_pose_from_matrix(lm_result.facial_transformation_matrixes[0])

    return {
        "bbox": (x0, y0, x1, y1),
        "class_probs": class_probs,
        "valence": valence,
        "arousal": arousal,
        "blendshapes": blendshapes,
        "head": head,
        "gaze": gaze_from_blendshapes(blendshapes),
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
def _split(item):
    return item if isinstance(item, tuple) else (item, None)


def _cue_ok(cue, analysis: dict, au_thr: float) -> bool:
    kind = cue[0]
    bs = analysis["blendshapes"]
    head = analysis.get("head") or {}
    gaze = analysis.get("gaze") or {}
    if kind == "au":
        return any(bs.get(n, 0.0) >= (t if t is not None else au_thr)
                   for n, t in map(_split, cue[1]))
    if kind == "not":
        return all(bs.get(n, 0.0) < (t if t is not None else au_thr)
                   for n, t in map(_split, cue[1]))
    if kind == "tilt":
        return abs(head.get("roll", 0.0)) >= cue[1]
    if kind == "turn":
        return abs(head.get("yaw", 0.0)) >= cue[1]
    if kind == "chin_up":
        return head.get("pitch", 0.0) >= cue[1]
    if kind == "chin_down":
        return head.get("pitch", 0.0) <= -cue[1]
    if kind == "gaze":
        return gaze.get(cue[1], 0.0) >= cue[2]
    if kind == "asym":
        left, right = cue[1]
        return abs(bs.get(left, 0.0) - bs.get(right, 0.0)) >= cue[2]
    if kind == "any":
        return any(_cue_ok(c, analysis, au_thr) for c in cue[1])
    raise ValueError(f"unknown cue kind {kind!r}")


def target_spec(target: str) -> dict:
    """Unified cue spec for a core class or a wheel target."""
    if target in WHEEL_SPECS:
        return WHEEL_SPECS[target]
    spec = {
        "family": [target],
        "soft": [("au", group) for group in TARGET_BLENDSHAPES.get(target, [])],
        "hard": [],
    }
    # Contempt: require asymmetry in dimplers or smile corners.
    if target == "Contempt":
        spec["hard"] = [("any", [("asym", ("mouthDimpleLeft", "mouthDimpleRight"), 0.15),
                                 ("asym", ("mouthSmileLeft", "mouthSmileRight"), 0.15)])]
    return spec


def match_score(
    target: str,
    analysis: dict,
    class_prob_threshold: float,
    au_fraction_threshold: float,
    au_active_threshold: float = AU_DISPLAY_THRESHOLD,
) -> tuple[bool, float, float, float]:
    """Score one target. Returns (is_match, family_prob, cue_frac, visual).

    family_prob — best classifier probability among the target's HSE family
    cue_frac    — fraction of all cues (soft + hard) currently satisfied
    visual      — 0..1 progress for the match bar (half class, half cues)
    """
    spec = target_spec(target)
    probs = analysis["class_probs"]
    p = max((probs.get(f, 0.0) for f in spec["family"]), default=1.0)

    soft_ok = [_cue_ok(c, analysis, au_active_threshold) for c in spec["soft"]]
    hard_ok = [_cue_ok(c, analysis, au_active_threshold) for c in spec["hard"]]
    n_cues = len(soft_ok) + len(hard_ok)
    frac = (sum(soft_ok) + sum(hard_ok)) / n_cues if n_cues else 1.0
    soft_frac = sum(soft_ok) / len(soft_ok) if soft_ok else 1.0
    min_frac = spec.get("min_frac", au_fraction_threshold)

    is_match = p >= class_prob_threshold and all(hard_ok) and soft_frac >= min_frac
    visual = min(1.0, 0.5 * min(p / class_prob_threshold, 1.0) + 0.5 * frac)
    return is_match, p, frac, visual


def target_match(
    target: str,
    analysis: dict,
    class_prob_threshold: float,
    au_fraction_threshold: float,
    au_active_threshold: float = AU_DISPLAY_THRESHOLD,
) -> tuple[bool, float, float]:
    """Return (is_match, family_prob, cue_fraction) for the given target."""
    is_match, p, frac, _ = match_score(
        target, analysis, class_prob_threshold, au_fraction_threshold, au_active_threshold
    )
    return is_match, p, frac


def best_wheel_match(
    analysis: dict,
    class_prob_threshold: float,
    au_fraction_threshold: float,
    targets: list[str] = ALL_TARGETS,
) -> tuple[str | None, float, bool]:
    """Closest target by match progress. Returns (name, visual, is_match)."""
    best = (None, 0.0, False)
    for name in targets:
        is_match, _, _, visual = match_score(
            name, analysis, class_prob_threshold, au_fraction_threshold
        )
        # Prefer true matches; among equals, the higher visual score.
        if (is_match, visual) > (best[2], best[1]):
            best = (name, visual, is_match)
    return best
