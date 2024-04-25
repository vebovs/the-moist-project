#include <SPI.h>
#include <RH_RF95.h>
#include <TimeLib.h>
#include <float16.h>
#include <moist.h>

// Set to 0 while capturing data
#define DEBUG 0

RH_RF95 rf95(CS_PIN, INT_PIN);

uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];

const uint16_t bits_id = 24;
const uint16_t bits_hour = bits_id + 8;
const uint16_t bits_minute = bits_hour + 8;
const uint16_t bits_second = bits_minute + 8;
const uint16_t bits_altitude = bits_second + 32;
const uint16_t bits_lat = bits_altitude + 32;
const uint16_t bits_lng = bits_lat + 32;
const uint16_t bits_pressure = bits_lng + 32;
const uint16_t bits_reading = bits_pressure + 32;
const uint16_t bits_rh = bits_reading + 16;
const uint16_t bits_co2 = bits_rh + 32;
const uint16_t bits_temp = bits_co2 + 16;

void setup() {
  #if DEBUG
    Serial.begin(9600);
    while (!Serial) delay(10); // Wait for serial port to be available
  #endif

  if (!rf95.init()) {
    #if DEBUG
      Serial.println("Radio initialisation failed...");
    #endif
  }

  rf95.setFrequency(FREQUENCY);
  rf95.setSpreadingFactor(SPREADING_FACTOR);
  rf95.setSignalBandwidth(BANDWIDTH);
  rf95.setCodingRate4(CRC_DENOMINATOR);
}

void loop() {
  if (rf95.waitAvailableTimeout(3000)) {
    uint8_t len = sizeof(buf);
    if (rf95.recv(buf, &len)) {
      char bit_str_buf[DATA_BUDGET_SIZE * 8];
      bytesToBitStr(buf, DATA_BUDGET_SIZE, bit_str_buf);
      String bit_str = String(bit_str_buf);

      #if DEBUG
        Serial.print("Elapsed time: ");
        Serial.print(hour());
        Serial.print(":");
        Serial.print(minute());
        Serial.print(":");
        Serial.println(second());
        Serial.print("ID: ");
        Serial.println(bitStringToInt32(bit_str.substring(0, bits_id).c_str()));
        Serial.print("Timestamp: ");
        Serial.print(bitStringToUint8(bit_str.substring(bits_id, bits_hour).c_str()));
        Serial.print(":");
        Serial.print(bitStringToUint8(bit_str.substring(bits_hour, bits_minute).c_str()));
        Serial.print(":");
        Serial.println(bitStringToUint8(bit_str.substring(bits_minute, bits_second).c_str()));
        Serial.print("Altitude: ");
        Serial.println(bitStringToFloat(bit_str.substring(bits_second, bits_altitude).c_str()));
        Serial.print("Latitude: ");
        Serial.println(bitStringToFloat(bit_str.substring(bits_altitude, bits_lat).c_str()), 6);
        Serial.print("Longitude: ");
        Serial.println(bitStringToFloat(bit_str.substring(bits_lat, bits_lng).c_str()), 6);
        Serial.print("Pressure: ");
        Serial.println(bitStringToFloat(bit_str.substring(bits_lng, bits_pressure).c_str()));
        Serial.print("NTC: ");
        Serial.println(bitStringToFloat(bit_str.substring(bits_pressure, bits_reading).c_str()));
        Serial.print("Relative humidity: ");
        Serial.println(bitStringToFloat16(bit_str.substring(bits_reading, bits_rh).c_str()));
        Serial.print("CO2: ");
        Serial.println(bitStringToFloat(bit_str.substring(bits_rh, bits_co2).c_str()));
        Serial.print("Temperature: ");
        Serial.println(bitStringToFloat16(bit_str.substring(bits_co2, bits_temp).c_str()));
        Serial.print("RSSI: ");
        Serial.println(rf95.lastRssi(), DEC);
        Serial.println();
      #endif

      #if !DEBUG
        //Elapsed time since start
        Serial.print(hour());
        Serial.print(":");
        Serial.print(minute());
        Serial.print(":");
        Serial.print(second());
        Serial.print(",");
        Serial.print(bitStringToInt32(bit_str.substring(0, bits_id).c_str()));
        Serial.print(",");
        Serial.print(bitStringToUint8(bit_str.substring(bits_id, bits_hour).c_str()));
        Serial.print(":");
        Serial.print(bitStringToUint8(bit_str.substring(bits_hour, bits_minute).c_str()));
        Serial.print(":");
        Serial.print(bitStringToUint8(bit_str.substring(bits_minute, bits_second).c_str()));
        Serial.print(",");
        Serial.print(bitStringToFloat(bit_str.substring(bits_second, bits_altitude).c_str()));
        Serial.print(",");
        Serial.print(bitStringToFloat(bit_str.substring(bits_altitude, bits_lat).c_str()), 6);
        Serial.print(",");
        Serial.print(bitStringToFloat(bit_str.substring(bits_lat, bits_lng).c_str()), 6);
        Serial.print(",");
        Serial.print(bitStringToFloat(bit_str.substring(bits_lng, bits_pressure).c_str()));
        Serial.print(",");
        Serial.print(bitStringToFloat(bit_str.substring(bits_pressure, bits_reading).c_str()));
        Serial.print(",");
        Serial.print(bitStringToFloat16(bit_str.substring(bits_reading, bits_rh).c_str()));
        Serial.print(",");
        Serial.print(bitStringToFloat(bit_str.substring(bits_rh, bits_co2).c_str()));
        Serial.print(",");
        Serial.print(bitStringToFloat16(bit_str.substring(bits_co2, bits_temp).c_str()));
        Serial.print(",");
        Serial.println(rf95.lastRssi(), DEC);
      #endif
      
    }
    else {
      #if DEBUG
        Serial.println("recv failed");
      #endif
    }
  }
  else {
    #if DEBUG
      Serial.println("Nothing received...");
    #endif
  }
}
