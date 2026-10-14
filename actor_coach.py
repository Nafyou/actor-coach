"""Actor Coach — real-time facial-emotion practice with multiple modes.

Modes:
  1. Classic Simon   — random prompt from the 7 core emotions, 5s to hit it,
                       one miss ends the game
  2. Practice        — pick any of the 23 emotions, drill it endlessly
  3. Freeplay        — mirror with live emotion bars, valence/arousal, AUs,
                       head pose, and the closest wheel emotion
  4. Wheel Simon     — classic rules, but prompts come from the full wheel

Run:  .venv/bin/python actor_coach.py 1          # camera index 1 (default 0)
      .venv/bin/python actor_coach.py --list     # probe indices 0..5
Quit:     q from the menu
Back:     b from any sub-mode
"""
import random
import sys
import time

import cv2

from emotion_lib import (
    ALL_TARGETS,
    EMOTION_TARGETS,
    KEY_FOR_TARGET,
    TARGET_HINTS,
    TARGET_KEYS,
    analyze_frame,
    best_wheel_match,
    compute_active_aus,
    describe,
    load_models,
    match_score,
    open_camera,
    probe_cameras,
)

# --- game-mode tuning -----------------------------------------------------
CLASS_PROB_THRESHOLD = 0.35
AU_FRACTION_THRESHOLD = 0.50
HOLD_DURATION = 0.25
ROUND_TIMEOUT = 5.0
READY_DURATION = 1.0
FLASH_DURATION = 1.0

# --- color palette --------------------------------------------------------
# Keep names generic so CUSTOMIZE.md can describe "what each color is for".
BG_OVERLAY = (0, 0, 0)
TEXT = (255, 255, 255)
MUTED = (180, 180, 180)
ACCENT = (0, 200, 255)
GREEN = (0, 200, 0)
RED = (30, 30, 230)
AMBER = (0, 200, 255)
BAR_BG = (60, 60, 60)
BAR_FG = (0, 200, 255)
AU_COLOR = (140, 230, 255)
BOX = (0, 255, 0)

# --- menu labels ----------------------------------------------------------
MAIN_MENU = [
    ("1", "Classic Simon",       "Random prompt from the 7 core emotions. 5s to hit. One miss = game over."),
    ("2", "Practice a single emotion", "Pick any of the 23. Drill it until you quit."),
    ("3", "Freeplay / Mirror",   "Live classes, AUs, head pose, and closest wheel emotion."),
    ("4", "Wheel Simon",         "Classic rules, all 23 emotions. Head pose counts. Hard."),
    ("q", "Quit",                ""),
]

# --- state identifiers ----------------------------------------------------
S_MENU = "menu"
S_PICK = "pick"
S_CLASSIC = "classic"
S_PRACTICE = "practice"
S_FREEPLAY = "freeplay"


# --- drawing helpers ------------------------------------------------------
def put_centered(frame, text, y, scale=1.0, color=TEXT, thickness=2):
    (tw, _), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, thickness)
    cv2.putText(frame, text, ((frame.shape[1] - tw) // 2, y),
                cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA)


def draw_strip(frame, y0, y1, alpha=0.55):
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, y0), (frame.shape[1], y1), BG_OVERLAY, -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)


def draw_dim(frame, alpha=0.55):
    draw_strip(frame, 0, frame.shape[0], alpha)


