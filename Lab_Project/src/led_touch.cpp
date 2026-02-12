#include "BluetoothSerial.h"

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

BluetoothSerial SerialBT;
const int ADC_PIN = 34;
const int touchPin = 14;
const int ledPin = 27;
const int threshold = 40; // Need to be tuned
int touchValue;
int led_logic = 0;
float voltageReader(uint8_t _adc_pin, uint8_t _window_size)
{
  float _avg_adc = 0;
  float _volatge = 0;
  uint8_t _index = 0;
  do
  {
    _avg_adc += (float)analogRead(_adc_pin);
    _index += 1;
  } while (_index < _window_size);
  _avg_adc /= _index;
  _avg_adc = _avg_adc * 1 + 0.00;
  // Calculate the volatge from the slide, page 9
  _volatge = (_avg_adc * 3.3) / 4095.0;
  return _volatge;
}
void setup()
{
  Serial.begin(9600);
  SerialBT.begin("C2R2_GOONER"); // Bluetooth device name
  Serial.println("The device started, now you can pair it with bluetooth!");
  pinMode(ledPin, OUTPUT);
}

void loop()
{
  touchValue = touchRead(touchPin);
  float currentVoltage = voltageReader(ADC_PIN, 10);

  // Detect touch
  String touchStatus = "NO_TOUCH";

  if (touchValue <= threshold)
  {
    led_logic = !led_logic;
    digitalWrite(ledPin, led_logic);

    touchStatus = "TOUCH";
  }

  // ✅ Send CSV line: led_logic,voltage,status
  SerialBT.printf("%d,%.2f,%s\n", led_logic, currentVoltage, touchStatus.c_str());
  Serial.printf("%d,%.2f,%s\n", led_logic, currentVoltage, touchStatus.c_str());

  delay(300);
}