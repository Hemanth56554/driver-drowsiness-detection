# Driver Drowsiness Detection

Real-time drowsiness detection using a webcam. The program finds the driver's face with MediaPipe Face Landmarker, measures the eyes and mouth, and raises an alarm when the eyes stay closed too long. It also counts yawns.

## How it works

1. The webcam captures video with OpenCV.
2. MediaPipe Face Landmarker detects 478 landmarks on the face.
3. **Eyes:** six landmarks around each eye give the Eye Aspect Ratio (EAR):
   EAR = (vertical distances) / (2 x horizontal distance)
   EAR is about 0.30 with open eyes and drops towards 0.05 when the eyes close.
   If EAR stays below 0.20 for 2 seconds, a red warning and a beep are triggered. Normal blinks are ignored.
4. **Mouth:** four landmarks give the Mouth Aspect Ratio (MAR):
   MAR = lip opening / mouth width
   In my tests, MAR was about 0.04 with the mouth closed, up to 0.30 while talking, and 0.9 to 1.2 during a wide yawn.
   A yawn is counted when MAR stays above 0.60 for 1.5 seconds.

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
python drowsiness_detector.py
```

Press `q` to quit.

## Settings

In `drowsiness_detector.py`:

- `EAR_THRESHOLD = 0.20` : below this value the eyes are treated as closed
- `CLOSED_SECONDS = 2.0` : closed-eye time before the alarm starts
- `MAR_THRESHOLD = 0.60` : above this value the mouth is treated as wide open
- `YAWN_SECONDS = 1.5` : open-mouth time before a yawn is counted

## Other files

- `eye_ear.py` : shows live EAR with lowest and highest values, used to choose the eye threshold
- `mouth_mar.py` : shows live MAR with lowest and highest values, used to choose the yawn threshold
- `alerts.py` : sends Telegram messages
- `logger.py` : writes alarms and yawns to `events.csv`
- `test_camera.py` : checks that the webcam works

## Planned features

- Head-nod detection
- Dim-light, glasses and angle testing
## Test results

Each test: 5 deliberate eye closures (about 3 seconds), 3 wide yawns, and 10 seconds of talking and normal blinking. Results are counted from the `events.csv` log.

| Condition | Eye closures detected | Yawns detected | False alarms |
|---|---|---|---|
| Bright light, no glasses | 5 / 5 | 3 / 3 | 0 |
| Dim light | to be tested | to be tested | to be tested |
| With glasses | to be tested | to be tested | to be tested |
| Head tilted / angled camera | to be tested | to be tested | to be tested |

## Known limitations

- Eye-closure detection is paused while the mouth is wide open, so a person sleeping with their mouth open would not trigger the eye alarm.
- Small yawns (MAR close to 0.60) may be missed.
- Tested on a laptop webcam only. Performance in a moving vehicle or at night is not yet measured.


## Author

Hemanth Akuthota