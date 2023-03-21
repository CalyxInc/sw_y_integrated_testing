import sys
import struct
import tkinter as tk
from tkinter import ttk
import serial
from serial_port import ser_usb, read_config_variable


variable_format = "=8s4B4B16s16s16s IH B32s32sBBBBBBHBBBBBB51B H"
vairable_struct = []
header_offset = 0
hw_version_offset = 1 + header_offset
fw_version_offset = 4 + hw_version_offset


def draw_systeminfo_frame(parent):

    fw_version = vairable_struct[fw_version_offset:fw_version_offset + 4]

    system_info_frame = ttk.Label(parent, font=('Arial',14,'bold'))

    # fw version
    tk.Label(system_info_frame, text="FW Version:", font=('Arial',14,'bold')).grid(
        row=2, column=1, padx=3, pady=3, sticky='w')
    tk.Label(system_info_frame, text="v%d.%d.%d.%d" % (fw_version[0], 
                                                       fw_version[1], 
                                                       fw_version[2], 
                                                       fw_version[3]), 
                                                       font=('Arial',14,'bold')).grid(
                                                        row=2, column=2, padx=3, pady=3, sticky='e')

    parent.add(system_info_frame, text='System Info')


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


def variable_start(parent):

    global vairable_struct
    global config_tab
    global win

    win = parent

    config_tab = ttk.Notebook(parent)          # Create Tab Control

    #config_frame = tk.LabelFrame (parent, text='Configuration')
    vairable_struct = list(read_config_variable(variable_format))

    # print(vairable_struct)

    header = vairable_struct[header_offset]

    draw_systeminfo_frame(config_tab)

    config_tab.grid(row=3, column=0, sticky='we', padx=3, pady=3, columnspan=3)

