import cv2
import time
import math
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os


modelo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "face_landmarker.task")


opcoes = vision.FaceLandmarkerOptions(
    base_options=python.BaseOptions(model_asset_path=modelo),
    running_mode=vision.RunningMode.VIDEO,
    num_faces=1
)


detector = vision.FaceLandmarker.create_from_options(opcoes)


ultimo_tempo = 0


OLHO_ESQ = [362, 385, 387, 263, 373, 380]
OLHO_DIR = [33, 160, 158, 133, 153, 144]



BOCA = {
    "esq": 61,
    "dir": 291,
    "sup1": 13,
    "inf1": 14,
    "sup2": 81,
    "inf2": 178,
    "sup3": 311,
    "inf3": 402,
}




def distancia(p1, p2):
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2) ** 0.5



#calulo do EAR (dos olhos)
def calcular_ear(pontos, indices, largura, altura):
    coords = [(pontos[i].x * largura, pontos[i].y * altura) for i in indices]


    p1, p2, p3, p4, p5, p6 = coords


    A = distancia(p2, p6)
    B = distancia(p3, p5)
    C = distancia(p1, p4)


    return (A + B) / (2.0 * C)



# MAR (calcullo da boca)
def calcular_mar(pontos, largura, altura):
    pts = {}


    for nome, indice in BOCA.items():
        pts[nome] = (
            pontos[indice].x * largura,
            pontos[indice].y * altura
        )


    A = distancia(pts["sup1"], pts["inf1"])
    B = distancia(pts["sup2"], pts["inf2"])
    C = distancia(pts["sup3"], pts["inf3"])
    D = distancia(pts["esq"], pts["dir"])


    return (A + B + C) / (2 * D)



#calculo da inclinação da cabeça
def calcular_head_angle(pontos, largura, altura):
    olho_esq = pontos[33]
    olho_dir = pontos[263]


    x1 = olho_esq.x * largura
    y1 = olho_esq.y * altura


    x2 = olho_dir.x * largura
    y2 = olho_dir.y * altura


    angulo = math.degrees(math.atan2(y2 - y1, x2 - x1))


    return angulo



#detecta o rosto
def detectar_rosto(frame):
    global ultimo_tempo


    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


    imagem_mp = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
    )


    tempo_atual = int(time.time() * 1000)


    if tempo_atual <= ultimo_tempo:
        tempo_atual = ultimo_tempo + 1


    ultimo_tempo = tempo_atual


    resultado = detector.detect_for_video(
        imagem_mp,
        timestamp_ms=tempo_atual
    )


    ear = None
    mar = None
    head_angle = None


    if resultado.face_landmarks:


        altura, largura, _ = frame.shape


        for rosto in resultado.face_landmarks:


            for ponto in rosto:
                x = int(ponto.x * largura)
                y = int(ponto.y * altura)


                cv2.circle(frame, (x, y), 1, (0,255,0), -1)


            ear_esq = calcular_ear(rosto, OLHO_ESQ, largura, altura)
            ear_dir = calcular_ear(rosto, OLHO_DIR, largura, altura)


            ear = (ear_esq + ear_dir)/2


            mar = calcular_mar(rosto, largura, altura)


            head_angle = calcular_head_angle(rosto, largura, altura)


            cv2.putText(frame,
                        f"EAR: {ear:.2f}",
                        (10,30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0,255,0),
                        2)


            cv2.putText(frame,
                        f"MAR: {mar:.2f}",
                        (10,55),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255,255,0),
                        2)


            cv2.putText(frame,
                        f"Head: {head_angle:.1f}",
                        (10,80),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0,255,255),
                        2)


    return frame, ear, mar, head_angle
