# GetVoltStatus
This script will connect to a chevrolet volt via bluetooth using a OBDLink MX # Il will wake up the necessary modules to obtain basic information such as battery # levels, fuel level, battery temp, etc...


To install:

Using a Raspberry Pi 3 or higher, install raspbian.

Install Apache 2, apply permissions

Install Blueman

Bind the bluetooth adapter to the OBDLINK ie: sudo rfcomm bind hci0 00:04:3E:4D:23:50

run program ie: sudo python GetVoltStatus.py

