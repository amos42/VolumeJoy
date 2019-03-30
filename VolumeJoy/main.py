#!/usr/bin/python
import serial
import time
import array
import os
import signal
import subprocess
import math
from subprocess import check_output

from config import *

warning = 0
status = 0
currentIcon = ""

def changeicon(percent):
    global currentIcon
    if currentIcon != percent:
        currentIcon = percent
        cmdLine = PNGVIEWPATH + "/pngview -b 0x000F -l 30000 -x 590 -y 2 " + ICONPATH + "/battery" + percent + ".png &"
        print(cmdLine)
        newPngViewProcessPid = int(subprocess.Popen(cmdLine.split(" ")).pid)
        out = check_output("ps aux | grep [p]ngview | awk '{ print $2 }'", shell=True)
        for pid in out.split('\n'):
            if pid.isdigit() and int(pid) != newPngViewProcessPid:
                if DEBUGMSG == 1:
                    print("killing: " + str(pid))
                os.system("kill " + pid)
        if DEBUGMSG == 1:
            print("Changed battery icon to " + percent + "%")
    else:
        if DEBUGMSG == 1:
            print("Changing of icon not needed")

def endProcess(signalnum = None, handler = None):
    os.system("sudo killall pngview");
    exit(0)

if DEBUGMSG == 1:
    print("Batteries 100% voltage:		" + str(VOLT100))
    print("Batteries 75% voltage:		" + str(VOLT75))
    print("Batteries 50% voltage:       	" + str(VOLT50))
    print("Batteries 25% voltage:       	" + str(VOLT25))
    print("Batteries dangerous voltage: 	" + str(VOLT0))

# Prepare handlers for process exit
signal.signal(signal.SIGTERM, endProcess)
signal.signal(signal.SIGINT, endProcess)

#os.system(PNGVIEWPATH + "/pngview -b 0 -l 299999 -x 590 -y 2 " + ICONPATH + "/blank.png &")

ser = serial.Serial("/dev/ttyACM0", 9600, timeout=3)

while True:
    ret = 0
    try:
        ser.write("battery\n");
        ser.flush()
        while ser.out_waiting:
            time.sleep(0.01)
        res = ser.readline()
        tok = res.split(":")
        if tok[0] == "Suc":
            ret = float(tok[1].strip())
    except serial.SerialException:
        time.sleep(REFRESH_RATE)
        continue
	   
    if ret == 0:
        print("Valide Voltage")
    elif ret < VOLT0:
        if status != 0:
            changeicon("0")
            if CLIPS == 1:
	        os.system("/usr/bin/omxplayer --no-osd --layer 999999  " + ICONPATH + "/lowbattshutdown.mp4 --alpha 160;sudo shutdown -h now")
        status = 0
    elif ret < VOLT25:
        if status != 25:
            changeicon("25")
            if warning != 1:
		if CLIPS == 1:
                    os.system("/usr/bin/omxplayer --no-osd --layer 999999  " + ICONPATH + "/lowbattalert.mp4 --alpha 160")
                warning = 1
        status = 25
    elif ret < VOLT50:
        if status != 50:
            changeicon("50")
        status = 50
    elif ret < VOLT75:
        if status != 75:
            changeicon("75")
        status = 75
    else:
        if status != 100:
            changeicon("100")
        status = 100

    time.sleep(REFRESH_RATE)
