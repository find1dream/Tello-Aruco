import cv2
import sys


video_capture = cv2.VideoCapture(0)
i = 0
while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()
    i += 1
    if cv2.waitKey(1) & 0xFF == ord('t'):
        cv2.imwrite(str(i)+".png", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Display the resulting frame
    cv2.imshow('Video', frame)
# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
