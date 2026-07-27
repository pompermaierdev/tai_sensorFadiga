import cv2
import time
import math
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
# ÍNDICES DOS LANDMARKS (MediaPipe FaceMesh - 468/478 pontos)
# ==========================
OLHO_DIREITO = [33, 160, 158, 133, 153, 144]   # p1..p6
OLHO_ESQUERDO = [362, 385, 387, 263, 373, 380]  # p1..p6

BOCA_SUPERIOR = 13
BOCA_INFERIOR = 14
BOCA_ESQUERDA = 78
BOCA_DIREITA = 308

# ==========================
# PARÂMETROS DE FADIGA (ajustáveis)
# ==========================
EAR_LIMIAR = 0.21          # abaixo disso, olho considerado fechado
EAR_TEMPO_SONO = 1.5       # segundos com olho fechado -> alerta de sonolência

MAR_LIMIAR = 0.6           # acima disso, boca considerada aberta (bocejo)
MAR_TEMPO_BOCEJO = 1.2     # segundos com boca aberta -> conta como bocejo

JANELA_PERCLOS = 60        # segundos usados para calcular o PERCLOS
PERCLOS_LIMIAR = 0.4       # 40% do tempo com olhos fechados -> alerta

# ==========================
# ESTADO (mantido entre frames)
# ==========================
estado = {
    "olho_fechado_desde": None,
    "boca_aberta_desde": None,
    "bocejos": 0,
    "piscadas": 0,
    "olho_estava_fechado": False,
    "boca_estava_aberta": False,
    "historico_fechado": [],   # lista de (timestamp, olho_fechado_bool)
    "alerta_sonolencia": False,
    "alerta_bocejo": False,
}


def _distancia(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)


def _calcular_ear(landmarks, indices):
    p1, p2, p3, p4, p5, p6 = [landmarks[i] for i in indices]
    vertical1 = _distancia(p2, p6)
    vertical2 = _distancia(p3, p5)
    horizontal = _distancia(p1, p4)
    if horizontal == 0:
        return 0.0
    return (vertical1 + vertical2) / (2.0 * horizontal)


def _calcular_mar(landmarks):
    superior = landmarks[BOCA_SUPERIOR]
    inferior = landmarks[BOCA_INFERIOR]
    esquerda = landmarks[BOCA_ESQUERDA]
    direita = landmarks[BOCA_DIREITA]
    vertical = _distancia(superior, inferior)
    horizontal = _distancia(esquerda, direita)
    if horizontal == 0:
        return 0.0
    return vertical / horizontal


def _atualizar_perclos(agora, olho_fechado):
    historico = estado["historico_fechado"]
    historico.append((agora, olho_fechado))
    # remove entradas fora da janela de tempo
    limite = agora - JANELA_PERCLOS
    while historico and historico[0][0] < limite:
        historico.pop(0)
    if not historico:
        return 0.0
    fechados = sum(1 for _, f in historico if f)
    return fechados / len(historico)


def _desenhar_texto(frame, texto, posicao, cor, escala=0.7, espessura=2):
    cv2.putText(
        frame, texto, posicao,
        cv2.FONT_HERSHEY_SIMPLEX, escala, cor, espessura, cv2.LINE_AA
    )


# ==========================
# DETECTOR DE ROSTO + FADIGA
# ==========================
def detectar_rosto(frame):
    global ultimo_tempo

    # OpenCV usa BGR
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Cria imagem MediaPipe
    imagem_mp = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    # Corrige timestamp
    tempo_atual = int(time.time() * 1000)
    if tempo_atual <= ultimo_tempo:
        tempo_atual = ultimo_tempo + 1
    ultimo_tempo = tempo_atual

    # Detecta rosto
    resultado = detector.detect_for_video(imagem_mp, timestamp_ms=tempo_atual)

    agora = time.time()
    altura, largura, _ = frame.shape

    if not resultado.face_landmarks:
        # sem rosto detectado, reseta contadores de "fechado desde"
        estado["olho_fechado_desde"] = None
        estado["boca_aberta_desde"] = None
        _desenhar_texto(frame, "Rosto nao detectado", (20, 40), (0, 0, 255))
        return frame

    rosto = resultado.face_landmarks[0]

    # Desenha pontos do rosto (mantido do original)
    for ponto in rosto:
        x = int(ponto.x * largura)
        y = int(ponto.y * altura)
        cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

    # ---- Cálculo de métricas de fadiga ----
    ear_dir = _calcular_ear(rosto, OLHO_DIREITO)
    ear_esq = _calcular_ear(rosto, OLHO_ESQUERDO)
    ear_medio = (ear_dir + ear_esq) / 2.0

    mar = _calcular_mar(rosto)

    olho_fechado = ear_medio < EAR_LIMIAR
    boca_aberta = mar > MAR_LIMIAR

    # --- Sonolência (olhos fechados por tempo prolongado) ---
    if olho_fechado:
        if estado["olho_fechado_desde"] is None:
            estado["olho_fechado_desde"] = agora
        duracao_fechado = agora - estado["olho_fechado_desde"]
        estado["alerta_sonolencia"] = duracao_fechado >= EAR_TEMPO_SONO
    else:
        # se o olho estava fechado e abriu, conta como piscada
        if estado["olho_estava_fechado"]:
            estado["piscadas"] += 1
        estado["olho_fechado_desde"] = None
        estado["alerta_sonolencia"] = False

    estado["olho_estava_fechado"] = olho_fechado

    # --- Bocejo (boca aberta por tempo prolongado) ---
    if boca_aberta:
        if estado["boca_aberta_desde"] is None:
            estado["boca_aberta_desde"] = agora
        duracao_boca = agora - estado["boca_aberta_desde"]
        if duracao_boca >= MAR_TEMPO_BOCEJO and not estado["boca_estava_aberta"]:
            estado["bocejos"] += 1
        estado["alerta_bocejo"] = duracao_boca >= MAR_TEMPO_BOCEJO
    else:
        estado["boca_aberta_desde"] = None
        estado["alerta_bocejo"] = False

    estado["boca_estava_aberta"] = boca_aberta

    # --- PERCLOS (percentual do tempo com olhos fechados na janela) ---
    perclos = _atualizar_perclos(agora, olho_fechado)

    # ---- Overlay de informações ----
    cor_ear = (0, 0, 255) if olho_fechado else (0, 255, 0)
    _desenhar_texto(frame, f"EAR: {ear_medio:.2f}", (20, 30), cor_ear, 0.6, 1)
    _desenhar_texto(frame, f"MAR: {mar:.2f}", (20, 55), (255, 255, 0), 0.6, 1)
    _desenhar_texto(frame, f"PERCLOS: {perclos * 100:.0f}%", (20, 80), (255, 255, 0), 0.6, 1)
    _desenhar_texto(frame, f"Piscadas: {estado['piscadas']}  Bocejos: {estado['bocejos']}", (20, 105), (255, 255, 255), 0.6, 1)

    y_alerta = 140
    if estado["alerta_sonolencia"]:
        _desenhar_texto(frame, "ALERTA: SONO DETECTADO!", (20, y_alerta), (0, 0, 255), 0.9, 2)
        y_alerta += 35

    if estado["alerta_bocejo"]:
        _desenhar_texto(frame, "BOCEJO EM ANDAMENTO", (20, y_alerta), (0, 165, 255), 0.8, 2)
        y_alerta += 35

    if perclos >= PERCLOS_LIMIAR:
        _desenhar_texto(frame, "ALERTA: FADIGA (PERCLOS ALTO)", (20, y_alerta), (0, 0, 255), 0.8, 2)

    return frame