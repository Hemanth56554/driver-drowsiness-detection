import time
import winsound
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

# ---- Settings you can change later ----
EAR_THRESHOLD = 0.20      # below this = eyes considered closed
CLOSED_SECONDS = 2.0      # eyes closed this long = drowsy alarm

# Landmark numbers for 6 points around each eye
RIGHT_EYE = [33, 160, 158, 133, 153, 144]
LEFT_EYE = [362, 385, 387, 263, 373, 380]

def eye_aspect_ratio(pts):
    p1, p2, p3, p4, p5, p6 = pts
    vertical = np.linalg.norm(p2 - p6) + np.linalg.norm(p3 - p5)
    horizontal = 2.0 * np.linalg.norm(p1 - p4)
    return vertical / horizontal

options = vision.FaceLandmarkerOptions(
    base_options=mp_python.BaseOptions(model_asset_path="face_landmarker.task"),
    running_mode=vision.RunningMode.VIDEO,
    num_faces=1,
)
landmarker = vision.FaceLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)
start = time.monotonic()
closed_since = None   # time when eyes first closed (None = eyes open)

while True:
    ok, frame = cap.read()
    if not ok:
        break
    h, w = frame.shape[:2]

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    timestamp_ms = int((time.monotonic() - start) * 1000)
    result = landmarker.detect_for_video(mp_image, timestamp_ms)

    if result.face_landmarks:
        lm = result.face_landmarks[0]

        def get_points(idx_list):
            return np.array([[lm[i].x * w, lm[i].y * h] for i in idx_list])

        right = get_points(RIGHT_EYE)
        left = get_points(LEFT_EYE)
        ear = (eye_aspect_ratio(right) + eye_aspect_ratio(left)) / 2.0

        for p in np.vstack([right, left]):
            cv2.circle(frame, (int(p[0]), int(p[1])), 2, (0, 255, 0), -1)
        cv2.putText(frame, f"EAR: {ear:.2f}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        if ear < EAR_THRESHOLD:
            if closed_since is None:
                closed_since = time.monotonic()
            closed_for = time.monotonic() - closed_since
            cv2.putText(frame, f"Eyes closed: {closed_for:.1f}s", (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
            if closed_for >= CLOSED_SECONDS:
                cv2.rectangle(frame, (0, 0), (w, h), (0, 0, 255), 12)
                cv2.putText(frame, "DROWSY! WAKE UP!", (20, h - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 0, 255), 4)
                winsound.Beep(1000, 200)
        else:
            closed_since = None
            cv2.putText(frame, "Status: Awake", (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    else:
        closed_since = None
        cv2.putText(frame, "No face", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Drowsiness Detector", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()