import serial
from time import sleep

if __name__ == '__main__':
    port = '/dev/cu.usbmodem14101'
    ser = serial.Serial(port, 9600)
    ser.flush()
    while 1:
        ser.write(int.to_bytes(int(input()), 1, 'big'))
        if ser.in_waiting:
            print(ser.read().decode(), end='')
