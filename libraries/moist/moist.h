#ifndef MOIST_H
#define MOIST_H

#include <Arduino.h>
#include <float16.h>

#define CS_PIN 24
#define INT_PIN 25

#define FREQUENCY 433.600
#define BANDWIDTH 62500
#define SPREADING_FACTOR 7
#define CRC_DENOMINATOR 5
#define OUTPUT_POWER 10

// RxPin = 0, TxPin = 1 on Teensy
#define GPS_RX_PIN 0
#define GPS_TX_PIN 1
#define GPS_BAUD 9600

#define SCD30_ADDRESS 0x61

#define DATA_BUDGET_SIZE 34

uint8_t bitStringToUint8(const char* str);
int32_t bitStringToInt32(const char* str);
float16 bitStringToFloat16(const char* str);
float bitStringToFloat(const char* str);
void bytesToBitStr(uint8_t* bytes, uint8_t len, char* str);
void byteToBits(uint8_t val, char* str, uint8_t len);

void idToBytes(uint8_t* bf, uint32_t id, uint8_t len);
void float16ToBytes(uint8_t* bf, float16 val, uint8_t len);
void floatToBytes(uint8_t* bf, float val, uint8_t len);
void printBytes(uint8_t* bytes, uint8_t len);
void printBitsFromByte(byte val);

#endif