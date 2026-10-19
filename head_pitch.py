import time
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

options = vision.FaceLandmarkerOptions(
    base_options=mp_python.BaseOptions(model_asset_path="face_landmarker.task"),
    running_mode=vision.RunningMode.VIDEO,
    num_faces=1,
    output_facial_transformation_matrixes=True,
)
landmarker = vision.FaceLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)
start = time.monotonic()
min_p, max_p = 999.0, -999.0

while True:
    ok, frame = cap.read()
    if not ok:
        break
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    ts = int((time.monotonic() - start) * 1000)
    result = landmarker.detect_for_video(mp_image, ts)

    if result.facial_transformation_matrixes:
        m = np.array(result.facial_transformation_matrixes[0])
        # Pitch: up-and-down head tilt, in degrees
        pitch = float(np.degrees(np.arctan2(-m[1][2], m[2][2])))
        min_p, max_p = min(min_p, pitch), max(max_p, pitch)
        cv2.putText(frame, f"Pitch: {pitch:.0f}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(frame, f"Min: {min_p:.0f}  Max: {max_p:.0f}", (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 200, 0), 2)
    else:
        cv2.putText(frame, "No face", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Head pitch", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()