#https://oscarliang.com/connect-raspberry-pi-and-arduino-usb-cable/
import serial
#find the port name with `ls /dev/tty*` on Terminal
ser = serial.Serial('/dev/ttyACM0', 9600)

while 1 :
    ser.readline()
    ser.write('3')