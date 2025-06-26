import serial

baudrate = 115200
ser=""
port = "COM5"
try:
    ser = serial.Serial(port, baudrate, timeout=1)
    #ser.write(b'uaisb')
    ser.close()
except Exception as e:
    print(e)