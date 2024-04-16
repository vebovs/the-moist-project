#include <AUnit.h>
#include <moist.h>
#include <float16.h>

using namespace aunit;

class BitStringTestOnce: public TestOnce {
  protected:
    void assertEqualInt32(int32_t a, int32_t b) {
      if(a == b) assertTrue(true);
      if(a != b) assertTrue(false);
    }

    void assertEqualFloat16(float16 a, float16 b) {
      if(a == b) assertTrue(true);
      if(a != b) assertTrue(false);
    }
};

void setup() {
  Serial.begin(9600);
  while(!Serial) delay(10);
}

void loop() {
  TestRunner::run();
}

test(BitStringToUint8) {
  char bits[] = "110010"; // 50
  uint8_t num = bitStringToUint8(bits);
  assertEqual(num, 50);
}

test(BitStringToUint8PreAppendedZeroBits) {
  char bits[] = "00110010"; // 50
  uint8_t num = bitStringToUint8(bits);
  assertEqual(num, 50);
}

testF(BitStringTestOnce, BitStringToInt32) {
  char bits[] = "1101100110010010000000111100010"; // 1825112546
  int32_t num = bitStringToInt32(bits);
  assertEqualInt32(num, 1825112546);
}


testF(BitStringTestOnce, BitStringToFloat16) {
  char bits[] = "0101011011110010"; // 111.1
  float16 f16_1 = bitStringToFloat16(bits);
  float16 f16_2(111.1);
  assertEqualFloat16(f16_1, f16_2);
}

testF(BitStringTestOnce, BitStringToFloat16NegativeNum) {
  char bits[] = "1101011011110010"; // 111.1
  float16 f16_1 = bitStringToFloat16(bits);
  float16 f16_2(-111.1);
  assertEqualFloat16(f16_1, f16_2);
}

test(BitStringToFloat) {
  char bits[] = "01000100100010101110001110001110"; // 1111.1111
  float f1 = bitStringToFloat(bits);
  float f2 = 1111.1111;
  assertEqual(f1, f2);
}

test(BitStringToFloatNegativeNum) {
  char bits[] = "11000100100010101110001110001110"; // 1111.1111
  float f1 = bitStringToFloat(bits);
  float f2 = -1111.1111;
  assertEqual(f1, f2);
}

