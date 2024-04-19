import serial
import time

port = 'COM6'
baudrate = 9600
ser = serial.Serial(port, baudrate)

while (True):
    if(ser.in_waiting):
        data = ser.readline(ser.in_waiting).decode()
        print(data, end='')
    time.sleep(0.01)