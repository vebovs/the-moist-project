#include <AUnit.h>
#include <moist.h>
#include <float.h>

using namespace aunit;

void setup() {
  Serial.begin(9600);
  while(!Serial) delay(10);
}

void loop() {
  TestRunner::run();
}

test(floatToBytes) {
  float f = 111.111;
  uint8_t buf[4];
  floatToBytes(buf, f, 0);
  float reconstructed_float = reconstructedFloat(buf);
  assertEqual(f, reconstructed_float);
}

test(floatToBytesMax) {
  float f = FLT_MAX;
  uint8_t buf[4];
  floatToBytes(buf, f, 0);
  float reconstructed_float = reconstructedFloat(buf);
  assertEqual(f, reconstructed_float);
}

test(floatToBytesMin) {
  float f = FLT_MIN;
  uint8_t buf[4];
  floatToBytes(buf, f, 0);
  float reconstructed_float = reconstructedFloat(buf);
  assertEqual(f, reconstructed_float);
}

float reconstructedFloat(uint8_t *buf) {
  uint32_t temp = 0;
  temp = ((buf[0] << 24) |
          (buf[1] << 16) |
          (buf[2] << 8)  |
           buf[3]);
  return *((float*)&temp);
}
