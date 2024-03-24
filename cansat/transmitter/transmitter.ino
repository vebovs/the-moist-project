#include <SPI.h>
#include <RH_RF95.h>

const uint8_t CS_PIN = 24;
const uint8_t INT_PIN = 25;

const float tx_freq = 433.600; // in Mhz
const long sbw = 20800; // 20.8 kHz
const uint8_t sf = 8;
const uint8_t crc = 7; //denominator, final value is 4/7
const int8_t tx_power = 10; // in dbm

RH_RF95 rf95(CS_PIN, INT_PIN);

// uint8_t data[RH_RF95_MAX_MESSAGE_LEN];
uint8_t data[] = "Hello World!";

void setup() {
  Serial.begin(9600);
  while (!Serial) ; // Wait for serial port to be available

  if (!rf95.init()) {
    Serial.println("Radio initialisation failed...");
  }
  
  rf95.setFrequency(tx_freq);
  rf95.setSignalBandwidth(sbw);
  rf95.setSpreadingFactor(sf);
  rf95.setCodingRate4(crc);
  rf95.setTxPower(tx_power, 0);
}

void loop() {
  Serial.println("Sending to rf95_server");
  rf95.send(data, sizeof(data));
  rf95.waitPacketSent();
  delay(1000);
}


