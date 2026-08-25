// parte que deve ser rodada no arduino IDE em c++

// definicao dos pinos
const int PIN_BUZZER = 10; //sinal do buzzer
const int PIN_LED1   = 12; //led de atencao
const int PIN_LED2   = 13; // led de fadiga critica

void setup() {
  // tempo de comunicao com o computador
  Serial.begin(9600);

  // configura od pinos de saida
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_LED1, OUTPUT);
  pinMode(PIN_LED2, OUTPUT);

  //comeca com tudo desligado
  noTone(PIN_BUZZER);
  digitalWrite(PIN_BUZZER, LOW);
  digitalWrite(PIN_LED1, LOW);
  digitalWrite(PIN_LED2, LOW);
}

void loop() {
  //verifica se algum comando foi enviado
  if (Serial.available() > 0) {
    char comando = Serial.read();

    if (comando == '0') {
      // 0: normal (olhos abertos) tudo desligado
      noTone(PIN_BUZZER);
      digitalWrite(PIN_BUZZER, LOW);
      digitalWrite(PIN_LED1, LOW);
      digitalWrite(PIN_LED2, LOW);
    } 
    else if (comando == '1') {
      // 1: atencao: piscada longa liga apenas um led
      noTone(PIN_BUZZER);
      digitalWrite(PIN_BUZZER, LOW);
      digitalWrite(PIN_LED1, HIGH);
      digitalWrite(PIN_LED2, LOW);
    } 
    else if (comando == '2') {
      // 2: "dormiu" : toca o buzzer e acende os dois leds
      tone(PIN_BUZZER, 1200);       // emite tom de 1200 Hz
      digitalWrite(PIN_LED1, HIGH);
      digitalWrite(PIN_LED2, HIGH);
    }
  }
}