# --- menus ----------------------------------------------------------------
def draw_main_menu(frame):
    draw_dim(frame, 0.62)
    h = frame.shape[0]
    put_centered(frame, "ACTOR COACH", 80, 1.7, TEXT, 3)
    put_centered(frame, "real-time emotion training", 120, 0.55, MUTED, 1)

    base_y = h // 2 - 80
    for i, (key, name, desc) in enumerate(MAIN_MENU):
        y = base_y + i * 56
        cv2.putText(frame, f"[{key}]", (80, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, ACCENT, 2, cv2.LINE_AA)
        cv2.putText(frame, name, (150, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, TEXT, 2, cv2.LINE_AA)
        if desc:
            cv2.putText(frame, desc, (150, y + 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, MUTED, 1, cv2.LINE_AA)

    put_centered(frame, "press a key to pick a mode", h - 30, 0.5, MUTED, 1)


def draw_pick_menu(frame):
    draw_dim(frame, 0.62)
    h, w = frame.shape[:2]
    put_centered(frame, "Practice which emotion?", 60, 1.0, TEXT, 2)
    put_centered(frame, "press its key, [b] to go back", 90, 0.5, MUTED, 1)

    # Two columns: core 7 first, then the wheel. Row pitch shrinks on small frames.
    per_col = (len(ALL_TARGETS) + 1) // 2
    row_h = max(22, min(34, (h - 150) // per_col))
    col_w = w // 2
    font = cv2.FONT_HERSHEY_SIMPLEX
    for i, emotion in enumerate(ALL_TARGETS):
        col, row = divmod(i, per_col)
        x = 30 + col * col_w
        y = 130 + row * row_h
        color = TEXT if emotion in EMOTION_TARGETS else ACCENT
        cv2.putText(frame, f"[{KEY_FOR_TARGET[emotion]}]", (x, y), font, 0.6, ACCENT, 2, cv2.LINE_AA)
        cv2.putText(frame, emotion, (x + 42, y), font, 0.6, color, 2, cv2.LINE_AA)
        hint = TARGET_HINTS.get(emotion, "")
        if hint:
            cv2.putText(frame, hint, (x + 180, y), font, 0.4, MUTED, 1, cv2.LINE_AA)
    cv2.putText(frame, "white = classifier core   cyan = wheel (AU recipe + head pose)",
                (30, h - 14), font, 0.42, MUTED, 1, cv2.LINE_AA)


# --- classic + practice shared prompt HUD --------------------------------
def draw_prompt_hud(frame, target, time_left, score, match_frac, label_prefix="SHOW"):
    h, w = frame.shape[:2]
    draw_strip(frame, 0, 130)
    put_centered(frame, label_prefix + ":", 36, 0.7, AMBER, 1)
    put_centered(frame, target.upper(), 86, 1.6, TEXT, 3)
    put_centered(frame, TARGET_HINTS.get(target, ""), 115, 0.55, ACCENT, 1)

    cv2.putText(frame, f"Score: {score}", (w - 170, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, TEXT, 2, cv2.LINE_AA)

    if time_left is not None:
        bar_w = int(w * 0.7)
        x0 = (w - bar_w) // 2
        y0 = h - 50
        cv2.rectangle(frame, (x0, y0), (x0 + bar_w, y0 + 14), (50, 50, 50), -1)
        filled = int(bar_w * max(0.0, min(time_left / ROUND_TIMEOUT, 1.0)))
        color = GREEN if time_left > 2 else AMBER if time_left > 1 else RED
        cv2.rectangle(frame, (x0, y0), (x0 + filled, y0 + 14), color, -1)
        put_centered(frame, f"{time_left:0.1f}s", y0 - 6, 0.5, TEXT, 1)

    if match_frac is not None:
        mbar_w = 240
        mx = (w - mbar_w) // 2
        my = 150
        cv2.rectangle(frame, (mx, my), (mx + mbar_w, my + 10), (50, 50, 50), -1)
        cv2.rectangle(frame, (mx, my), (mx + int(mbar_w * match_frac), my + 10),
                      GREEN if match_frac >= 1.0 else AMBER, -1)
        cv2.putText(frame, "match", (mx, my - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, TEXT, 1, cv2.LINE_AA)

    cv2.putText(frame, "[b] back", (10, h - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, MUTED, 1, cv2.LINE_AA)


def draw_ready(frame, seconds_left, score):
    draw_strip(frame, 0, 130)
    put_centered(frame, "Get ready...", 70, 1.0, AMBER, 2)
    put_centered(frame, f"next in {seconds_left:0.1f}s", 110, 0.55, ACCENT, 1)
    cv2.putText(frame, f"Score: {score}", (frame.shape[1] - 170, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, TEXT, 2, cv2.LINE_AA)
    cv2.putText(frame, "[b] back", (10, frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, MUTED, 1, cv2.LINE_AA)


def draw_flash(frame, text, color, score):
    draw_dim(frame, 0.35)
    put_centered(frame, text, frame.shape[0] // 2, 1.8, color, 4)
    cv2.putText(frame, f"Score: {score}", (frame.shape[1] - 170, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, TEXT, 2, cv2.LINE_AA)


def draw_game_over(frame, score):
    draw_dim(frame, 0.6)
    h = frame.shape[0]
    put_centered(frame, "GAME OVER", h // 2 - 60, 1.9, RED, 4)
    put_centered(frame, f"Final score: {score}", h // 2, 1.2, TEXT, 2)
    put_centered(frame, "[r] restart   [b] menu   [q] quit", h // 2 + 60, 0.65, ACCENT, 1)


# --- freeplay drawing (mirror view) --------------------------------------
def draw_bars(frame, probs, origin=(10, 30)):
    x0, y0 = origin
    bar_w, bar_h, gap = 160, 14, 4
    for i, (name, p) in enumerate(sorted(probs.items(), key=lambda kv: kv[1], reverse=True)):
        y = y0 + i * (bar_h + gap)
        cv2.rectangle(frame, (x0, y), (x0 + bar_w, y + bar_h), BAR_BG, -1)
        filled = int(bar_w * max(0.0, min(p, 1.0)))
        cv2.rectangle(frame, (x0, y), (x0 + filled, y + bar_h), BAR_FG, -1)
        cv2.putText(frame, f"{name:<10}{p * 100:5.1f}%", (x0 + 4, y + bar_h - 3),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, TEXT, 1, cv2.LINE_AA)


def draw_circumplex(frame, valence, arousal, radius=60):
    w = frame.shape[1]
    cx = w - radius - 20
    cy = radius + 30
    cv2.circle(frame, (cx, cy), radius, MUTED, 1)
    cv2.line(frame, (cx - radius, cy), (cx + radius, cy), MUTED, 1)
    cv2.line(frame, (cx, cy - radius), (cx, cy + radius), MUTED, 1)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, "excited", (cx - 22, cy - radius - 4), font, 0.35, MUTED, 1, cv2.LINE_AA)
    cv2.putText(frame, "calm",    (cx - 14, cy + radius + 12), font, 0.35, MUTED, 1, cv2.LINE_AA)
    cv2.putText(frame, "neg",     (cx - radius - 22, cy + 4), font, 0.35, MUTED, 1, cv2.LINE_AA)
    cv2.putText(frame, "pos",     (cx + radius + 4, cy + 4), font, 0.35, MUTED, 1, cv2.LINE_AA)
    v = max(-1.0, min(1.0, float(valence)))
    a = max(-1.0, min(1.0, float(arousal)))
    cv2.circle(frame, (int(cx + v * radius), int(cy - a * radius)), 5, BAR_FG, -1)
    cv2.putText(frame, f"v={v:+.2f} a={a:+.2f}", (cx - radius, cy + radius + 28),
                font, 0.4, TEXT, 1, cv2.LINE_AA)


def draw_aus(frame, active_aus):
    if not active_aus:
        return
    h = frame.shape[0]
    x0 = 10
    y0 = h - 20 - len(active_aus) * 18
    cv2.putText(frame, "Active AUs", (x0, y0 - 6),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, TEXT, 1, cv2.LINE_AA)
    for i, (label, val) in enumerate(active_aus):
        y = y0 + (i + 1) * 18 - 4
        cv2.putText(frame, f"{label} {val:.2f}", (x0, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, AU_COLOR, 1, cv2.LINE_AA)


def draw_freeplay(frame, analysis):
    if analysis is None:
        return
    x0, y0, x1, y1 = analysis["bbox"]
    cv2.rectangle(frame, (x0, y0), (x1, y1), BOX, 2)
    nuanced, base = describe(analysis["class_probs"])
    cv2.putText(frame, nuanced, (x0, max(y0 - 28, 22)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, BOX, 2, cv2.LINE_AA)
    cv2.putText(frame, base, (x0, max(y0 - 8, 42)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, BOX, 1, cv2.LINE_AA)
    draw_bars(frame, analysis["class_probs"])
    draw_circumplex(frame, analysis["valence"], analysis["arousal"])
    draw_aus(frame, compute_active_aus(analysis["blendshapes"]))
    draw_head_and_wheel(frame, analysis)
    cv2.putText(frame, "[b] back   [q] quit",
                (10, frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, MUTED, 1, cv2.LINE_AA)


def draw_head_and_wheel(frame, analysis, origin=(190, 30)):
    """Head pose + gaze readout and the closest wheel emotion (freeplay)."""
    x0, y0 = origin
    font = cv2.FONT_HERSHEY_SIMPLEX
    head = analysis.get("head")
    if head:
        pitch, roll, yaw = head["pitch"], head["roll"], head["yaw"]
        chin = "up" if pitch > 0 else "down"
        txt = f"head  chin {chin} {abs(pitch):4.1f}  tilt {abs(roll):4.1f}  turn {abs(yaw):4.1f}"
        cv2.putText(frame, txt, (x0, y0), font, 0.42, AU_COLOR, 1, cv2.LINE_AA)
    gaze = analysis.get("gaze") or {}
    cv2.putText(frame, f"gaze  down {gaze.get('down', 0):.2f}  up {gaze.get('up', 0):.2f}"
                f"  averted {gaze.get('averted', 0):.2f}",
                (x0, y0 + 18), font, 0.42, AU_COLOR, 1, cv2.LINE_AA)
    name, visual, is_match = best_wheel_match(
        analysis, CLASS_PROB_THRESHOLD, AU_FRACTION_THRESHOLD)
    if name:
        color = GREEN if is_match else MUTED
        cv2.putText(frame, f"closest: {name} {visual * 100:.0f}%" + ("  MATCH" if is_match else ""),
                    (x0, y0 + 40), font, 0.55, color, 2, cv2.LINE_AA)


def draw_no_face_warning(frame):
    cv2.putText(frame, "No face detected",
                (10, frame.shape[0] - 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, RED, 2, cv2.LINE_AA)


# --- match-scoring glue used by classic + practice -----------------------
def match_progress(target, analysis):
    """Return (is_match, visual_match_frac 0..1) for the given target."""
    is_match, _, _, visual = match_score(
        target, analysis, CLASS_PROB_THRESHOLD, AU_FRACTION_THRESHOLD)
    return is_match, visual


# --- main -----------------------------------------------------------------
if len(sys.argv) > 1 and sys.argv[1] == "--list":
    probe_cameras()
    sys.exit(0)

camera_index = int(sys.argv[1]) if len(sys.argv) > 1 else 0

print("Loading HSEmotion + MediaPipe FaceLandmarker...")
recognizer, landmarker = load_models()
cap = open_camera(camera_index)
print(f"Camera {camera_index} open. Press q at the menu to quit.")

# App state (kept as a plain dict for transparency; see CUSTOMIZE.md).
app = {
    "mode": S_MENU,
    # Classic mode sub-state
    "classic_phase": "ready",   # ready | playing | flash | over
    "classic_phase_start": time.time(),
    "classic_score": 0,
    "classic_target": None,
    "classic_pool": EMOTION_TARGETS,   # or ALL_TARGETS for Wheel Simon
    "classic_round_start": None,
    "classic_hold_start": None,
    "classic_flash_text": "",
    "classic_flash_color": TEXT,
    # Practice mode
    "practice_target": None,
    "practice_score": 0,
    "practice_hold_start": None,
    "practice_flash_start": 0.0,
    "practice_flash_text": "",
}

frame_idx = 0
while True:
    ok, frame = cap.read()
    if not ok:
        break
    frame = cv2.flip(frame, 1)
    now = time.time()
    ts_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC)) or (frame_idx * 33)

    # Inference is shared across all modes (except pure menu screens, but we
    # still run it so the video behind the menu looks alive).
    analysis = analyze_frame(frame, recognizer, landmarker, ts_ms)

    key = cv2.waitKey(1) & 0xFF

    # ---- MENU ----------------------------------------------------------
    if app["mode"] == S_MENU:
        draw_main_menu(frame)
        if key == ord("q"):
            break
        if key in (ord("1"), ord("4")):
            app["mode"] = S_CLASSIC
            app["classic_pool"] = EMOTION_TARGETS if key == ord("1") else ALL_TARGETS
            app["classic_phase"] = "ready"
            app["classic_phase_start"] = now
            app["classic_score"] = 0
            app["classic_target"] = None
            app["classic_hold_start"] = None
        elif key == ord("2"):
            app["mode"] = S_PICK
        elif key == ord("3"):
            app["mode"] = S_FREEPLAY

    # ---- PICK EMOTION --------------------------------------------------
    elif app["mode"] == S_PICK:
        draw_pick_menu(frame)
        if key == ord("b"):
            app["mode"] = S_MENU
        elif chr(key) in TARGET_KEYS:
            app["practice_target"] = TARGET_KEYS[chr(key)]
            app["practice_score"] = 0
            app["practice_hold_start"] = None
            app["practice_flash_start"] = 0.0
            app["mode"] = S_PRACTICE

    # ---- CLASSIC SIMON -------------------------------------------------
    elif app["mode"] == S_CLASSIC:
        if key == ord("b"):  # back -> menu
            app["mode"] = S_MENU
            continue
        if app["classic_phase"] == "ready":
            elapsed = now - app["classic_phase_start"]
            draw_ready(frame, max(0.0, READY_DURATION - elapsed), app["classic_score"])
            if elapsed >= READY_DURATION:
                app["classic_target"] = random.choice(app["classic_pool"])
                app["classic_phase"] = "playing"
                app["classic_round_start"] = now
                app["classic_hold_start"] = None

        elif app["classic_phase"] == "playing":
            target = app["classic_target"]
            time_left = ROUND_TIMEOUT - (now - app["classic_round_start"])
            match_frac = 0.0
            if analysis is not None:
                is_match, match_frac = match_progress(target, analysis)
                if is_match:
                    if app["classic_hold_start"] is None:
                        app["classic_hold_start"] = now
                    if now - app["classic_hold_start"] >= HOLD_DURATION:
                        app["classic_score"] += 1
                        app["classic_phase"] = "flash"
                        app["classic_phase_start"] = now
                        app["classic_flash_text"] = f"+1  {target}!"
                        app["classic_flash_color"] = GREEN
                else:
                    app["classic_hold_start"] = None
            else:
                draw_no_face_warning(frame)

            if time_left <= 0 and app["classic_phase"] == "playing":
                app["classic_phase"] = "flash"
                app["classic_phase_start"] = now
                app["classic_flash_text"] = f"missed: {target}"
                app["classic_flash_color"] = RED

            draw_prompt_hud(frame, target, max(0.0, time_left),
                            app["classic_score"], match_frac)

        elif app["classic_phase"] == "flash":
            draw_flash(frame, app["classic_flash_text"],
                       app["classic_flash_color"], app["classic_score"])
            if now - app["classic_phase_start"] >= FLASH_DURATION:
                if app["classic_flash_color"] == RED:
                    app["classic_phase"] = "over"
                    app["classic_phase_start"] = now
                else:
                    app["classic_phase"] = "ready"
                    app["classic_phase_start"] = now

        elif app["classic_phase"] == "over":
            draw_game_over(frame, app["classic_score"])
            if key == ord("r"):
                app["classic_phase"] = "ready"
                app["classic_phase_start"] = now
                app["classic_score"] = 0
                app["classic_hold_start"] = None
            elif key == ord("q"):
                break

    # ---- PRACTICE ------------------------------------------------------
    elif app["mode"] == S_PRACTICE:
        if key == ord("b"):
            app["mode"] = S_MENU
            continue
        if chr(key) in TARGET_KEYS:
            app["practice_target"] = TARGET_KEYS[chr(key)]
            app["practice_hold_start"] = None
            app["practice_flash_start"] = 0.0
        target = app["practice_target"]
        match_frac = 0.0
        if analysis is not None:
            is_match, match_frac = match_progress(target, analysis)
            if is_match:
                if app["practice_hold_start"] is None:
                    app["practice_hold_start"] = now
                if now - app["practice_hold_start"] >= HOLD_DURATION:
                    app["practice_score"] += 1
                    app["practice_hold_start"] = None
                    app["practice_flash_start"] = now
                    app["practice_flash_text"] = f"+1  ({app['practice_score']})"
            else:
                app["practice_hold_start"] = None
        else:
            draw_no_face_warning(frame)

        draw_prompt_hud(frame, target, None, app["practice_score"], match_frac,
                        label_prefix="PRACTICE")
        cv2.putText(frame, "[1-7, a-s] switch emotion",
                    (120, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, MUTED, 1, cv2.LINE_AA)
        if now - app["practice_flash_start"] < 0.6:
            put_centered(frame, app["practice_flash_text"],
                         frame.shape[0] // 2, 1.5, GREEN, 3)

    # ---- FREEPLAY ------------------------------------------------------
    elif app["mode"] == S_FREEPLAY:
        if key == ord("b"):
            app["mode"] = S_MENU
            continue
        if key == ord("q"):
            break
        if analysis is None:
            draw_no_face_warning(frame)
        else:
            draw_freeplay(frame, analysis)

    cv2.imshow("Actor Coach", frame)
    if key == ord("q") and app["mode"] == S_MENU:
        break
    frame_idx += 1

cap.release()
cv2.destroyAllWindows()
