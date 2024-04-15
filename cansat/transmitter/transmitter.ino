#include <SPI.h>
#include <RH_RF95.h>
#include <GY91.h>
#include <Adafruit_SCD30.h>
#include <SoftwareSerial.h>
#include <TinyGPSPlus.h>
#include <float16.h>
#include <TeensyThreads.h>
#include <moist.h>

// Enables the serial port for diagnostics
// Set to 0 before connecting to battery power
#define DEBUG 1

RH_RF95 rf95(CS_PIN, INT_PIN);
Adafruit_SCD30 scd30;
GY91 gy91;
SoftwareSerial gpsSerial(GPS_RX_PIN, GPS_TX_PIN);
TinyGPSPlus gps;

const uint16_t main_loop_delay = 2000; // ms
uint16_t scd30_interval = 0;
bool setup_error = false;
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
  #if DEBUG
    Serial.begin(9700);
    while(!Serial) delay(10); // Wait for serial port to be available
  #endif

  gpsSerial.begin(GPS_BAUD);

  gps_thread_id = threads.addThread(gpsTask);
  gps_thread_state = threads.getState(gps_thread_id);

  if(!rf95.init()) {
    setup_error = true;
    #if DEBUG
      Serial.println("Radio initialisation failed...");
    #endif
  }
  
  rf95.setFrequency(FREQUENCY);
  rf95.setSignalBandwidth(BANDWIDTH);
  rf95.setSpreadingFactor(SPREADING_FACTOR);
  rf95.setCodingRate4(CRC_DENOMINATOR);
  rf95.setTxPower(OUTPUT_POWER, 0);

  if(!scd30.begin(SCD30_ADDRESS, &Wire1, 0)) {
    setup_error = true;
    #if DEBUG
      Serial.println("Failed to find the SCD30...");
    #endif
  }

  scd30_interval = scd30.getMeasurementInterval();

  #if DEBUG
    Serial.print("SCD30 measurement interval: ");
    Serial.print(scd30.getMeasurementInterval());
    Serial.println("s");
  #endif

  scd30_thread_id = threads.addThread(scd30Task);
  scd30_thread_state = threads.getState(scd30_thread_id);

  if(!gy91.init()) {
    setup_error = true;
    #if DEBUG
      Serial.println("Could not initiate the GY91...");
    #endif
  }

  #if !DEBUG
    if(!setup_error) SetupSuccess();
    if(setup_error) SetupFailure();
  #endif
}

void loop() {
  delay(main_loop_delay);

  #if DEBUG
    Serial.println();
    if(gps_thread_state == threads.RUNNING) Serial.println("GPS thread is running");
    if(gps_thread_state == threads.ENDED) Serial.println("GPS thread has ended");
    if(scd30_thread_state == threads.RUNNING) Serial.println("SCD30 thread is running");
    if(scd30_thread_state == threads.ENDED) Serial.println("SCD30 thread has ended");
    Serial.println();
    Serial.print("ID: ");
    Serial.println(ID);
  #endif

  float reading = analogRead(A8);
  reading = (1023 / reading)  - 1;
  reading = 4700 / reading; // R1 = 4.7 kOhms

  double pressure = float(gy91.readPressure());

  #if DEBUG
    Serial.print("Thermistor resistance: ");
    Serial.println(reading);

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
  #endif

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
  
  #if DEBUG
    printBytes(payload, 34);
  #endif

  rf95.send(payload, 34);
  rf95.waitPacketSent();

  ID++;

  #if DEBUG
    Serial.println();
  #endif
}

void scd30Task() {
  while(1) {
    delay(scd30_interval * 1000);
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

void SetupSuccess() {
    tone(BUZZER_PIN, 523.25, 133);
    delay(133);
    tone(BUZZER_PIN, 523.25, 133);
    delay(133);
    tone(BUZZER_PIN, 523.25, 133);
    delay(133);
    tone(BUZZER_PIN, 523.25, 400);
    delay(400);
    tone(BUZZER_PIN, 415.30, 400);
    delay(400);
    tone(BUZZER_PIN, 466.16, 400);
    delay(400);
    tone(BUZZER_PIN, 523.25, 133);
    delay(133);
    delay(133);
    tone(BUZZER_PIN, 466.16, 133);
    delay(133);
    tone(BUZZER_PIN, 523.25, 1200);
    delay(1200);
}

void SetupFailure() {
    tone(BUZZER_PIN, 1000);
    delay(250);
    noTone(BUZZER_PIN);
}
