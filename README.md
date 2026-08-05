# Detector de Fadiga com Buzzer (Raspberry Pi)

`pra rodar no pc use os detec e cameraT, pro raspberry usa os normais`
## Instalação no Raspberry Pi

```bash
sudo apt update
sudo apt install python3-pip python3-venv -y

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

> Se o `pip install mediapipe` falhar, confirme que o Raspberry Pi OS está em **64 bits** — o Pi 3B
> suporta, mas por padrão muitas instalações vêm em 32 bits, e o MediaPipe não tem wheel pra 32 bits
> nesse hardware.

## Ligação do buzzer

- **Buzzer ativo (2 pinos):** `+` no GPIO17 (pino físico 11), `-` no GND (ex: pino físico 9).

Se o pino GPIO17 já estiver em uso por outra coisa, troque o valor de `BUZZER_PIN` em `camera.py`.

## Rodando

```bash
python3 camera.py
```

## Ajustes finos

Em `camera.py`:

- `EAR_THRESH` — quanto menor, mais fechado o olho precisa estar pra contar. Calibre testando com a
  própria câmera e iluminação do carro.
- `FRAMES_CONSEC` — quantos frames seguidos de olho fechado até o alarme disparar. O Pi 3B deve rodar
  o MediaPipe de uns 5 até 15 FPS, então ajuste esse número pensando nesse FPS real (ex: 15 frames ≈ 1–3s).
- `MOSTRAR_JANELA` — deixe `False` se for rodar sem monitor/HDMI conectado (modo headless no carro).
