import cv2
import time
import math
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from datetime import datetime
import json

# ==========================
# MODELO E DETECTOR
# ==========================
MODELO = "face_landmarker.task"

opcoes = vision.FaceLandmarkerOptions(
    base_options=python.BaseOptions(model_asset_path=MODELO),
    running_mode=vision.RunningMode.VIDEO,
    num_faces=1,
)
detector = vision.FaceLandmarker.create_from_options(opcoes)

ultimo_tempo = 0  # último timestamp enviado ao detector (precisa ser crescente)

# ==========================
# ÍNDICES DOS LANDMARKS
# ==========================
OLHO_DIREITO = [33, 160, 158, 133, 153, 144]
OLHO_ESQUERDO = [362, 385, 387, 263, 373, 380]

BOCA_SUPERIOR = 13
BOCA_INFERIOR = 14
BOCA_ESQUERDA = 78
BOCA_DIREITA = 308

# ==========================
# PARÂMETROS
# ==========================
EAR_LIMIAR = 0.21
EAR_TEMPO_SONO = 2.0

MAR_LIMIAR = 0.6
MAR_TEMPO_BOCEJO = 0.5

JANELA_PERCLOS = 30
PERCLOS_LIMIAR = 0.3

# ==========================
# ESTADO (entre frames) E ESTATÍSTICAS
# ==========================
estado = {
    "olho_fechado_desde": None,
    "boca_aberta_desde": None,
    "piscadas": 0,
    "olho_estava_fechado": False,
    "bocejo_contado": False,
    "historico_fechado": [],
    "alerta_sonolencia": False,
    "sinal_bocejo": False,
    "alerta_perclos_anterior": False,
    "ultimo_tempo_frame": None,
}

estatisticas = {
    "inicio": time.time(),
    "total_piscadas": 0,
    "total_bocejos": 0,
    "total_fadiga": 0,
    "total_sonolencia": 0,
    "duracao_sonolencia": 0.0,
    "amostras_perclos": [],
}

# ==========================
# FUNÇÕES AUXILIARES
# ==========================
def _ponto_px(landmark, largura, altura):
    """Converte um landmark normalizado (0-1) para coordenadas em PIXELS.

    Importante: usar direto landmark.x/landmark.y (normalizados) para medir
    distâncias dá um resultado errado sempre que a imagem não é quadrada
    (ex.: webcam 640x480), porque x e y ficam em escalas diferentes.
    Isso distorcia o EAR e fazia o "olho fechado" nunca ser detectado
    corretamente. Convertendo para pixels antes de medir, o problema some.
    """
    return landmark.x * largura, landmark.y * altura


