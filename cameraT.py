#bibliotecas necessarias
import cv2
import numpy as np
import serial
import time
import urllib.request
import os
import mediapipe as mp

PORTA_SERIAL = 'COM3'  #pra relacionar com o arduino
BAUDRATE = 9600 #vel da comunicação serial (computador e arduino)

try:
    arduino = serial.Serial(PORTA_SERIAL, BAUDRATE, timeout=1)#pra abrir a porta
    time.sleep(2)
    arduino.reset_input_buffer()#limpa a memoria de entrada
    print(f"[INFO] Conectado na porta {PORTA_SERIAL}")
except Exception as e:
    print(f"[ERRO] Falha na conexão serial: {e}")
    arduino = None

MODEL_PATH = "face_landmarker.task"
if not os.path.exists(MODEL_PATH):
    url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task" #para se não tiver o arquivo na pasta ele baixar automaticamente
    urllib.request.urlretrieve(url, MODEL_PATH)

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.IMAGE,
    num_faces=1
)

landmarker = FaceLandmarker.create_from_options(options) #inicializa e configura para so um rosto por vez

def calcular_ear(pts, p_h1, p_v1, p_v2, p_h2, p_v3, p_v4):
    d_v1 = np.linalg.norm(pts[p_v1] - pts[p_v2])
    d_v2 = np.linalg.norm(pts[p_v3] - pts[p_v4])
    d_h = np.linalg.norm(pts[p_h1] - pts[p_h2])
    return (d_v1 + d_v2) / (2.0 * d_h)

LIMIAR_EAR = 0.21  #limite do ear do sistema       
FRAMES_FADIGA = 8    #quantidade min de piscadas seguidas para alertar 
contador_frames = 0
ultimo_estado = None

cap = cv2.VideoCapture(0)#abre a webcam do pc

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)#inverte a imagem
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    detection_result = landmarker.detect(mp_image) #acah onde estão as coordenadas do rosto
    estado_atual = '0'

    if detection_result.face_landmarks:
        face = detection_result.face_landmarks[0]
        pts = np.array([(int(pt.x * w), int(pt.y * h)) for pt in face])

        ear_esq = calcular_ear(pts, 33, 160, 144, 133, 158, 153)
        ear_dir = calcular_ear(pts, 362, 385, 380, 263, 387, 373)
        ear_medio = (ear_esq + ear_dir) / 2.0

        cv2.putText(frame, f"EAR: {ear_medio:.2f}", (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        if ear_medio < LIMIAR_EAR:
            contador_frames += 1
            if contador_frames >= FRAMES_FADIGA:
                estado_atual = '2' #buzzer e led
                cv2.putText(frame, "ALERTA: FADIGA DETECTADA!", (30, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            else:
                estado_atual = '1' # led
        else:
            contador_frames = 0
            estado_atual = '0'

    if arduino and estado_atual != ultimo_estado:
        arduino.write(estado_atual.encode())
        print(f"[SERIAL] Estado: {estado_atual}")
        ultimo_estado = estado_atual

    cv2.imshow("Monitoramento de Fadiga", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):#para encerrar o sistema
        break

cap.release()
cv2.destroyAllWindows()
if arduino:
    arduino.write(b'0')
    arduino.close()