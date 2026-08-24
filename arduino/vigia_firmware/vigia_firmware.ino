// ==========================================================
// FIRMWARE CORRIGIDO PARA A SUA MONTAGEM FÍSICA
// ==========================================================

// Ponte H L298N (Controle do Rotor)
const int PIN_IN1 = 4;     // Pino 4 do Arduino -> IN1 da Ponte H
const int PIN_IN2 = 5;     // Pino 5 do Arduino -> IN2 da Ponte H

// Alertas na Protoboard
const int PIN_BUZZER = 10; // Pino 10 do Arduino -> Buzzer
const int PIN_LED1 = 12;   // Pino 12 do Arduino -> LED 1
const int PIN_LED2 = 13;   // Pino 13 do Arduino -> LED 2

void setup() {
  Serial.begin(9600);

  pinMode(PIN_IN1, OUTPUT);
  pinMode(PIN_IN2, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_LED1, OUTPUT);
  pinMode(PIN_LED2, OUTPUT);

  // ESTADO INICIAL: Motor LIGADO, LEDs e Buzzer DESLIGADOS
  digitalWrite(PIN_IN1, HIGH);
  digitalWrite(PIN_IN2, LOW);
  digitalWrite(PIN_LED1, LOW);
  digitalWrite(PIN_LED2, LOW);
  digitalWrite(PIN_BUZZER, LOW);
}

void loop() {
  if (Serial.available() > 0) {
    char comando = Serial.read();

    if (comando == '0') {
      // ESTADO 0: NORMAL -> Liga Rotor, Desliga Avisos
      digitalWrite(PIN_IN1, HIGH);
      digitalWrite(PIN_IN2, LOW);
      digitalWrite(PIN_LED1, LOW);
      digitalWrite(PIN_LED2, LOW);
      digitalWrite(PIN_BUZZER, LOW);
    } 
    else if (comando == '1') {
      // ESTADO 1: ATENÇÃO -> Mantém Rotor, Liga LED 1
      digitalWrite(PIN_IN1, HIGH);
      digitalWrite(PIN_IN2, LOW);
      digitalWrite(PIN_LED1, HIGH);
      digitalWrite(PIN_LED2, LOW);
      digitalWrite(PIN_BUZZER, LOW);
    } 
    else if (comando == '2') {
      // ESTADO 2: FADIGA CRÍTICA -> PARA ROTOR, LIGA BUZZER E LEDS
      digitalWrite(PIN_IN1, LOW);  // DESLIGA MOTOR
      digitalWrite(PIN_IN2, LOW);
      digitalWrite(PIN_LED1, HIGH); // LIGA LED 1
      digitalWrite(PIN_LED2, HIGH); // LIGA LED 2
      digitalWrite(PIN_BUZZER, HIGH); // LIGA BUZZER
    }
  }
}