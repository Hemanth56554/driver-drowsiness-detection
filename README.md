# Driver Drowsiness Detection

Real-time drowsiness detection using a webcam. The program finds the driver's face with MediaPipe Face Landmarker, calculates the Eye Aspect Ratio (EAR), and raises an alarm when the eyes stay closed for too long.

## How it works

1. The webcam captures video with OpenCV.
2. MediaPipe Face Landmarker detects 478 landmarks on the face.
3. Six landmarks around each eye are used to compute the EAR:
   EAR = (vertical distances) / (2 x horizontal distance)
4. EAR is about 0.30 with open eyes and drops towards 0.05 when the eyes close.
5. If EAR stays below 0.20 for 2 seconds, a red warning and a beep are triggered. Normal blinks are ignored.

## Requirements

- Windows 10 or later
- Python 3.13 (3.10 or newer should also work)
- A webcam

## Setup

```
git clone https://github.com/Hemanth56554/driver-drowsiness-detection.git
cd driver-drowsiness-detection
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```

Download the face model into the project folder:

```
Invoke-WebRequest -Uri "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task" -OutFile "face_landmarker.task"
```

## Run

```
python eye_ear.py
```

Press `q` to quit.

## Settings

In `eye_ear.py`:

- `EAR_THRESHOLD = 0.20` : below this value the eyes are treated as closed
- `CLOSED_SECONDS = 2.0` : closed-eye time before the alarm starts

## Planned features

- Yawn detection
- Head-nod detection
- Telegram alert
- Test results across lighting conditions

## Author

Hemanth Akuthota