#!/usr/bin/env python3

import subprocess
import argparse
import uhubctl # https://github.com/nbuchwitz/python3-uhubctl
import time
from datetime import datetime

#commands used
batteryCommand = ["cfgutil", "get", "batteryCurrentCapacity"]

parser = argparse.ArgumentParser(description='Charge a USB attached iOS device to a specified level')
parser.add_argument('-x', metavar='max',
                    help='Maximum charge level')
parser.add_argument('-n', metavar='min',
                    help='Minimum charge level')
parser.add_argument('-m', metavar='sleepMin',
                    help='Minutes between checks')
parser.add_argument('-v', action='store_true',
                    help='Verbose mode')

args = parser.parse_args()

if args.x:
    max = args.x
else:
    max = 80

if args.n:
    min = args.n
else:
    min = 20

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

    #check for battery level
    batteryLevel = subprocess.run(batteryCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if verbose:
        print(batteryLevel)

    if batteryLevel.returncode == 0:
        # Extract the number from stdout
        output = batteryLevel.stdout.strip()  # Remove leading/trailing whitespaces
        try:
            batteryNumber = int(output)
        except(ValueError):
            print(f"Please unlock your device.")
            batteryNumber = -1
        if verbose:
            print(f"Battery level: {batteryNumber}%")
    else:
        batteryNumber = -1

    if (batteryNumber > -1 and batteryNumber <= int(min)):
        if verbose:
            print(f"Leaving on {port} for {sleepMin} minutes.")
    elif (batteryNumber > -1 and batteryNumber >= int(max)):
        if verbose:
            print(f"Turning off {port} for {sleepMin} minutes.")
        port.status = False
    else:
        if verbose:
            print(f"Unable to find battery level of this device. Debug: {min} min - {max} max - {batteryNumber}%")

  
    if verbose:
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"Sleeping for {sleepMin} minute(s) at {formatted_time}")
    time.sleep(int(sleepMin)*60)