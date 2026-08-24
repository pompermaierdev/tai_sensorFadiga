# 👁️ Vigia - Sistema de Detecção de Fadiga e Alerta veicular

O **Vigia** é um sistema de segurança veicular ativa desenvolvido para identificar sinais biomecânicos de fadiga humana em tempo real e intervir de forma automatizada no veículo. Utilizando computação visual no computador e controle embarcado no Arduino Uno, a aplicação monitora o nível de atenção do motorista e aciona atuadores de emergência em cenários críticos.

---

## 🛠️ Arquitetura do Sistema

O projeto funciona de forma integrada entre o software de visão computacional (Python) e o hardware de resposta (Arduino Uno):

1. **Captura e Processamento (Python + MediaPipe):** A câmera captura o rosto do motorista e calcula a métrica **EAR** (*Eye Aspect Ratio*) para identificar o fechamento prolongado dos olhos.
2. **Comunicação Serial:** O Python envia comandos de status via porta COM para o microcontrolador a uma taxa de **9600 baud**.
3. **Atuação no Hardware (Arduino Uno):** O Arduino lê os comandos enviados e controla o rotor (simulando a tração/motor do veículo), LEDs de alerta e alarme sonoro (buzzer).

---

## 📌 Esquema de Pinos (Pinout Arduino Uno)

| Componente | Pino no Arduino | Função |
| :--- | :--- | :--- |
| **Ponte H (IN1)** | Pino 5 | Controle de direção/acionamento do Rotor |
| **Ponte H (IN2)** | Pino 4 | Controle de direção/acionamento do Rotor |
| **Buzzer** | Pino 8 | Sinalizador sonoro de emergência |
| **LED 1 (Aviso)** | Pino 13 | Alerta preventivo de fadiga |
| **LED 2 (Emergência)** | Pino 12 | Alerta crítico de fadiga |

> **Nota:** Certifique-se de que a Ponte H L298N está alimentada com uma fonte externa adequada (ex: bateria de 9V a 12V) e com o pino **GND compartilhado** com o GND do Arduino Uno.

---

## 🚨 Estados de Operação

- **Estado `0` (Normal):** Rotor em funcionamento normal (100%), LEDs apagados e buzzer desligado.
- **Estado `1` (Alerta Leve / Bocejo):** Rotor mantido ligado, LED 1 aceso e beeps curtos no buzzer.
- **Estado `2` (Fadiga Crítica):** Rotor desligado imediatamente (parada de emergência), ambos os LEDs (1 e 2) aceso e alarme sonoro contínuo.

---

## 📦 Dependências e Instalação

### 1. Requisitos do Sistema
- **Python 3.8+**
- **Arduino IDE** (para gravação do firmware)

### 2. Instalação das Bibliotecas Python
Execute no terminal para instalar as dependências necessárias:

```bash
pip install opencv-python mediapipe numpy pyserial