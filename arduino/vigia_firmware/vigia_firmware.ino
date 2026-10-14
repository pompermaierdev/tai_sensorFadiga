// ===== MOTOR 1 (ponte H) =====
const int PIN_IN1 = 9;   // PWM
const int PIN_IN2 = 5;   // PWM
// ===== MOTOR 2 (ponte H) =====
const int PIN_IN3 = 4;   // sem PWM
const int PIN_IN4 = 6;   // PWM

// ===== ALERTAS =====
const int PIN_BUZZER = 10;
const int PIN_LED1   = 12;
const int PIN_LED2   = 13;

char estadoAtual = '0';
int velocidadeMotor = 255;

unsigned long tempoLED = 0;
unsigned long tempoRampa = 0;
bool estadoLEDs = LOW;

// Gira os dois motores para frente com a velocidade dada
void moverMotores(int vel) {
  // Motor 1: IN1 recebe PWM, IN2 fica LOW
  analogWrite(PIN_IN1, vel);
  digitalWrite(PIN_IN2, LOW);   // pino 5 tem PWM; usar digitalWrite LOW é ok
  // Motor 2: IN4 recebe PWM, IN3 fica LOW (pino 4 sem PWM, só direção)
  digitalWrite(PIN_IN3, LOW);
  analogWrite(PIN_IN4, vel);
}

void setup() {
  Serial.begin(9600);
  pinMode(PIN_IN1, OUTPUT);
  pinMode(PIN_IN2, OUTPUT);
  pinMode(PIN_IN3, OUTPUT);
  pinMode(PIN_IN4, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_LED1, OUTPUT);
  pinMode(PIN_LED2, OUTPUT);

  moverMotores(255);
}

void loop() {
  if (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '0' || c == '1' || c == '2') estadoAtual = c;
  }

  unsigned long agora = millis();

  if (estadoAtual == '0') {            // acordado
    velocidadeMotor = 255;
    moverMotores(velocidadeMotor);
    noTone(PIN_BUZZER);
    digitalWrite(PIN_BUZZER, LOW);
    digitalWrite(PIN_LED1, LOW);
    digitalWrite(PIN_LED2, LOW);
    estadoLEDs = LOW;
  }
  else if (estadoAtual == '1') {       // sono leve
    velocidadeMotor = 255;
    moverMotores(velocidadeMotor);
    tone(PIN_BUZZER, 1000);
    digitalWrite(PIN_LED1, LOW);
    digitalWrite(PIN_LED2, LOW);
  }
  else if (estadoAtual == '2') {       // dormindo
    tone(PIN_BUZZER, 1200);

    // desacelera 5 unidades a cada 30 ms, sem travar o loop
    if (velocidadeMotor > 0 && agora - tempoRampa >= 30) {
      tempoRampa = agora;
      velocidadeMotor -= 5;
      if (velocidadeMotor < 0) velocidadeMotor = 0;
      moverMotores(velocidadeMotor);
    }

    // pisca-alerta
    if (agora - tempoLED >= 300) {
      tempoLED = agora;
      estadoLEDs = !estadoLEDs;
      digitalWrite(PIN_LED1, estadoLEDs);
      digitalWrite(PIN_LED2, estadoLEDs);
    }
  }
}