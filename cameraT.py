import cv2
import serial
import time
from detec import detectar_rosto  # Importa a função do seu arquivo de detecção

# ==========================================
# CONFIGURAÇÕES E LIMIARES DO SISTEMA VIGIA
# ==========================================
PORTA_SERIAL = 'COM3'   # No Windows ajuste para a sua porta COM (ex: COM3, COM4). No Linux/Mac: '/dev/ttyUSB0'
BAUD_RATE = 115200

EAR_THRESH = 0.18       # Abaixo disso considera olho fechado
FRAMES_CONSEC = 15      # Frames seguidos para confirmar olhos fechados (fadiga)
MAR_THRESH = 0.60       # Acima disso considera bocejo
HEAD_ANGLE_THRESH = 15  # Inclinação de cabeça (graus)

MOSTRAR_JANELA = True

# ==========================================
# INICIALIZAÇÃO DA CONEXÃO SERIAL (ESP32)
# ==========================================
try:
    esp32 = serial.Serial(PORTA_SERIAL, BAUD_RATE, timeout=1)
    time.sleep(2)  # Aguarda a inicialização do ESP32
    print(f"[INFO] Conectado ao ESP32 com sucesso na porta {PORTA_SERIAL}.")
except Exception as e:
    esp32 = None
    print(f"[AVISO] Não foi possível conectar ao ESP32 ({e}). Rodando em modo simulação.")

contador_fadiga = 0
camera = cv2.VideoCapture(0)

try:
    while True:
        ret, frame = camera.read()
        if not ret:
            break

        # Chama sua função original de processamento facial
        frame, ear, mar, head_angle = detectar_rosto(frame)

        comando = '0'  # Estado Padrão: Normal

        if ear is not None:
            # 1. VERIFICAÇÃO DE FADIGA PELOS OLHOS (GRAVE)
            if ear < EAR_THRESH:
                contador_fadiga += 1
                if contador_fadiga >= FRAMES_CONSEC:
                    comando = '2'  # Comando de Emergência para o ESP32
                    if MOSTRAR_JANELA:
                        cv2.putText(frame, "PERIGO: FADIGA DETECTADA!", (10, 170),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            else:
                contador_fadiga = 0

            # 2. VERIFICAÇÃO DE BOCEJO E INCLINAÇÃO (ALERTAS LEVES)
            # Se não estiver no nível de emergência (olhos fechados), checa avisos preventivos
            if comando != '2':
                bocejo = (mar is not None and mar > MAR_THRESH)
                cabeca_inclinada = (head_angle is not None and abs(head_angle) > HEAD_ANGLE_THRESH)

                if bocejo:
                    comando = '1'  # Alerta leve no ESP32
                    if MOSTRAR_JANELA:
                        cv2.putText(frame, "AVISO: BOCEJO DETECTADO", (10, 110),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)

                if cabeca_inclinada:
                    comando = '1'  # Alerta leve no ESP32
                    if MOSTRAR_JANELA:
                        cv2.putText(frame, "AVISO: CABECA INCLINADA", (10, 140),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        else:
            # Nenhum rosto na câmera: reinicia contadores
            contador_fadiga = 0

        # ==========================================
        # ENVIO DO COMANDO SERIAL PARA O ESP32
        # ==========================================
        if esp32 is not None and esp32.is_open:
            esp32.write(comando.encode())  # Envia '0', '1' ou '2' via cabo USB

        if MOSTRAR_JANELA:
            cv2.imshow("Sistema Vigia - Detecção de Fadiga", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

except KeyboardInterrupt:
    pass

finally:
    # Desliga alertas antes de encerrar
    if esp32 is not None and esp32.is_open:
        esp32.write(b'0')
        esp32.close()
    
    camera.release()
    if MOSTRAR_JANELA:
        cv2.destroyAllWindows()
