#include <SPI.h>
#include <RH_RF95.h>

const uint8_t CS_PIN = 24;
const uint8_t INT_PIN = 25;

const float rx_freq = 433.600; // in Mhz
const long sbw = 62500; // in kHz
const uint8_t sf = 8;
const uint8_t crc = 7; //denominator, final value is 4/7

RH_RF95 rf95(CS_PIN, INT_PIN);

uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];

const uint8_t data_budget_size = 24; // bytes to be decoded

const uint16_t bits_pressure = 64;
const uint16_t bits_reading = bits_pressure + 32;
const uint16_t bits_rh = bits_reading + 32;
const uint16_t bits_co2 = bits_rh + 32;
const uint16_t bits_temp = bits_co2 + 32;

void setup() {
  Serial.begin(9600);
  while (!Serial); // Wait for serial port to be available

  if (!rf95.init()) {
    Serial.println("init failed");
  }

  rf95.setFrequency(rx_freq);
  rf95.setSpreadingFactor(sf);
  rf95.setSignalBandwidth(sbw);
  rf95.setCodingRate4(crc);
}

void loop() {
  if (rf95.waitAvailableTimeout(3000)) {
    uint8_t len = sizeof(buf);
    if (rf95.recv(buf, &len)) {
      Serial.println("Received data: ");
      char bit_str_buf[data_budget_size * 8];
      bytesToBitStr(buf, data_budget_size, bit_str_buf);
      String bit_str = String(bit_str_buf);

      Serial.println(bit_str_buf);
      Serial.print(bitStringToFloat(bit_str.substring(bits_pressure, bits_reading).c_str()));
      Serial.print(", ");
      Serial.print(bitStringToDouble(bit_str.substring(0, bits_pressure).c_str()));
      Serial.print(", ");
      Serial.print(bitStringToFloat(bit_str.substring(bits_co2, bits_temp).c_str()));
      Serial.print(", ");
      Serial.print(bitStringToFloat(bit_str.substring(bits_reading, bits_rh).c_str()));
      Serial.print(", ");
      Serial.println(bitStringToFloat(bit_str.substring(bits_rh, bits_co2).c_str()));

      Serial.print("RSSI: ");
      Serial.println(rf95.lastRssi(), DEC);
    }
    else {
      Serial.println("recv failed");
    }
  }
  else{
    Serial.println("Nothing received...");
  }
}

float bitStringToFloat(const char* str) {
  uint32_t x = 0;
  for(; *str; ++str) {
    x = (x << 1) + (*str - '0');
  }
  float f;
  memcpy(&f, &x, 4); // 4 because float is 32 bits
  return f;
}

double bitStringToDouble(const char* str) {
  uint64_t x = 0;
  for(; *str; ++str) {
    x = (x << 1) + (*str - '0');
  }
  double d;
  memcpy(&d, &x, 8); // 8 because double is 64 bits
  return d;
}

void bytesToBitStr(uint8_t* bytes, uint8_t len, char* str) {
  for(uint8_t i = 0; i < len; i++) {
    byteToBits(bytes[i], str, i);
  }
}

void byteToBits(uint8_t val, char* str, uint8_t len) {
  for(uint8_t i = 0; i < 8; i++) {
    bool b = val & 0x80;
    str[len * 8 + i] = b == 1 ? '1' : '0';
    val = val << 1;
  }
}


