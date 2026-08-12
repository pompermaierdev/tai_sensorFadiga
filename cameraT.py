import cv2
from detec import detectar_rosto



# CONFIGURAÇÃO
BUZZER_PIN = 17
EAR_THRESH = 0.18
FRAMES_CONSEC = 15
MOSTRAR_JANELA = True


# Limiares das novas detecções
MAR_THRESH = 0.60
HEAD_ANGLE_THRESH = 15



# BUZZER
try:
    from gpiozero import Buzzer


    buzzer = Buzzer(BUZZER_PIN)
    print("[INFO] Buzzer real (GPIO) detectado.")


except Exception:


    class BuzzerFake:
        """Simula o buzzer quando não há GPIO disponível."""


        def __init__(self):
            self._ligado = False


        def on(self):
            if not self._ligado:
                print("[BUZZER] LIGADO (simulado)")
            self._ligado = True


        def off(self):
            if self._ligado:
                print("[BUZZER] DESLIGADO (simulado)")
            self._ligado = False


    buzzer = BuzzerFake()
    print("[INFO] GPIO não encontrado — usando buzzer simulado.")


contador = 0


camera = cv2.VideoCapture(0)


try:
    while True:


        ret, frame = camera.read()


        if not ret:
            break


        # Agora recebe EAR, MAR e ângulo da cabeça
        frame, ear, mar, head_angle = detectar_rosto(frame)


        if ear is not None:


           
            # Fadiga pelos olhos
            if ear < EAR_THRESH:
                contador += 1


                if contador >= FRAMES_CONSEC:
                    buzzer.on()


                    cv2.putText(
                        frame,
                        "FADIGA DETECTADA!",
                        (10, 170),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 0, 255),
                        2
                    )
            else:
                contador = 0
                buzzer.off()


            
            # Bocejo
            if mar is not None and mar > MAR_THRESH:


                cv2.putText(
                    frame,
                    "BOCEJO DETECTADO",
                    (10, 110),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 0, 255),
                    2
                )



            # Inclinação da cabeça
            if head_angle is not None and abs(head_angle) > HEAD_ANGLE_THRESH:


                cv2.putText(
                    frame,
                    "CABECA INCLINADA",
                    (10, 140),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 255),
                    2
                )


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
