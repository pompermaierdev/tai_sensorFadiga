import cv2
from detec import detectar_rosto

# ==========================
# CONFIGURAÇÃO
# ==========================
BUZZER_PIN = 17        # GPIO do buzzer (pino físico 11 na maioria das pinagens)
EAR_THRESH = 0.25       # abaixo disso considera o olho fechado (calibre testando)
FRAMES_CONSEC = 15      # frames seguidos de olho fechado até soar o alarme
MOSTRAR_JANELA = True   # False se for rodar headless (sem monitor/HDMI)

# ==========================
# BUZZER (real no Pi, simulado em notebook/PC sem GPIO)
# ==========================
try:
    from gpiozero import Buzzer
    buzzer = Buzzer(BUZZER_PIN)
    print("[INFO] Buzzer real (GPIO) detectado.")
except Exception:
    class BuzzerFake:
        """Simula o buzzer quando não há GPIO disponível (ex: notebook/PC)."""
        def __init__(self):
            self._ligado = False

        def on(self):
            if not self._ligado:
                print("[BUZZER] LIGADO (simulado)")
            self._ligado = True

        def off(self):
            if self._ligado:
                print("[BUZZER] desligado (simulado)")
            self._ligado = False

    buzzer = BuzzerFake()
    print("[INFO] GPIO não encontrado — usando buzzer simulado (modo notebook/PC).")
contador = 0

camera = cv2.VideoCapture(0)

try:
    while True:
        ret, frame = camera.read()
        if not ret:
            break

        frame, ear = detectar_rosto(frame)

        if ear is not None:
            if MOSTRAR_JANELA:
                cv2.putText(frame, f"EAR: {ear:.2f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            if ear < EAR_THRESH:
                contador += 1
                if contador >= FRAMES_CONSEC:
                    buzzer.on()
                    if MOSTRAR_JANELA:
                        cv2.putText(frame, "FADIGA DETECTADA!", (10, 60),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            else:
                contador = 0
                buzzer.off()
        else:
            contador = 0
            buzzer.off()

        if MOSTRAR_JANELA:
            cv2.imshow("Detector de Fadiga", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

except KeyboardInterrupt:
    pass

finally:
    buzzer.off()
    camera.release()
    if MOSTRAR_JANELA:
        cv2.destroyAllWindows()