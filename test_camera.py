import cv2

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Webcam not found")
else:
    print("Webcam OK - press q in the video window to quit")
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        cv2.imshow("Camera test", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
cap.release()
cv2.destroyAllWindows()