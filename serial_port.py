import sys
import serial
import struct
import threading

class mutex_serial (serial.Serial):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mutex = threading.Lock()

    def acquire(self):
        self.mutex.acquire()

    def release(self):
        self.mutex.release()

SER_RETRY_TIMES = 5
SER_NORMAL_TIMEOUT = 1
SER_SET_SENSOR_PARAMETERS_TIMEOUT = 10

ser_usb = mutex_serial(
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=SER_NORMAL_TIMEOUT
)


def read_fw_stage_header(ser):

    header_format = '=2sBI'
    result = 0
    header = None

    raw = ser.read(7)
    in_checksum = ser.read(1)
    if (len(raw) == 7) and (len(in_checksum) == 1):
        checksum = 0
        for i in raw:
            checksum += int(i)
        checksum = (checksum & 0xff).to_bytes(1, sys.byteorder, signed=False)
        header = struct.unpack(header_format, raw)
        if ((header[0] != b'FW') and (header[0] != b'BL')):
            print("header_two = ", header[0])
            result = 1
        if (checksum != in_checksum):
            result = 1
    else:
        result = 1
        print("header zero!")

    return header, result

def read_header(ser):

    header_format = '=2sBI'
    result = 0
    header = None

    raw = ser.read(7)
    in_checksum = ser.read(1)
    if (len(raw) == 7) and (len(in_checksum) == 1):
        checksum = 0
        for i in raw:
            checksum += int(i)
        checksum = (checksum & 0xff).to_bytes(1, sys.byteorder, signed=False)
        header = struct.unpack(header_format, raw)
        if (header[0] != b'OK'):
            result = 1
        if (checksum != in_checksum):
            print("header checksum err = calculate - ", checksum, "  in - ", in_checksum)
            result = 1
    else:
        result = 1
        print("header zero!")

    return header, result

def read_config_variable(format):
    ser_usb.acquire()
    ser_usb.write(serial.to_bytes([0x45, 0x00, 0x01, 0x0C, 0x52]))
    raw = ser_usb.read(struct.calcsize(format))
    ser_usb.release()
    return struct.unpack(format, raw)

def write_config_variable(var):
    ser_usb.acquire()
    ser_usb.write(serial.to_bytes([0x45, 0x00, 0x01, 0x0D, 0x53]))
    ser_usb.write(var)
    answer = ser_usb.read(2)
    ser_usb.release()
    print(answer)
    
def get_fw_stage():

    print("get_fw_stage")

    ser_usb.acquire()
    ser_usb.write(serial.to_bytes([0x45, 0x00, 0x01, 0x1A, 0x60]))
    header, result = read_fw_stage_header(ser_usb)
    ser_usb.release()
    if (result != 0):
        print("command fail")
        return struct.pack('=2s', 0)
    else:
        return header[0]