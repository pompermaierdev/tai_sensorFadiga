import cv2
import time
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# ==========================
# CONFIGURAÇÃO DO MODELO
# ==========================

modelo = "face_landmarker.task"


opcoes = vision.FaceLandmarkerOptions(
    base_options=python.BaseOptions(
        model_asset_path=modelo
    ),
    running_mode=vision.RunningMode.VIDEO,
    num_faces=1
)


detector = vision.FaceLandmarker.create_from_options(opcoes)


# Guarda o último tempo do frame
ultimo_tempo = 0


# ==========================
# DETECTOR DE ROSTO
# ==========================

def detectar_rosto(frame):

    global ultimo_tempo

    # OpenCV usa BGR
    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    # Cria imagem MediaPipe
    imagem_mp = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
    )


    # Corrige timestamp
    tempo_atual = int(time.time() * 1000)

    if tempo_atual <= ultimo_tempo:
        tempo_atual = ultimo_tempo + 1

    ultimo_tempo = tempo_atual


    # Detecta rosto
    resultado = detector.detect_for_video(
        imagem_mp,
        timestamp_ms=tempo_atual
    )


    # Desenha pontos do rosto
    if resultado.face_landmarks:

        for rosto in resultado.face_landmarks:

            altura, largura, _ = frame.shape

            for ponto in rosto:

                x = int(ponto.x * largura)
                y = int(ponto.y * altura)


                cv2.circle(
                    frame,
                    (x, y),
                    1,
                    (0, 255, 0),
                    -1
                )


    return frame