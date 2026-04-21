"""Emotion Simon — show the prompted emotion within 5 seconds to score.

Rules:
  - Game picks an emotion. You have 5 seconds to show it.
  - You score when the model classifies you as that emotion (>= threshold)
    AND the required FACS AUs are active, for a sustained quarter-second.
  - One miss = game over. Press 'r' to restart, 'q' to quit.

Run:  .venv/bin/python emotion_simon.py 1
"""
import random
import sys
import time
import urllib.request  # noqa: F401 — hsemotion_onnx has a missing-import bug

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
from hsemotion_onnx.facial_emotions import HSEmotionRecognizer

# --- tuning ---------------------------------------------------------------
ROUND_TIMEOUT = 5.0            # seconds to produce the emotion
HOLD_DURATION = 0.25           # sustained match required to score
READY_DURATION = 1.0           # pause between rounds
FLASH_DURATION = 1.2           # pause after round result
CLASS_PROB_THRESHOLD = 0.35    # minimum P(target_class)
AU_FRACTION_THRESHOLD = 0.50   # fraction of required AUs that must be active
AU_ACTIVE_THRESHOLD = 0.25     # per-blendshape score treated as "active"

FACE_LANDMARKER_TASK = "models/face_landmarker.task"
FACE_PAD = 0.15

# Round pool — Neutral excluded on purpose.
TARGETS = ["Happiness", "Sadness", "Anger", "Fear", "Surprise", "Disgust", "Contempt"]

# Required blendshapes per target (loose FACS recipe). Multiple blendshapes
# per row means any subset above AU_ACTIVE_THRESHOLD counts.
REQUIRED_BLENDSHAPES = {
    "Happiness": [["mouthSmileLeft", "mouthSmileRight"], ["cheekSquintLeft", "cheekSquintRight"]],
    "Sadness":   [["browInnerUp"], ["browDownLeft", "browDownRight"], ["mouthFrownLeft", "mouthFrownRight"]],
    "Anger":     [["browDownLeft", "browDownRight"], ["eyeSquintLeft", "eyeSquintRight"], ["mouthPressLeft", "mouthPressRight"]],
    "Fear":      [["browInnerUp"], ["browOuterUpLeft", "browOuterUpRight"], ["eyeWideLeft", "eyeWideRight"], ["jawOpen"]],
    "Surprise":  [["browInnerUp"], ["browOuterUpLeft", "browOuterUpRight"], ["eyeWideLeft", "eyeWideRight"], ["jawOpen"]],
    "Disgust":   [["noseSneerLeft", "noseSneerRight"], ["mouthUpperUpLeft", "mouthUpperUpRight"]],
    "Contempt":  [["mouthDimpleLeft", "mouthDimpleRight"]],  # asymmetry checked separately
}

# Short hint text shown with the prompt.
HINTS = {
    "Happiness": "big smile + cheeks up",
    "Sadness":   "inner brows up, corners down",
    "Anger":     "brows together, jaw clenched, lips pressed",
    "Fear":      "brows up and together, eyes wide, jaw open",
    "Surprise":  "brows up, eyes wide, jaw drop (brows parallel)",
    "Disgust":   "wrinkle the nose, upper lip up",
    "Contempt":  "one-sided smirk (asymmetric)",
}

# --- colors ---------------------------------------------------------------
BG_OVERLAY = (0, 0, 0)
TEXT = (255, 255, 255)
ACCENT = (0, 200, 255)
GREEN = (0, 200, 0)
RED = (30, 30, 230)
AMBER = (0, 200, 255)


# --- helpers --------------------------------------------------------------
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


def au_group_active(bs: dict, names: list) -> bool:
    return any(bs.get(n, 0.0) >= AU_ACTIVE_THRESHOLD for n in names)


def target_match(target: str, class_probs: dict, bs: dict) -> tuple[bool, float, float]:
    """Return (is_match, class_prob, au_fraction)."""
    p = class_probs.get(target, 0.0)
    groups = REQUIRED_BLENDSHAPES.get(target, [])
    active = sum(1 for g in groups if au_group_active(bs, g))
    frac = active / len(groups) if groups else 1.0

    # Contempt special case: require asymmetry in dimpler or smile corners.
    if target == "Contempt":
        asym = abs(bs.get("mouthDimpleLeft", 0.0) - bs.get("mouthDimpleRight", 0.0))
        asym = max(asym, abs(bs.get("mouthSmileLeft", 0.0) - bs.get("mouthSmileRight", 0.0)))
        if asym < 0.15:
            frac = min(frac, 0.0)  # force fail if symmetric

    is_match = (p >= CLASS_PROB_THRESHOLD) and (frac >= AU_FRACTION_THRESHOLD)
    return is_match, p, frac


