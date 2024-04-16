#include <AUnit.h>
#include <moist.h>

using namespace aunit;

void setup() {
  Serial.begin(9600);
  while(!Serial) delay(10);
}

void loop() {
  TestRunner::run();
}

test(idToBytes) {
  uint32_t id = 1000;
  uint8_t buf[3];
  idToBytes(buf, id, 0);
  uint32_t reconstructed_id = reconstructedId(buf);
  assertEqual(reconstructed_id, id);
}

test(idToBytesMaxValue) {
  uint32_t max_id_allowed = 16777215;
  uint8_t buf[3];
  idToBytes(buf, max_id_allowed, 0);
  uint32_t reconstructed_id = reconstructedId(buf);
  assertEqual(reconstructed_id, max_id_allowed);
}

test(idToBytesValueOverflow) {
  uint32_t id_value_overflow = 16777216;
  uint8_t buf[3];
  idToBytes(buf, id_value_overflow, 0);
  uint32_t reconstructed_id = reconstructedId(buf);
  assertNotEqual(reconstructed_id, id_value_overflow);
}

uint32_t reconstructedId(uint8_t *buf) {
  uint32_t reconstructed_id = 0;
  reconstructed_id = (reconstructed_id & 0xFFFFFF00) | buf[2];
  reconstructed_id = (reconstructed_id & 0xFFFF00FF) | ((uint32_t)buf[1] <<  8);
  reconstructed_id = (reconstructed_id & 0xFF00FFFF) | ((uint32_t)buf[0] << 16);
  return reconstructed_id;
}