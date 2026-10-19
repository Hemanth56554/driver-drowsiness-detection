import time
import winsound
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
from alerts import send_telegram
from logger import log_event

# ---- Settings you can change later ----
EAR_THRESHOLD = 0.20     # below this = eyes closed
CLOSED_SECONDS = 2.0     # eyes closed this long = drowsy alarm
MAR_THRESHOLD = 0.60     # above this = mouth wide open
YAWN_SECONDS = 1.5       # mouth open this long = one yawn
ALERT_GAP_SECONDS = 30   # minimum time between two drowsy Telegram messages
PITCH_THRESHOLD = 15     # head tilted forward more than this (degrees) = nodding
NOD_SECONDS = 1.5        # head down this long = one nod

# Landmark numbers
RIGHT_EYE = [33, 160, 158, 133, 153, 144]
LEFT_EYE = [362, 385, 387, 263, 373, 380]
MOUTH_LEFT, MOUTH_RIGHT, LIP_TOP, LIP_BOTTOM = 78, 308, 13, 14


def eye_aspect_ratio(pts):
    p1, p2, p3, p4, p5, p6 = pts
    vertical = np.linalg.norm(p2 - p6) + np.linalg.norm(p3 - p5)
    horizontal = 2.0 * np.linalg.norm(p1 - p4)
    return vertical / horizontal


def mouth_aspect_ratio(pt):
    vertical = np.linalg.norm(pt(LIP_TOP) - pt(LIP_BOTTOM))
    horizontal = np.linalg.norm(pt(MOUTH_LEFT) - pt(MOUTH_RIGHT))
    return vertical / horizontal


options = vision.FaceLandmarkerOptions(
    base_options=mp_python.BaseOptions(model_asset_path="face_landmarker.task"),
    running_mode=vision.RunningMode.VIDEO,
        num_faces=1,
    output_facial_transformation_matrixes=True,
)
landmarker = vision.FaceLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)
start = time.monotonic()

closed_since = None       # when the eyes first closed
mouth_open_since = None   # when the mouth first opened wide
yawn_counted = False      # so one long yawn is counted only once
yawn_count = 0
head_down_since = None
nod_counted = False
nod_count = 0
last_alert_time = -1000.0  # when the last drowsy Telegram message was sent

while True:
    ok, frame = cap.read()
    if not ok:
        break
    h, w = frame.shape[:2]

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    timestamp_ms = int((time.monotonic() - start) * 1000)
    result = landmarker.detect_for_video(mp_image, timestamp_ms)
    now = time.monotonic()

    if result.face_landmarks:
        lm = result.face_landmarks[0]

        def pt(i):
            return np.array([lm[i].x * w, lm[i].y * h])

        right = np.array([pt(i) for i in RIGHT_EYE])
        left = np.array([pt(i) for i in LEFT_EYE])
        ear = (eye_aspect_ratio(right) + eye_aspect_ratio(left)) / 2.0
        mar = mouth_aspect_ratio(pt)

        # Draw eye and mouth points
        for p in np.vstack([right, left]):
            cv2.circle(frame, (int(p[0]), int(p[1])), 2, (0, 255, 0), -1)
        for i in (MOUTH_LEFT, MOUTH_RIGHT, LIP_TOP, LIP_BOTTOM):
            p = pt(i)
            cv2.circle(frame, (int(p[0]), int(p[1])), 3, (255, 0, 255), -1)

        # Numbers on screen
        cv2.putText(frame, f"EAR: {ear:.2f}", (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(frame, f"MAR: {mar:.2f}", (20, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(frame, f"Yawns: {yawn_count}", (20, 95),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 200, 0), 2)

        # ---- Eye logic ----
        # While the mouth is wide open (a yawn), eyes squint, so ignore EAR
        mouth_wide = mar > MAR_THRESHOLD
        if ear < EAR_THRESHOLD and not mouth_wide:
            if closed_since is None:
                closed_since = now
            closed_for = now - closed_since
            cv2.putText(frame, f"Eyes closed: {closed_for:.1f}s", (20, 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
            if closed_for >= CLOSED_SECONDS:
                cv2.rectangle(frame, (0, 0), (w, h), (0, 0, 255), 12)
                cv2.putText(frame, "DROWSY! WAKE UP!", (20, h - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 0, 255), 4)
                # Log and Telegram message, at most once per ALERT_GAP_SECONDS
                if now - last_alert_time >= ALERT_GAP_SECONDS:
                    last_alert_time = now
                    log_event("DROWSY", ear, mar)
                    send_telegram(
                        "DRIVER DROWSY! Eyes closed for "
                        f"{closed_for:.1f}s at {time.strftime('%H:%M:%S')}"
                    )
                winsound.Beep(1000, 200)
        else:
            closed_since = None
            cv2.putText(frame, "Eyes: Open", (20, 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        # ---- Head-nod logic ----
        if result.facial_transformation_matrixes:
            m = np.array(result.facial_transformation_matrixes[0])
            pitch = float(np.degrees(np.arctan2(-m[1][2], m[2][2])))
            cv2.putText(frame, f"Pitch: {pitch:.0f}", (20, 195),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            if pitch > PITCH_THRESHOLD:
                if head_down_since is None:
                    head_down_since = now
                if now - head_down_since >= NOD_SECONDS:
                    cv2.putText(frame, "HEAD NOD!", (20, 230),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 3)
                    if not nod_counted:
                        nod_count += 1
                        nod_counted = True
                        log_event("NOD", ear, mar)
                        send_telegram(
                            f"Head nod #{nod_count} detected at {time.strftime('%H:%M:%S')}"
                        )
            else:
                head_down_since = None
                nod_counted = False
        # ---- Yawn logic ----
        if mouth_wide:
            if mouth_open_since is None:
                mouth_open_since = now
            open_for = now - mouth_open_since
            if open_for >= YAWN_SECONDS:
                if not yawn_counted:
                    yawn_count += 1
                    yawn_counted = True
                    log_event("YAWN", ear, mar)
                    send_telegram(
                        f"Yawn #{yawn_count} detected at {time.strftime('%H:%M:%S')}"
                    )
                cv2.putText(frame, "YAWNING", (20, 165),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)
        else:
            mouth_open_since = None
            yawn_counted = False
    else:
        closed_since = None
        mouth_open_since = None
        yawn_counted = False
        cv2.putText(frame, "No face", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Drowsiness Detector", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()