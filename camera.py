import cv2

# Abre a câmera (0 é a webcam padrão)
camera = cv2.VideoCapture(0)

while True:
    ret, frame = camera.read()
    if not ret:
        print("Erro ao acessar a câmera.")
        break
    # Mostra o vídeo
    cv2.imshow("Camera", frame)
    # Fecha ao apertar a tecla Q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
