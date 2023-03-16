import time
from multiprocessing import Value
from threading import Event
from Automation.BDaq import *
from Automation.BDaq.InstantAiCtrl import InstantAiCtrl

event = Event()
timer_count = 0
alarm_count = 0
voltage = Value('d', 0.0)
power_flag = Value('i', 0)
alarm_flag = Value('i', 0)

channelCount = 3
startChannel = 5
deviceDescription = "USB-4704,BID#0"


# power state
def DAQ_NAVI(voltage, event, power_flag):
    global startChannel, channelCount, scaledData, timer_count, alarm_count
    timer_count = 0
    instanceAiObj = InstantAiCtrl(deviceDescription)
    while not event.is_set():
        _, scaledData = instanceAiObj.readDataF64(startChannel, channelCount)
        for _ in range(startChannel, startChannel + channelCount):
            with voltage.get_lock():     
                if scaledData[0]: 
                    voltage.value = round(scaledData[0], 3)  
                    # print(f"DAQ Voltage: {voltage.value}")
                    if (voltage.value > 4.825 < 5.125):
                        power_flag.value = 1
                        timer_count = 0   

                    if (voltage.value > 4.825 < 5.125) and timer_count > 10:
                        power_flag.value = 2
                    
                    if voltage.value < 4.825 and timer_count > 10:
                        power_flag.value = 2

                if scaledData[2]:   
                    voltage.value = round(scaledData[2], 1) 
                    if voltage.value < 1.5:
                        alarm_flag.value = 1  
            


def DAQ_ALARM(voltage, event, alarm_flag):
    global startChannel, channelCount, scaledData, alarm_count
    instanceAiObj = InstantAiCtrl(deviceDescription)
    while not event.is_set():
        _, scaledData = instanceAiObj.readDataF64(startChannel, channelCount)
        for _ in range(startChannel, startChannel + channelCount):  
            with voltage.get_lock():  
                if scaledData[2]:    
                    voltage.value = round(scaledData[2], 1)

                    if voltage.value > 1.5:
                        alarm_flag.value = 2

                    if voltage.value < 1.5:
                        alarm_flag.value = 1
                                         

# DAQ counter           
def DAQ_timer(event):
    while not event.is_set():
        global timer_count, reset_flag
        time.sleep(1)
        timer_count += 1
        # print(f"DAQ Timer: {timer_count}")


# Alarm counter
def alarm_timer(event):
    while not event.is_set():
        global alarm_count
        time.sleep(1)
        alarm_count += 1
        # print(f"Alarm Timer: {alarm_count}")
        
