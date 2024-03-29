#include <SPI.h>
#include <RH_RF95.h>
#include <GY91.h>
#include <Adafruit_SCD30.h>

const uint8_t CS_PIN = 24;
const uint8_t INT_PIN = 25;
const float tx_freq = 433.600; // in Mhz
const long sbw = 62500; // in kHz
const uint8_t sf = 8;
const uint8_t crc = 7; //denominator, final value is 4/7
const uint8_t tx_power = 6; // in dbm

const byte scd30_address = 0x61;

const uint16_t main_loop_delay = 2500; // ms

RH_RF95 rf95(CS_PIN, INT_PIN);
Adafruit_SCD30 scd30;
GY91 gy91;

uint8_t payload[RH_RF95_MAX_MESSAGE_LEN];

void setup() {
  Serial.begin(9600);
  while(!Serial) delay(10); // Wait for serial port to be available

  if(!rf95.init()) {
    Serial.println("Radio initialisation failed...");
  }
  
  rf95.setFrequency(tx_freq);
  rf95.setSignalBandwidth(sbw);
  rf95.setSpreadingFactor(sf);
  rf95.setCodingRate4(crc);
  rf95.setTxPower(tx_power, 0);

  if(!scd30.begin(scd30_address, &Wire1, 0)) {
    Serial.println("Failed to find the SCD30...");
  }

  if(!gy91.init()) {
    Serial.println("Could not initiate the GY91...");
  }
}

void loop() {
  delay(main_loop_delay);
  Serial.println();

  float reading = analogRead(A8);
  reading = (1023 / reading)  - 1;     // (1023/ADC - 1)
  reading = 10000 / reading;  // 10K / (1023/ADC - 1)
  Serial.print("Thermistor resistance: ");
  Serial.println(reading);

  double pressure = gy91.readPressure();
  Serial.print("Pressure: ");
  Serial.print(pressure);

  Serial.println();

  float temperature = 0.0;
  float relative_humidity = 0.0;
  float co2 = 0.0;

  if(scd30.dataReady()) {
    if(scd30.read()) {
      temperature = scd30.temperature; 
      Serial.print("Temperature: ");
      Serial.print(scd30.temperature);
      Serial.println(" degrees C");
   
      relative_humidity = scd30.relative_humidity; 
      Serial.print("Relative Humidity: ");
      Serial.print(scd30.relative_humidity);
      Serial.println(" %");
   
      co2 = scd30.CO2;
      Serial.print("CO2: ");
      Serial.print(scd30.CO2, 3);
      Serial.println(" ppm");
      Serial.println(""); 
    }
  }

  Serial.println("Sending payload to ground station...");

  doubleToBytes(payload, pressure, 0);
  floatToBytes(payload, reading, 8);
  floatToBytes(payload, relative_humidity, 12);
  floatToBytes(payload, co2, 16);
  floatToBytes(payload, temperature, 20);
  printBytes(payload, 24);

  rf95.send(payload, 24);
  rf95.waitPacketSent();

  Serial.println();
}

void floatToBytes(uint8_t* bf, float val, uint8_t len) {
    byte data[4] = {
    ((uint8_t*)&val)[3],
    ((uint8_t*)&val)[2],
    ((uint8_t*)&val)[1],
    ((uint8_t*)&val)[0]
  };

  for(int i = 0; i < sizeof(data); i++) {
    bf[i + len] = data[i];
  }
}

void doubleToBytes(uint8_t* bf, double val, uint8_t len) {
    byte data[8] = {
    ((uint8_t*)&val)[7],
    ((uint8_t*)&val)[6],
    ((uint8_t*)&val)[5],
    ((uint8_t*)&val)[4],
    ((uint8_t*)&val)[3],
    ((uint8_t*)&val)[2],
    ((uint8_t*)&val)[1],
    ((uint8_t*)&val)[0]
  };

  for(int i = 0; i < sizeof(data); i++) {
    bf[i + len] = data[i];
  }
}

void printBytes(uint8_t* bytes, uint8_t len) {
  for(uint8_t i = 0; i < len; i++) {
    printBitsFromByte(bytes[i]);
  }
}

void printBitsFromByte(byte val) {
    for(int i = 0; i < 8; i++) {
    bool b = val & 0x80;
    Serial.print(b);
    val = val << 1;
  }
}