#!/usr/bin/env python3

import subprocess
import argparse
import uhubctl # https://github.com/nbuchwitz/python3-uhubctl
import time
from datetime import datetime

#commands used
batteryCommand = ["cfgutil", "get", "batteryCurrentCapacity"]

#backoff values
currentDelay = 1
maxDelay = 45
minDelay = 1
backoffAmount = 2

parser = argparse.ArgumentParser(description='Charge a USB attached iOS device to a specified level')
parser.add_argument('-l', metavar='batteryLevel',
                    help='Desired maintenance charge level (default is 80%)')
parser.add_argument('-v', action='store_true',
                    help='Verbose mode')
parser.add_argument('-d', action='store_true',
                    help='Debug mode')

args = parser.parse_args()

if args.l:
    batteryLevel = args.l
else:
    batteryLevel = 80

if args.v:
    verbose = True
else:
    verbose = False

if args.d:
    debug = True
else:
    debug = False

# Figure out which hub to use
hubs = uhubctl.discover_hubs()
useHub = False
usePort = False

while not useHub:
    for hub in hubs:
        print(f"Found hub: {hub}")
        hubCheck = input("Would you like to use this hub? (y/n) ")
        if debug:
            print(f"{useHub} - {hubCheck}")
        if hubCheck == "Y" or hubCheck == "y":
            useHub = hub
            while not usePort:
                for port in hub.ports:
                    print(f"Found port: {port} - {port.description()}")
                    portCheck = input("Would you like to use this port? (y/n) ")
                    if debug:
                        print(f"{usePort} - {portCheck}")
                    if portCheck == "Y" or portCheck == "y":
                        usePort = port
                        break

while True:
    if verbose:
        currentTime = datetime.now()
        formattedTime = currentTime.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{formattedTime}")

    if debug:
        print(f"Current port status: {port.status}")

    if not port.status:
        #turn on port
        port.status = True
        time.sleep(60)

    #check for battery batteryLevel
    batterybatteryLevel = subprocess.run(batteryCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if debug:
        print(batterybatteryLevel)

    if batterybatteryLevel.returncode == 0:
        # Extract the number from stdout
        output = batterybatteryLevel.stdout.strip()  # Remove leading/trailing whitespaces
        try:
            batteryNumber = int(output)
        except(ValueError):
            print(f"Please unlock your device.")
            batteryNumber = -1
        if verbose and batteryNumber > -1:
            print(f"Battery level: {batteryNumber}%")
    else:
        batteryNumber = -1

    if (batteryNumber >= int(batteryLevel)):
        #currentDelay = min(max((batteryNumber-int(batteryLevel))*10, currentDelay * backoffFactor), maxDelay)
        currentDelay = min(max(currentDelay * backoffAmount, batteryNumber-int(batteryLevel)+1), maxDelay)

        if verbose:
            print(f"{port}: Off")

        port.status = False

    elif (batteryNumber > -1):
        currentDelay = 1
        if verbose:
            print(f"{port}: On")

    else:
        #currentDelay = max(currentDelay // backoffFactor, minDelay)
        #portNumber = str(usePort).split(".")
        #hubNumber = str(useHub).split(" ")
        #space = " "
        #rawUSBCommand = ["uhubctl", "-l", hubNumber[2], "-p", portNumber[1], "-a", "on", "-N"]

        if verbose:
            print(f"Unable to find battery level of this device.")
        
        if debug:
            print(f"Desired level: {batteryLevel} Checked level: {batteryNumber}")
        #    print(f"Attempting raw uhubctl command: {space.join(rawUSBCommand)}")

        #forceResult = subprocess.run(rawUSBCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        #if debug:
        #    print(forceResult)

        #if forceResult.returncode == 0:
        #    if verbose:
        #        print("Successfully turned on port with raw uhubctl command...")
        #    currentDelay = 1

    if verbose:
        if currentDelay > 1:
            print(f"Sleeping for {currentDelay} minutes")
        else:
            print(f"Sleeping for {currentDelay} minute")
    time.sleep(int(currentDelay)*60)