#include <moist.h>

uint8_t bitStringToUint8(const char* str) {
  uint8_t x = 0;
  for(; *str; ++str) {
    x = (x << 1) + (*str - '0');
  }
  return x;
}

int32_t bitStringToInt32(const char* str) {
  int32_t x = 0;
  for(; *str; ++str) {
    x = (x << 1) + (*str - '0');
  }
  return x;
}

float16 bitStringToFloat16(const char* str) {
  uint16_t x = 0;
  for(; *str; ++str) {
    x = (x << 1) + (*str - '0');
  }
  float16 f;
  f.setBinary(x);
  return f;
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