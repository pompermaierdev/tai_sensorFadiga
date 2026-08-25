// para rodar no arduino uno
// ponte H L298N (Controle do motor)
const int PIN_IN1 = 4;     // in1 da Ponte H
const int PIN_IN2 = 5;     // in2 da Ponte H

// alertas na Protoboard
const int PIN_BUZZER = 10; 
const int PIN_LED1 = 12;  
const int PIN_LED2 = 13;  

void setup() {
  Serial.begin(9600);

  pinMode(PIN_IN1, OUTPUT);
  pinMode(PIN_IN2, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_LED1, OUTPUT);
  pinMode(PIN_LED2, OUTPUT);

  // estado inicial: motor LIGADO, LEDs e Buzzer DESLIGADOS
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
      // estado 0: normal = liga motor, desliga os avisos
      digitalWrite(PIN_IN1, HIGH);
      digitalWrite(PIN_IN2, LOW);
      digitalWrite(PIN_LED1, LOW);
      digitalWrite(PIN_LED2, LOW);
      digitalWrite(PIN_BUZZER, LOW);
    } 
    else if (comando == '1') {
      // estado 1: ATENÇÃO = mantem o motor, liga LED 1
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
