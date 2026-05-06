#include <DHT.h>

#define DHTPIN 10
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

// ===== PIN =====
int gasPin = A0;
int firePin = 11;
int trig = 12;
int echo = 13;
int button = 9;

int buzzer = 7;

int led_safe = 8;
int led_warn = 5;
int led_danger = 6;

// ===== STATE =====
float baseDistance = 0;

int buttonState = LOW;       // trạng thái ổn định
int lastReading = LOW;       // đọc thô
unsigned long lastDebounceTime = 0;
unsigned long debounceDelay = 50;

int stove_on = 0;
// ===== TIME =====
unsigned long lastLoopTime = 0;
unsigned long loopInterval = 3000;

unsigned long absence_time = 0;
unsigned long stove_time = 0;

float lastTemp = 0;
float lastGas = 0;

int result = 0;

void setup() {
  Serial.begin(115200);

  dht.begin();
  pinMode(firePin, INPUT);

  pinMode(trig, OUTPUT);
  pinMode(echo, INPUT);

  pinMode(button, INPUT);

  pinMode(buzzer, OUTPUT);

  pinMode(led_safe, OUTPUT);
  pinMode(led_warn, OUTPUT);
  pinMode(led_danger, OUTPUT);

  delay(2000);
  baseDistance = getDistance();
}

void loop() {

  // ===== ĐỌC NÚT (KHÔNG BỊ MISS) =====
  int reading = digitalRead(button);

  // nếu có thay đổi thì reset timer
  if (reading != lastReading) {
    lastDebounceTime = millis();
  }

  // nếu ổn định đủ lâu
  if ((millis() - lastDebounceTime) > debounceDelay) {

    if (reading != buttonState) {
      buttonState = reading;

      // chỉ toggle khi nhấn xuống
      if (buttonState == HIGH) {
        stove_on = !stove_on;
      }
    }
  }

  lastReading = reading;

  if (Serial.available()) {
    result = Serial.parseInt();
  }

  // ===== 2. LUÔN UPDATE LED =====
  if (result == 2) {
    digitalWrite(led_safe, LOW);
    digitalWrite(led_warn, LOW);
    digitalWrite(led_danger, HIGH);
    digitalWrite(buzzer, HIGH);
  }
  else if (result == 1) {
    digitalWrite(led_safe, LOW);
    digitalWrite(led_warn, HIGH);
    digitalWrite(led_danger, LOW);
    digitalWrite(buzzer, HIGH);
  }
  else {
    digitalWrite(led_safe, HIGH);
    digitalWrite(led_warn, LOW);
    digitalWrite(led_danger, LOW);
    digitalWrite(buzzer, LOW);
  }

  // ===== CHẠY SENSOR MỖI 3s =====
  if (millis() - lastLoopTime >= loopInterval) {
    lastLoopTime = millis();

    // ===== DHT =====
    float temp = dht.readTemperature();
    float delta_temp = temp - lastTemp;
    lastTemp = temp;

    // ===== GAS =====
    int gasValue = analogRead(gasPin);
    float delta_gas = gasValue - lastGas;
    lastGas = gasValue;

    // ===== LỬA =====
    int fireState = !digitalRead(firePin);

    // ===== SIÊU ÂM =====
    float distance = getDistance();

    int human = 0;
    if (distance != -1 && abs(distance - baseDistance) > 1) {
      human = 1;
    }

    // ===== absence TIME =====
    if (human == 0) {
      absence_time += (loopInterval / 1000);
    } else {
      absence_time = 0;
    }

    if (stove_on == 1) {
      stove_time += (loopInterval / 1000);
    } else {
      stove_time = 0;
    }

    // ===== SERIAL OUTPUT =====
    Serial.print(fireState);
    Serial.print(',');
    Serial.print(gasValue);
    Serial.print(',');
    Serial.print(temp);
    Serial.print(',');
    Serial.print(human);
    Serial.print(',');
    Serial.print(stove_on);
    Serial.print(',');
    Serial.print(absence_time);
    Serial.print(',');
    Serial.print(stove_time);
    Serial.print(',');
    Serial.print(delta_gas);
    Serial.print(',');
    Serial.print(delta_temp);
    Serial.print(',');
    Serial.println();
  }
}

// ===== SIÊU ÂM =====
float getDistance() {
  digitalWrite(trig, LOW);
  delayMicroseconds(2);

  digitalWrite(trig, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig, LOW);

  long duration = pulseIn(echo, HIGH, 30000);

  if (duration == 0) return -1;

  float distance = duration * 0.034 / 2;
  return distance;
}
