#!/usr/bin/env python3

import subprocess
import argparse
import uhubctl # https://github.com/nbuchwitz/python3-uhubctl
import time
from datetime import datetime

#commands used
batteryCommand = ["cfgutil", "get", "batteryCurrentCapacity"]

parser = argparse.ArgumentParser(description='Charge a USB attached iOS device to a specified level')
parser.add_argument('-l', metavar='batteryLevel',
                    help='Desired maintenance charge level (default is 80%)')
parser.add_argument('-m', metavar='sleepMin',
                    help='Minutes between checks (default is 10 minutes)')
parser.add_argument('-v', action='store_true',
                    help='Verbose mode')

args = parser.parse_args()

if args.l:
    batteryLevel = args.l
else:
    batteryLevel = 80

if args.m:
    sleepMin = args.m
else:
    sleepMin = 10

if args.v:
    verbose = True
else:
    verbose = False

# Figure out which hub to use
hubs = uhubctl.discover_hubs()
useHub = False
usePort = False

while not useHub:
    for hub in hubs:
        print(f"Found hub: {hub}")
        hubCheck = input("Would you like to use this hub? (y/n) ")
        if verbose:
            print(f"{useHub} - {hubCheck}")
        if hubCheck == "Y" or hubCheck == "y":
            useHub = hub
            while not usePort:
                for port in hub.ports:
                    print(f"Found port: {port} - {port.description()}")
                    portCheck = input("Would you like to use this port? (y/n) ")
                    if verbose:
                        print(f"{usePort} - {portCheck}")
                    if portCheck == "Y" or portCheck == "y":
                        usePort = port
                        break

while True:
    #turn on port
    port.status = True

    #check for battery batteryLevel
    batterybatteryLevel = subprocess.run(batteryCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if verbose:
        print(batterybatteryLevel)

    if batterybatteryLevel.returncode == 0:
        # Extract the number from stdout
        output = batterybatteryLevel.stdout.strip()  # Remove leading/trailing whitespaces
        try:
            batteryNumber = int(output)
        except(ValueError):
            print(f"Please unlock your device.")
            batteryNumber = -1
        if verbose:
            print(f"Battery level: {batteryNumber}%")
    else:
        batteryNumber = -1

    if (batteryNumber >= int(batteryLevel)):
        if verbose:
            print(f"Turning off {port} for {sleepMin} minutes.")
        port.status = False
    elif (batteryNumber > -1):
        if verbose:
            print(f"Leaving on {port} for {sleepMin} minutes.")
    else:
        if verbose:
            print(f"Unable to find battery level of this device. Desired level: {batteryLevel} Checked level: {batteryNumber}")

  
    if verbose:
        currentTime = datetime.now()
        formattedTime = currentTime.strftime("%Y-%m-%d %H:%M:%S")
        print(f"Sleeping for {sleepMin} minute(s) at {formattedTime}")
    time.sleep(int(sleepMin)*60)