# iOSChargeController
A charge controller for iOS devices that queries the battery level with cfgutil and controls power with uhubctl

Prerequisites:
- Get uhubctl: https://github.com/mvp/uhubctl
- Get this python3 uhubctl wrapper: https://github.com/nbuchwitz/python3-uhubctl
- Get Apple Configurator: https://support.apple.com/apple-configurator
- Install "Automation Tools" from the Apple Configuration menu
- Have a USB hub that supports being controlled programmatically (see https://github.com/mvp/uhubctl for a list)

Command line options:
  -h, --help       show this help message and exit
  -l batteryLevel  Desired maintenance charge level (default is 80)
  -m sleepMin      Minutes between checks (default is 10)
  -v               Verbose mode
