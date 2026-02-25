#include <Arduino.h>
#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 5
#define RST_PIN 22
#define SCK_PIN 18
#define MISO_PIN 19
#define MOSI_PIN 23

MFRC522 rfid(SS_PIN, RST_PIN);

const int ADC_PIN = 34;
const int touchPin = 14;
const int ledPin = 27;
const int threshold = 35;

int led_logic = 0;
bool lastTouchState = false;

float voltageReader(uint8_t _adc_pin)
{
  float avg_adc = 0;
  for (int i = 0; i < 10; i++)
    avg_adc += (float)analogRead(_adc_pin);
  return (avg_adc / 10.0) * 3.3 / 4095.0;
}

void setup()
{
  Serial.begin(9600);
  pinMode(ledPin, OUTPUT);
  SPI.begin(SCK_PIN, MISO_PIN, MOSI_PIN, SS_PIN);
  rfid.PCD_Init();
  digitalWrite(ledPin, led_logic);
}

void loop()
{
  // รับคำสั่งจาก Web
  if (Serial.available() > 0)
  {
    char cmd = Serial.read();
    if (cmd == 'T')
    {
      led_logic = !led_logic;
      digitalWrite(ledPin, led_logic);
    }
  }

  // อ่านบัตร RFID
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial())
  {
    String uid = "";
    for (byte i = 0; i < rfid.uid.size; i++)
    {
      uid += String(rfid.uid.uidByte[i] < 0x10 ? "0" : "");
      uid += String(rfid.uid.uidByte[i], HEX);
    }
    uid.toUpperCase();
    Serial.print("RFID:");
    Serial.println(uid);
    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();
  }

  // อ่านค่า Touch และส่งข้อมูล Telemetry
  int touchValue = touchRead(touchPin);
  bool currentTouchState = (touchValue <= threshold);
  String touchStatus = currentTouchState ? "TOUCH" : "NO_TOUCH";

  if (currentTouchState && !lastTouchState)
  {
    led_logic = !led_logic;
    digitalWrite(ledPin, led_logic);
    delay(50);
  }
  lastTouchState = currentTouchState;

  float voltage = voltageReader(ADC_PIN);

  // รูปแบบสำคัญ: DATA:LED,VOLTAGE,TOUCH
  Serial.print("DATA:");
  Serial.print(led_logic);
  Serial.print(",");
  Serial.print(voltage);
  Serial.print(",");
  Serial.println(touchStatus);

  delay(150);
}