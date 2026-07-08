import cv2
from detector import detectar_rosto

camera = cv2.VideoCapture(0)

while True:

    ret, frame = camera.read()

    if not ret:
        break

    frame = detectar_rosto(frame)

    cv2.imshow("Detector de Fadiga", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()