def _distancia(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def _calcular_ear(landmarks, indices, largura, altura):
    pts = [_ponto_px(landmarks[i], largura, altura) for i in indices]
    p1, p2, p3, p4, p5, p6 = pts
    vertical = _distancia(p2, p6) + _distancia(p3, p5)
    horizontal = _distancia(p1, p4)
    if horizontal == 0:
        return 0.0
    return vertical / (2.0 * horizontal)


def _calcular_mar(landmarks, largura, altura):
    superior = _ponto_px(landmarks[BOCA_SUPERIOR], largura, altura)
    inferior = _ponto_px(landmarks[BOCA_INFERIOR], largura, altura)
    esquerda = _ponto_px(landmarks[BOCA_ESQUERDA], largura, altura)
    direita = _ponto_px(landmarks[BOCA_DIREITA], largura, altura)
    horizontal = _distancia(esquerda, direita)
    if horizontal == 0:
        return 0.0
    return _distancia(superior, inferior) / horizontal


def _atualizar_perclos(agora, olho_fechado):
    historico = estado["historico_fechado"]
    historico.append((agora, olho_fechado))
    limite = agora - JANELA_PERCLOS
    while historico and historico[0][0] < limite:
        historico.pop(0)
    if not historico:
        return 0.0
    fechados = sum(1 for _, f in historico if f)
    return fechados / len(historico)


def _desenhar_texto(frame, texto, posicao, cor, escala=0.7, espessura=2):
    cv2.putText(frame, texto, posicao, cv2.FONT_HERSHEY_SIMPLEX, escala, cor, espessura, cv2.LINE_AA)


# ==========================
# RELATÓRIO FINAL (chamar sempre que o programa for encerrado,
# tanto por 'q' quanto por Ctrl+C)
# ==========================
def imprimir_estatisticas():
    fim = time.time()
    duracao_total = fim - estatisticas["inicio"]

    perclos_medio = 0.0
    if estatisticas["amostras_perclos"]:
        perclos_medio = sum(estatisticas["amostras_perclos"]) / len(estatisticas["amostras_perclos"])

    risco = "BAIXO"
    if estatisticas["total_fadiga"] > 5 or estatisticas["total_sonolencia"] > 3:
        risco = "ALTO"
    elif estatisticas["total_fadiga"] > 2 or estatisticas["total_sonolencia"] > 1:
        risco = "MEDIO"

    linhas = [
        ("Duracao total", f"{duracao_total:.1f}s ({duracao_total / 60:.1f} min)"),
        ("Piscadas", str(estatisticas["total_piscadas"])),
        ("Bocejos", str(estatisticas["total_bocejos"])),
        ("Alertas de fadiga (PERCLOS)", str(estatisticas["total_fadiga"])),
        ("Alertas de sonolencia", str(estatisticas["total_sonolencia"])),
        ("Tempo em sonolencia", f"{estatisticas['duracao_sonolencia']:.1f}s"),
        ("PERCLOS medio", f"{perclos_medio * 100:.1f}%"),
        ("Nivel de risco", risco),
    ]

    largura_col1 = max(len(rotulo) for rotulo, _ in linhas) + 2
    largura_col2 = max(len(valor) for _, valor in linhas) + 2
    borda = "+" + "-" * largura_col1 + "+" + "-" * largura_col2 + "+"

    print("\n" + borda)
    print("| " + "RELATORIO FINAL - MONITORAMENTO DE FADIGA".ljust(largura_col1 + largura_col2 - 1) + "|")
    print(borda)
    for rotulo, valor in linhas:
        print("| " + rotulo.ljust(largura_col1 - 1) + "| " + valor.ljust(largura_col2 - 1) + "|")
    print(borda)

    nome_arquivo = f"relatorio_fadiga_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(nome_arquivo, "w") as f:
            json.dump({rotulo: valor for rotulo, valor in linhas}, f, indent=2, ensure_ascii=False)
        print(f"Relatorio salvo em: {nome_arquivo}")
    except OSError as e:
        print(f"Nao foi possivel salvar o relatorio: {e}")


# ==========================
# FUNÇÃO PRINCIPAL DE DETECÇÃO
# ==========================
def detectar_rosto(frame):
    global ultimo_tempo

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    imagem_mp = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    tempo_atual = int(time.time() * 1000)
    if tempo_atual <= ultimo_tempo:
        tempo_atual = ultimo_tempo + 1
    ultimo_tempo = tempo_atual

    resultado = detector.detect_for_video(imagem_mp, timestamp_ms=tempo_atual)

    agora = time.time()
    altura, largura, _ = frame.shape

    delta_frame = 0.0
    if estado["ultimo_tempo_frame"] is not None:
        delta_frame = max(0.0, agora - estado["ultimo_tempo_frame"])
    estado["ultimo_tempo_frame"] = agora

    if not resultado.face_landmarks:
        estado["olho_fechado_desde"] = None
        estado["boca_aberta_desde"] = None
        estado["bocejo_contado"] = False
        estado["sinal_bocejo"] = False
        estado["alerta_sonolencia"] = False
        _desenhar_texto(frame, "Rosto nao detectado", (20, 40), (0, 0, 255))
        return frame

    rosto = resultado.face_landmarks[0]

    for ponto in rosto:
        x, y = int(ponto.x * largura), int(ponto.y * altura)
        cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

    # ---- Métricas (agora calculadas em pixels, e não mais direto em
    # coordenadas normalizadas -- essa era a causa do olho fechado
    # não ser detectado) ----
    ear_dir = _calcular_ear(rosto, OLHO_DIREITO, largura, altura)
    ear_esq = _calcular_ear(rosto, OLHO_ESQUERDO, largura, altura)
    ear_medio = (ear_dir + ear_esq) / 2.0
    mar = _calcular_mar(rosto, largura, altura)

    olho_fechado = ear_medio < EAR_LIMIAR
    boca_aberta = mar > MAR_LIMIAR

    # --- Sonolência ---
    if olho_fechado:
        if estado["olho_fechado_desde"] is None:
            estado["olho_fechado_desde"] = agora
        duracao_fechado = agora - estado["olho_fechado_desde"]
        if duracao_fechado >= EAR_TEMPO_SONO and not estado["alerta_sonolencia"]:
            estatisticas["total_sonolencia"] += 1
        estado["alerta_sonolencia"] = duracao_fechado >= EAR_TEMPO_SONO
        if estado["alerta_sonolencia"]:
            estatisticas["duracao_sonolencia"] += delta_frame
    else:
        if estado["olho_estava_fechado"]:
            estado["piscadas"] += 1
            estatisticas["total_piscadas"] += 1
        estado["olho_fechado_desde"] = None
        estado["alerta_sonolencia"] = False

    estado["olho_estava_fechado"] = olho_fechado

    # --- Bocejo ---
    if boca_aberta:
        if estado["boca_aberta_desde"] is None:
            estado["boca_aberta_desde"] = agora
        duracao_boca = agora - estado["boca_aberta_desde"]
        if duracao_boca >= MAR_TEMPO_BOCEJO:
            estado["sinal_bocejo"] = True
            if not estado["bocejo_contado"]:
                estatisticas["total_bocejos"] += 1
                estado["bocejo_contado"] = True
    else:
        estado["boca_aberta_desde"] = None
        estado["sinal_bocejo"] = False
        estado["bocejo_contado"] = False

    # --- PERCLOS ---
    perclos = _atualizar_perclos(agora, olho_fechado)
    estatisticas["amostras_perclos"].append(perclos)
    if len(estatisticas["amostras_perclos"]) > 1000:
        estatisticas["amostras_perclos"] = estatisticas["amostras_perclos"][-1000:]

    alerta_perclos = perclos >= PERCLOS_LIMIAR
    if alerta_perclos and not estado["alerta_perclos_anterior"]:
        estatisticas["total_fadiga"] += 1
    estado["alerta_perclos_anterior"] = alerta_perclos

    # ---- Overlay ----
    y_pos = 30
    cor_ear = (0, 0, 255) if olho_fechado else (0, 255, 0)
    _desenhar_texto(frame, f"EAR: {ear_medio:.2f}", (20, y_pos), cor_ear, 0.6, 1); y_pos += 25
    _desenhar_texto(frame, f"MAR: {mar:.2f}", (20, y_pos), (255, 255, 0), 0.6, 1); y_pos += 25
    _desenhar_texto(frame, f"PERCLOS: {perclos * 100:.0f}%", (20, y_pos), (255, 255, 0), 0.6, 1); y_pos += 25
    _desenhar_texto(frame, f"Piscadas: {estado['piscadas']}", (20, y_pos), (255, 255, 255), 0.6, 1); y_pos += 25
    _desenhar_texto(frame, f"Bocejos: {estatisticas['total_bocejos']}", (20, y_pos), (255, 255, 255), 0.6, 1); y_pos += 35

    if estado["alerta_sonolencia"]:
        _desenhar_texto(frame, "ALERTA CRITICO: SONOLENCIA!", (20, y_pos), (0, 0, 255), 0.9, 2); y_pos += 35
    if alerta_perclos:
        _desenhar_texto(frame, "ALERTA: FADIGA ACUMULADA", (20, y_pos), (0, 0, 255), 0.8, 2); y_pos += 35
    if estado["sinal_bocejo"]:
        _desenhar_texto(frame, "SINAL: BOCEJO DETECTADO", (20, y_pos), (0, 165, 255), 0.7, 2); y_pos += 35

    return frame