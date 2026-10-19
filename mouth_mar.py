import time
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

# Landmark numbers for the mouth
MOUTH_LEFT = 78      # left corner
MOUTH_RIGHT = 308    # right corner
LIP_TOP = 13         # inner upper lip
LIP_BOTTOM = 14      # inner lower lip

def mouth_aspect_ratio(lm, w, h):
    def pt(i):
        return np.array([lm[i].x * w, lm[i].y * h])
    vertical = np.linalg.norm(pt(LIP_TOP) - pt(LIP_BOTTOM))
    horizontal = np.linalg.norm(pt(MOUTH_LEFT) - pt(MOUTH_RIGHT))
    return vertical / horizontal

options = vision.FaceLandmarkerOptions(
    base_options=mp_python.BaseOptions(model_asset_path="face_landmarker.task"),
    running_mode=vision.RunningMode.VIDEO,
    num_faces=1,
)
landmarker = vision.FaceLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)
start = time.monotonic()
min_mar = 10.0
max_mar = 0.0

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
        mar = mouth_aspect_ratio(lm, w, h)
        min_mar = min(min_mar, mar)
        max_mar = max(max_mar, mar)

        for i in (MOUTH_LEFT, MOUTH_RIGHT, LIP_TOP, LIP_BOTTOM):
            cv2.circle(frame, (int(lm[i].x * w), int(lm[i].y * h)), 3, (0, 255, 0), -1)
        cv2.putText(frame, f"MAR: {mar:.2f}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(frame, f"Lowest: {min_mar:.2f}", (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 200, 0), 2)
        cv2.putText(frame, f"Highest: {max_mar:.2f}", (20, 115),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 200, 0), 2)
    else:
        cv2.putText(frame, "No face", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Mouth Aspect Ratio", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()