
const int PIN_BUZZER = 10; 
const int PIN_LED1   = 12; 
const int PIN_LED2   = 13; 

void setup() {
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_LED1, OUTPUT);
  pinMode(PIN_LED2, OUTPUT);
}

void loop() {

  digitalWrite(PIN_LED1, HIGH);
  digitalWrite(PIN_LED2, HIGH);
  tone(PIN_BUZZER, 1000);
  delay(500);

 
  digitalWrite(PIN_LED1, LOW);
  digitalWrite(PIN_LED2, LOW);
  noTone(PIN_BUZZER);
  digitalWrite(PIN_BUZZER, LOW);
  delay(500);
}