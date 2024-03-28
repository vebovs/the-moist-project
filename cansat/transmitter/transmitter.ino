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
const int8_t tx_power = 10; // in dbm

const byte scd30_address = 0x61;

const uint16_t main_loop_delay = 2000; // ms

RH_RF95 rf95(CS_PIN, INT_PIN);
Adafruit_SCD30 scd30;
GY91 gy91;

char payload[RH_RF95_MAX_MESSAGE_LEN];

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

  String sensor_data = "";
  sensor_data.concat(reading).concat(", ").
    concat(pressure).concat(", ").
    concat(temperature).concat(", ").
    concat(relative_humidity).concat(", ").
    concat(co2);

  char data[sensor_data.length()];
  sensor_data.toCharArray(data, sensor_data.length()); 

  uint8_t len = sprintf(payload, data) + 1;

  rf95.send((uint8_t *)payload, &len);
  rf95.waitPacketSent();

  Serial.println();
}

