#include <AUnit.h>
#include <moist.h>
#include <float16.h>

using namespace aunit;

class Float16TestOnce: public TestOnce {
  protected:
    void assertEqualFloat16(float16 a, float16 b) {
      if(a == b) assertEqual(true, true);
      if(a != b) assertEqual(true, false);
    }
};

void setup() {
  Serial.begin(9600);
  while(!Serial) delay(10);
}

void loop() {
  TestRunner::run();
}

testF(Float16TestOnce, float16ToBytes) {
  float f16 = 11.11;
  uint8_t buf[2];
  float16ToBytes(buf, f16, 0);
  float16 reconstructed_float16;
  uint16_t binary = reconstructedFloat16InBinary(buf);
  reconstructed_float16.setBinary(binary);
  assertEqualFloat16(f16, reconstructed_float16);
}

testF(Float16TestOnce, float16ToBytesMax) {
  float f16 = 6.5504 * pow(10, 4);
  uint8_t buf[2];
  float16ToBytes(buf, f16, 0);
  float16 reconstructed_float16;
  uint16_t binary = reconstructedFloat16InBinary(buf);
  reconstructed_float16.setBinary(binary);
  assertEqualFloat16(f16, reconstructed_float16);
}

testF(Float16TestOnce, float16ToBytesMin) {
  float f16 = -6.5504 * pow(10, 4);
  uint8_t buf[2];
  float16ToBytes(buf, f16, 0);
  float16 reconstructed_float16;
  uint16_t binary = reconstructedFloat16InBinary(buf);
  reconstructed_float16.setBinary(binary);
  assertEqualFloat16(f16, reconstructed_float16);
}

testF(Float16TestOnce, float16toBytesSmallest) {
  float f16 = 5.96046 * pow(10, -8);
  uint8_t buf[2];
  float16ToBytes(buf, f16, 0);
  float16 reconstructed_float16;
  uint16_t binary = reconstructedFloat16InBinary(buf);
  reconstructed_float16.setBinary(binary);
  assertEqualFloat16(f16, reconstructed_float16);
}

uint16_t reconstructedFloat16InBinary(uint8_t *buf) {
  uint16_t temp = 0;
  temp = ((buf[0] << 8)  |
           buf[1]);
  return temp;
}