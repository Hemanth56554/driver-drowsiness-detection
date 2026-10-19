# Driver Drowsiness Detection

Real-time drowsiness detection using a webcam. The program finds the driver's face with MediaPipe Face Landmarker, measures the eyes, mouth and head tilt, and raises alerts on the screen and on a phone through Telegram. Every event is also saved to a CSV log.

## Features

- Eye-closure alarm: red warning and beep when the eyes stay closed too long
- Yawn detection and counting
- Head-nod detection with automatic calibration
- Telegram messages to your phone (sent in a background thread, so the video never freezes)
- CSV event log (`events.csv`)

## How it works

1. The webcam captures video with OpenCV.
2. MediaPipe Face Landmarker detects 478 landmarks on the face.
3. **Eyes:** six landmarks around each eye give the Eye Aspect Ratio (EAR):
   EAR = (vertical distances) / (2 x horizontal distance)
   EAR is about 0.30 with open eyes and drops towards 0.05 when the eyes close.
   If EAR stays below 0.20 for 2 seconds, the alarm triggers. Normal blinks are ignored.
4. **Mouth:** four landmarks give the Mouth Aspect Ratio (MAR):
   MAR = lip opening / mouth width
   In my tests, MAR was about 0.04 with the mouth closed, up to 0.30 while talking, and 0.9 to 1.2 during a wide yawn.
   A yawn is counted when MAR stays above 0.60 for 1.5 seconds, and it ends only when MAR falls below 0.42, so one long yawn is not counted twice.
5. **Yawn vs. eye squint:** eyes squint during a yawn, which lowers EAR. While the mouth is wide open, the eye alarm is paused so a yawn is not mistaken for sleep.
6. **Head nod with auto-calibration:** the head pitch angle comes from the face transformation matrix. For the first 5 seconds the program measures your resting pitch (mine was 10 to 16 degrees). A nod is counted when pitch stays 12 degrees above that for 2 seconds. Press `c` to recalibrate.
7. **Head drop vs. eye alarm:** a lowered head makes the eyes look narrower to the camera, so the eye alarm is paused while the head is dropped.

## Requirements

- Windows 10 or later (the beep uses `winsound`)
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

## Telegram setup

1. In Telegram, talk to **BotFather**, send `/newbot`, and follow the steps to get a bot token.
2. Send any message to your new bot.
3. Create a file named `.env` in the project folder with:

```
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

4. To find your chat ID, run `python tools/get_chat_id.py` after the first message.

The `.env` file is ignored by Git, so your token is never uploaded. Never share the token. Without a `.env` file the detector still works, but no messages are sent.

## Run

```
python drowsiness_detector.py
```

Press `q` to quit, `c` to recalibrate head position.

## Settings

In `drowsiness_detector.py`:

- `EAR_THRESHOLD = 0.20` : below this value the eyes are treated as closed
- `CLOSED_SECONDS = 2.0` : closed-eye time before the alarm starts
- `MAR_THRESHOLD = 0.60` : above this value the mouth is treated as wide open
- `YAWN_SECONDS = 1.5` : open-mouth time before a yawn is counted
- `NOD_OFFSET = 12` : degrees above your resting pitch treated as head down
- `NOD_SECONDS = 2.0` : head-down time before a nod is counted
- `CALIBRATION_SECONDS = 5` : time spent measuring your resting head position
- `ALERT_GAP_SECONDS = 30` : minimum time between two drowsy Telegram messages

## Test results

Each test: 5 deliberate eye closures (about 3 seconds), 3 wide yawns, and 10 seconds of talking and normal blinking. Results are counted from the `events.csv` log.

| Condition | Eye closures detected | Yawns detected | Notes |
|---|---|---|---|
| Bright light, no glasses | 5 / 5 | 3 / 3 | 0 false alarms |
| Dim light | 5 / 5 | 3 done, 4 logged | One long yawn was counted twice; fixed by the yawn-reset rule. 0 false nods |
| Clear glasses | works | works | No failures observed |
| Dark / tinted glasses | not detected | not measured | EAR does not change when the eyes close |
| Angled camera | not tested | not tested | Planned |

## Known limitations

- Eye-closure detection is paused while the mouth is wide open or the head is dropped, so a person sleeping with the mouth open would not trigger the eye alarm.
- Small yawns (MAR close to 0.60) may be missed.
- Looking down at a phone or dashboard also tilts the head forward and can look like a nod.
- Dark or tinted glasses hide the eyelids, so eye-closure detection does not work. Commercial systems use infrared cameras to solve this.
- Thresholds are tuned to one person. Other faces may need different values.
- Tested on a laptop webcam only. Performance in a moving vehicle or at night is not yet measured.
- This is a learning project and is not a safety device.

## Other files

- `eye_ear.py` : live EAR with lowest and highest values, used to choose the eye threshold
- `mouth_mar.py` : live MAR with lowest and highest values, used to choose the yawn threshold
- `head_pitch.py` : live head pitch, used to choose the nod threshold
- `alerts.py` : sends Telegram messages
- `logger.py` : writes events to `events.csv`
- `test_camera.py` : checks that the webcam works

## Planned features

- Angled-camera testing
- Sunglasses mode (manual toggle)
- Android version

## Author

Hemanth Akuthota