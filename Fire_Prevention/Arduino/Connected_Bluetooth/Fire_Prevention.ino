#include <SoftwareSerial.h>

// BLE 모듈 RX, TX 핀 설정 (아두이노에서 반대 RXD = 3, TXD = 2)
SoftwareSerial bluetooth(2, 3);

int pirPin = 6;
int pirState = 0;
int buzzerPin = 8;
bool fireCheck = false;

// BLE 연결 (라즈베리파이 - 아두이노)
void setup() {
  Serial.begin(9600);
  bluetooth.begin(9600);

  pinMode(pirPin, INPUT);
}


void loop() {
  if (Serial.available()) {
    bluetooth.write(Serial.read());
  }
  
  if (bluetooth.available()) {

    // 라즈베리 파이로부터 데이터 수신
    String data = bluetooth.readString();
    Serial.println(data);

    // 라즈베리파이 온도 정보를 이용한 PIR 동작
    if(data == "turn on") {
      Serial.println("A : turn on");
      fireCheck = true;
    }
    // PIR 종료
    else if(data == "turn off") {
      Serial.println("A : turn off");
      fireCheck = false;
    }
  }

  // 화재 감지 및 PIR 감지
  if(fireCheck == true) {

    // PIR 센서 감지 
    pirState = digitalRead(pirPin);

    // PIR 감지된 경우 Buzzer 동작
    if(pirState == HIGH) {
      Serial.println("PIR Detected");
      tone(buzzerPin, 550);
      delay(500);

      // Buzzer 종료
      noTone(buzzerPin);
      delay(1000);
    }
  }
}