# --- HUD drawing ----------------------------------------------------------
def put_centered(frame, text, y: int, scale: float, color=TEXT, thickness=2):
    (tw, _), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, thickness)
    w = frame.shape[1]
    cv2.putText(frame, text, ((w - tw) // 2, y),
                cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA)


def draw_translucent_strip(frame, y0: int, y1: int, alpha: float = 0.55):
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, y0), (frame.shape[1], y1), BG_OVERLAY, -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)


def draw_prompt(frame, target: str, time_left: float, score: int, match_frac: float | None):
    h, w = frame.shape[:2]
    draw_translucent_strip(frame, 0, 130)
    put_centered(frame, "SHOW:", 36, 0.7, AMBER, 1)
    put_centered(frame, target.upper(), 86, 1.6, TEXT, 3)
    put_centered(frame, HINTS.get(target, ""), 115, 0.55, ACCENT, 1)

    # score, top-right
    cv2.putText(frame, f"Score: {score}", (w - 170, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, TEXT, 2, cv2.LINE_AA)

    # countdown bar, bottom
    bar_w = int(w * 0.7)
    x0 = (w - bar_w) // 2
    y0 = h - 50
    cv2.rectangle(frame, (x0, y0), (x0 + bar_w, y0 + 14), (50, 50, 50), -1)
    filled = int(bar_w * max(0.0, min(time_left / ROUND_TIMEOUT, 1.0)))
    bar_color = GREEN if time_left > 2 else AMBER if time_left > 1 else RED
    cv2.rectangle(frame, (x0, y0), (x0 + filled, y0 + 14), bar_color, -1)
    put_centered(frame, f"{time_left:0.1f}s", y0 - 6, 0.5, TEXT, 1)

    # live match bar, just under the prompt
    if match_frac is not None:
        mbar_w = 240
        mx = (w - mbar_w) // 2
        my = 150
        cv2.rectangle(frame, (mx, my), (mx + mbar_w, my + 10), (50, 50, 50), -1)
        cv2.rectangle(frame, (mx, my), (mx + int(mbar_w * match_frac), my + 10),
                      GREEN if match_frac >= 1.0 else AMBER, -1)
        cv2.putText(frame, "match", (mx, my - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, TEXT, 1, cv2.LINE_AA)


def draw_ready(frame, seconds_left: float, score: int):
    h = frame.shape[0]
    draw_translucent_strip(frame, 0, 120)
    put_centered(frame, "Get ready...", 60, 1.0, AMBER, 2)
    put_centered(frame, f"next in {seconds_left:0.1f}s", 100, 0.5, ACCENT, 1)
    cv2.putText(frame, f"Score: {score}", (frame.shape[1] - 170, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, TEXT, 2, cv2.LINE_AA)


def draw_flash(frame, text: str, color, score: int):
    draw_translucent_strip(frame, 0, frame.shape[0], alpha=0.35)
    put_centered(frame, text, frame.shape[0] // 2, 1.8, color, 4)
    cv2.putText(frame, f"Score: {score}", (frame.shape[1] - 170, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, TEXT, 2, cv2.LINE_AA)


def draw_game_over(frame, score: int):
    draw_translucent_strip(frame, 0, frame.shape[0], alpha=0.55)
    h = frame.shape[0]
    put_centered(frame, "GAME OVER", h // 2 - 60, 2.0, RED, 4)
    put_centered(frame, f"Final score: {score}", h // 2, 1.2, TEXT, 2)
    put_centered(frame, "[r] restart    [q] quit", h // 2 + 60, 0.7, ACCENT, 1)


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
        num_faces=1,
        running_mode=mp_vision.RunningMode.VIDEO,
    )
)

cap = cv2.VideoCapture(camera_index, cv2.CAP_AVFOUNDATION)
if not cap.isOpened():
    raise SystemExit(
        f"Could not open webcam (index {camera_index}). "
        "Try: .venv/bin/python emotion_simon.py --list"
    )

# Game state
STATE_READY, STATE_PLAYING, STATE_FLASH, STATE_GAME_OVER = "ready", "playing", "flash", "over"


def new_game():
    return {
        "state": STATE_READY,
        "score": 0,
        "target": None,
        "round_start": None,
        "hold_start": None,
        "state_start": time.time(),
        "flash_text": "",
        "flash_color": TEXT,
    }


game = new_game()
frame_idx = 0
print(f"Camera {camera_index} open. Press 'q' to quit, 'r' to restart after game over.")

while True:
    ok, frame = cap.read()
    if not ok:
        break
    frame = cv2.flip(frame, 1)
    h, w = frame.shape[:2]
    now = time.time()

    # --- inference -----------------------------------------------------------
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    ts_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC)) or (frame_idx * 33)
    lm_result = landmarker.detect_for_video(mp_img, ts_ms)

    class_probs: dict = {}
    bs: dict = {}
    face_present = False
    if lm_result.face_landmarks:
        face_present = True
        landmarks = lm_result.face_landmarks[0]
        x0, y0, x1, y1 = face_bbox_from_landmarks(landmarks, w, h)
        face_bgr = frame[y0:y1, x0:x1]
        if face_bgr.size > 0:
            face_rgb = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2RGB)
            try:
                _, scores = recognizer.predict_emotions(face_rgb, logits=False)
                class_probs = {recognizer.idx_to_class[i]: float(scores[i])
                               for i in range(len(recognizer.idx_to_class))}
            except Exception as e:
                print(f"emotion error: {e}")
        if lm_result.face_blendshapes:
            bs = blendshapes_to_dict(lm_result.face_blendshapes[0])

    # --- state machine ------------------------------------------------------
    if game["state"] == STATE_READY:
        elapsed = now - game["state_start"]
        if elapsed >= READY_DURATION:
            game["target"] = random.choice(TARGETS)
            game["state"] = STATE_PLAYING
            game["round_start"] = now
            game["hold_start"] = None

    elif game["state"] == STATE_PLAYING:
        time_left = ROUND_TIMEOUT - (now - game["round_start"])
        match_frac = 0.0
        if face_present and class_probs:
            is_match, p, frac = target_match(game["target"], class_probs, bs)
            # Visual match 0..1 = combined progress toward both gates
            match_frac = min(
                1.0,
                0.5 * min(p / CLASS_PROB_THRESHOLD, 1.0)
                + 0.5 * min(frac / AU_FRACTION_THRESHOLD, 1.0),
            )
            if is_match:
                if game["hold_start"] is None:
                    game["hold_start"] = now
                if now - game["hold_start"] >= HOLD_DURATION:
                    game["score"] += 1
                    game["state"] = STATE_FLASH
                    game["state_start"] = now
                    game["flash_text"] = f"+1  {game['target']}!"
                    game["flash_color"] = GREEN
            else:
                game["hold_start"] = None

        if time_left <= 0 and game["state"] == STATE_PLAYING:
            game["state"] = STATE_FLASH
            game["state_start"] = now
            game["flash_text"] = f"missed: {game['target']}"
            game["flash_color"] = RED

        draw_prompt(frame, game["target"], max(0.0, time_left), game["score"], match_frac)

    elif game["state"] == STATE_FLASH:
        elapsed = now - game["state_start"]
        draw_flash(frame, game["flash_text"], game["flash_color"], game["score"])
        if elapsed >= FLASH_DURATION:
            if game["flash_color"] == RED:
                game["state"] = STATE_GAME_OVER
                game["state_start"] = now
            else:
                game["state"] = STATE_READY
                game["state_start"] = now

    elif game["state"] == STATE_GAME_OVER:
        draw_game_over(frame, game["score"])

    # Ready screen drawing
    if game["state"] == STATE_READY:
        draw_ready(frame, READY_DURATION - (now - game["state_start"]), game["score"])

    if not face_present:
        cv2.putText(frame, "No face detected",
                    (10, h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, RED, 2, cv2.LINE_AA)

    cv2.imshow("Emotion Simon", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    if key == ord("r") and game["state"] == STATE_GAME_OVER:
        game = new_game()

    frame_idx += 1

cap.release()
cv2.destroyAllWindows()
