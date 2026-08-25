//codigo pra rodar no arduino IDE ou seja o codigo do hardware

const int PIN_IN1 = 5;  // velocidade do motor
const int PIN_IN2 = 4;  // direcao do motor

// dos alertas 
const int PIN_BUZZER = 10; //sinal do buzzer
const int PIN_LED1   = 12;
const int PIN_LED2   = 13;

char estadoAtual = '0';
int velocidadeMotor = 255; // vel em que o motor comeca

//  tempo do pisca-alerta 
unsigned long tempoAnteriorLED = 0;
bool estadoLEDs = LOW;

void setup() {
  Serial.begin(9600);//tempo de comunicacao serial
  // configura od pinos de saida
  pinMode(PIN_IN1, OUTPUT);
  pinMode(PIN_IN2, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_LED1, OUTPUT);
  pinMode(PIN_LED2, OUTPUT);

  // inicia com o motor rodando mas os alertas desligados 
  digitalWrite(PIN_IN2, LOW);
  analogWrite(PIN_IN1, 255);
}

void loop() {
  // verifica se algum comando foi enviado
  if (Serial.available() > 0) {
    estadoAtual = Serial.read();
  }

  //0 : acordado
  if (estadoAtual == '0') {
    velocidadeMotor = 255; 
    analogWrite(PIN_IN1, velocidadeMotor); // motor em 100%
    
    noTone(PIN_BUZZER);
    digitalWrite(PIN_BUZZER, LOW);
    digitalWrite(PIN_LED1, LOW);
    digitalWrite(PIN_LED2, LOW);
  } 


  //1 : sono leve 
  
  else if (estadoAtual == '1') {
    velocidadeMotor = 255;
    analogWrite(PIN_IN1, velocidadeMotor); // motor mantido ligado
    
    tone(PIN_BUZZER, 1000);                // dispara o Buzzer
    digitalWrite(PIN_LED1, LOW);           // LEDs continuam desligados
    digitalWrite(PIN_LED2, LOW);
  } 

  // 2 : dormindo 

  else if (estadoAtual == '2') {
    tone(PIN_BUZZER, 1200); // buzzer continua apitando

    //reduz a vel do motor aos poucos ate parar
    if (velocidadeMotor > 0) {
      velocidadeMotor -= 5; 
      if (velocidadeMotor < 0) velocidadeMotor = 0;
      analogWrite(PIN_IN1, velocidadeMotor);
      delay(30); // pra deixar a paraada mais suave
    }

    //o pisca alerta
    if (millis() - tempoAnteriorLED >= 300) {
      tempoAnteriorLED = millis();
      estadoLEDs = !estadoLEDs; // inverte o estado (ON/OFF)
      digitalWrite(PIN_LED1, estadoLEDs);
      digitalWrite(PIN_LED2, estadoLEDs);
    }
  }
}