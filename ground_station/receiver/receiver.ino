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
      printBytes(buf, 24);
      Serial.println();
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

void printBytes(uint8_t* bytes, uint8_t len) {
  for(uint8_t i = 0; i < len; i++) {
    printBitsFromByte(bytes[i]);
  }
}

void printBitsFromByte(uint8_t val) {
  for(uint8_t i = 0; i < 8; i++) {
    bool b = val & 0x80;
    Serial.print(b);
    val = val << 1;
  }
}


