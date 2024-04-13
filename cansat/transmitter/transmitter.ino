#include <SPI.h>
#include <RH_RF95.h>
#include <GY91.h>
#include <Adafruit_SCD30.h>
#include <SoftwareSerial.h>
#include <TinyGPSPlus.h>
#include <float16.h>
#include <TeensyThreads.h>

const uint8_t CS_PIN = 24;
const uint8_t INT_PIN = 25;

const float tx_freq = 433.600; // in Mhz
const long sbw = 62500; // in Hz
const uint8_t sf = 7;
const uint8_t crc = 5; //denominator, final value is 4/7
const uint8_t tx_power = 10; // in dbm

const byte scd30_address = 0x61;
const uint32_t GPSBaud = 9600;

const uint16_t main_loop_delay = 2000; // ms

RH_RF95 rf95(CS_PIN, INT_PIN);
Adafruit_SCD30 scd30;
GY91 gy91;
SoftwareSerial gpsSerial(0, 1); // RxPin = 0, TxPin = 1 on Teensy
TinyGPSPlus gps;

uint8_t payload[RH_RF95_MAX_MESSAGE_LEN];

int gps_thread_id = 0;
int gps_thread_state = 0;
int scd30_thread_id = 0;
int scd30_thread_state = 0;

int32_t ID = 0;
float altitude = 0;
float lat = 0;
float lng = 0;
uint8_t hour = 0;
uint8_t minute = 0;
uint8_t second = 0;
float16 temperature(0.0);
float16 relative_humidity(0.0);
float co2 = 0.0;

void setup() {
  Serial.begin(9700);
  while(!Serial) delay(10); // Wait for serial port to be available

  gpsSerial.begin(GPSBaud);

  gps_thread_id = threads.addThread(gpsTask);
  gps_thread_state = threads.getState(gps_thread_id);

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

  scd30_thread_id = threads.addThread(scd30Task);
  scd30_thread_state = threads.getState(scd30_thread_id);

  if(!gy91.init()) {
    Serial.println("Could not initiate the GY91...");
  }
}

void loop() {
  delay(main_loop_delay);

  Serial.println();
  if(gps_thread_state == threads.RUNNING) Serial.println("GPS thread is running");
  if(gps_thread_state == threads.ENDED) Serial.println("GPS thread has ended");
  if(scd30_thread_state == threads.RUNNING) Serial.println("SCD30 thread is running");
  if(scd30_thread_state == threads.ENDED) Serial.println("SCD30 thread has ended");
  Serial.println();

  Serial.print("ID: ");
  Serial.println(ID);

  float reading = analogRead(A8);
  reading = (1023 / reading)  - 1;
  reading = 4700 / reading; // R1 = 4.7 kOhms
  Serial.print("Thermistor resistance: ");
  Serial.println(reading);

  double pressure = float(gy91.readPressure());
  Serial.print("Pressure: ");
  Serial.println(pressure);

  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println(" degrees C");

  Serial.print("Relative Humidity: ");
  Serial.print(relative_humidity);
  Serial.println(" %");

  Serial.print("CO2: ");
  Serial.print(co2, 3);
  Serial.println(" ppm");

  Serial.print("Timestamp: ");
  Serial.print(hour);
  Serial.print(":");
  Serial.print(minute);
  Serial.print(":");
  Serial.println(second);

  Serial.print("Altitude: ");
  Serial.println(altitude);
  Serial.print("Latitude: ");
  Serial.println(lat);
  Serial.print("Longitude: ");
  Serial.println(lng);

  Serial.println();

  Serial.println("Sending payload to ground station...");

  idToBytes(payload, ID, 0);
  payload[3] = hour, payload[4] = minute, payload[5] = second;
  floatToBytes(payload, altitude, 6);
  floatToBytes(payload, lat, 10);
  floatToBytes(payload, lng, 14);
  floatToBytes(payload, pressure, 18);
  floatToBytes(payload, reading, 22);
  float16ToBytes(payload, relative_humidity, 26);
  floatToBytes(payload, co2, 28);
  float16ToBytes(payload, temperature, 32);
  printBytes(payload, 34);

  rf95.send(payload, 34);
  rf95.waitPacketSent();

  ID++;

  Serial.println();
}

void scd30Task() {
  while(1) {
    if(scd30.dataReady()) {
      if(scd30.read()) {
        temperature = float16(scd30.temperature); 
        relative_humidity = float16(scd30.relative_humidity); 
        co2 = scd30.CO2;
      }
    }
  }
}

void gpsTask() {
  while(1) {
    while(gpsSerial.available() > 0) gps.encode(gpsSerial.read());
    if(gps.location.isUpdated()) {
      lat = float(gps.location.lat());
      lng = float(gps.location.lng());
    }
    if(gps.altitude.isUpdated()) {
      altitude = float(gps.altitude.meters());
    }
    if(gps.time.isUpdated()) {
      hour = gps.time.hour() + 2; // Norway is GMT + 2
      minute = gps.time.minute();
      second = gps.time.second();
    }
  }
}

void idToBytes(uint8_t* bf, uint32_t id, uint8_t len) {
  bf[len + 2] = id & 0xff;
  bf[len + 1] = (id >> 8);
  bf[len] = (id >> 16);
}

void float16ToBytes(uint8_t* bf, float16 val, uint8_t len) {
  uint16_t bytes = val.getBinary();
  bf[len + 1] = bytes & 0xff;
  bf[len] = (bytes >> 8);
}

void floatToBytes(uint8_t* bf, float val, uint8_t len) {
    byte data[4] = {
    ((uint8_t*)&val)[3],
    ((uint8_t*)&val)[2],
    ((uint8_t*)&val)[1],
    ((uint8_t*)&val)[0]
  };

  for(uint8_t i = 0; i < 4; i++) {
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