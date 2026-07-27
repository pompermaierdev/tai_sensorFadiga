import cv2
from detector import detectar_rosto

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Erro: nao foi possivel acessar a webcam.")
    exit(1)

print("Detector de fadiga rodando. Pressione 'q' para sair.")

while True:
    ret, frame = camera.read()

    if not ret:
        print("Erro ao ler frame da camera.")
        break

    frame = detectar_rosto(frame)

    cv2.imshow("Detector de Fadiga", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()