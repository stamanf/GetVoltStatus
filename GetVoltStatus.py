
#
# GetVoltStatus:
# This script will connect to a chevrolet volt via bluetooth using a OBDLink MX
# Il will wake up the necessary modules to obtain basic information such as battery
# levels, fuel level, battery temp, etc...
#
# Hardware requirements:
# You will require a Raspberry PI 3 or above, and a OBDLink MX.

# version 0.5, June 25, 2019
# by Francois St-Amand (gtx_16v@hotmail.com)

# Thanks to Brian Batista for the use of the CANBUS guide spreadsheet.

# This code is public, please inform me of any improvements you have made.  
# Kindly provide credit if you use this code.
# You may not use this code for monetary reasons.



import bluetooth
import time
import schedule
import select	
import datetime
import smtplib,email,email.encoders,email.mime.text,email.mime.base	
from socket import *

#Change this for your OBDLink bluetooth address
bd_addr = "00:04:3E:4D:23:50"
port = 1
html_text = ""
parse = ""

#Function to write the html page.
def WriteFile(html_text):
	f = open("/var/www/html/index.html","w")
	f.write("<H1>VOLT STATUS</H1>")
	f.write(html_text)
	f.close()

#Function to wake up the volt's modules
def WakeVolt(sock):	
	sock.send("ATZ \r\n")
	time.sleep(.5)
	sock.send("ATR1 \r\n")
	time.sleep(.5)
	sock.send("ATE1 \r\n")
	time.sleep(.5)
	#set protocol to SW CAN (ISO 11898, 11-bit Tx, 33.3kbps, var DLC)
	sock.send("STP61 \r\n")
	time.sleep(.5)
	#wake up mode
	sock.send("STCSWM2 \r\n")
	time.sleep(.5)
	sock.send("ATSH100 \r\n")
	time.sleep(.5)
	sock.send("00 00 00 00 00 00 00 00 \r\n")
	time.sleep(.5)
	#wake up bus
	sock.send("ATSH621 \r\n")
	time.sleep(.5)
	sock.send("00 FF FF FF FF 00 00 00 \r\n")
	time.sleep(.5)
	sock.send("STCSWM3 \r\n")
	time.sleep(.5)
	#set protocol to SW CAN (ISO 11898, 11-bit Tx, 33.3kbps, var DLC)
	sock.send("STP33 \r\n")
	time.sleep(.5)
	sock.send("ATCP10 \r\n")
	time.sleep(.5)
	sock.send("ATSH7E0 \r\n")
	time.sleep(.5)
	sock.send("ATE0 \r\n")
	# clear buffer
	sock.recv(1024)

#Function to get the remaining fuel.
def GetFuelRemaining(sock):
	# FUEL REMAINING
	sock.settimeout(1)
	sock.send("22002F \r\n")
	time.sleep(5)
	print("Fuel remaining= ")
	try:
		parse= sock.recv(26)
	except sock.timeout as e:
		print "timeout"
	Fuel= parse[20] + parse[21]
	Fuel = int(Fuel,16) * 100 / 255
	print Fuel
	#html_text= "<H4>Fuel remaining= " + str(Fuel) + " %</H4>"
	return "<H4>Fuel remaining= " + str(Fuel) + " %</H4>"
	
#Function to get the battery level.
def GetBatteryRemaining(sock):

	# BATTERY REMAINING
	parse=0
	sock.settimeout(1)
	sock.send("22005B \r\n")
	time.sleep(5)
	print("Battery remaining= ")
	try:
		parse= sock.recv(24)
	except sock.timeout as e:
		print "timeout"
	Battery= parse[9] + parse[10]
	#print Battery
	Battery = int(Battery,16) * 100 / 255
	print Battery
	#html_text= "<H4>Battery remaining= " + str(Battery) + " %</H4>"
	return "<H4>Battery remaining= " + str(Battery) + " %</H4>"

#Function to get LV battery voltage
def GetLVBatteryRemaining(sock):

	# LV BATTERY VOLTAGE
	sock.settimeout(1)
	sock.send("ATRV\r\n")
	time.sleep(1)
	print("LV Battery= ")
	try:
		parse= sock.recv(10)
	except sock.timeout as e:
		print "timeout"
	print parse
	return "<H4>Battery remaining= " + parse + " </H4>"

#Function to get Battery pack voltage
def GetBatteryVoltage(sock):
	# HV BATTERY VOLTAGE
	sock.settimeout(1)
	parse=0
	sock.send("ATSH7E1 \r\n")
	time.sleep(.5)
	sock.send("222429 \r\n")
	time.sleep(5)
	print("Battery voltage= ")
	try:
		parse= sock.recv(24)
	except sock.timeout as e:
		print "timeout"
	HVBattery1= parse[14] + parse[15]
	HVBattery2= parse[17] + parse[18] 
	HVBattery=int(HVBattery1,16)*256
	HVBattery=HVBattery+int(HVBattery2,16)
	HVBattery = HVBattery / 64
	print HVBattery
	return "<H4>Battery voltage= " + str(HVBattery) + " V</H4>"
	#html_text= html_text + "<H4>Battery voltage= " + str(HVBattery) + " V</H4>"

#Function to get the charging current.
def GetChargerAmp(sock):
	# CHARGER AMP
	sock.settimeout(1)
	parse=0
	sock.send("ATSH7E4 \r\n")
	time.sleep(.5)
	sock.send("22436C \r\n")
	time.sleep(5)
	print("Charger amp= ")
	try:
		parse= sock.recv(24)
	except sock.timeout as e:
		print "timeout" 
	ChargerAmp = parse[17] + parse[18]
	ChargerAmp =int(ChargerAmp,16)/20
	print ChargerAmp
	#print parse
	#html_text= html_text + "<H4>Charger Amp= " + str(ChargerAmp) + " A</H4>"
	return "<H4>Charger Amp= " + str(ChargerAmp) + " A</H4>"

#Function to get the battery temperature.
def GetBatteryTemp(sock):
	# BATTERY TEMP
	sock.settimeout(1)
	parse=0
	sock.send("22434F \r\n")
	time.sleep(5)
	print("Battery temp= ")
	try:
		parse= sock.recv(24)
	except sock.timeout as e:
		print "timout"
	BatteryTemp=parse[9] + parse[10]
	BatteryTemp=(int(BatteryTemp,16)-40)
	print BatteryTemp
	#html_text= html_text + "<H4>Battery temp= " + str(BatteryTemp) + " oC</H4>"
	return "<H4>Battery temp= " + str(BatteryTemp) + " oC</H4>"

#Function to get the outside temperature (does not work).
def GetOutsideTemp(sock):
	# OUTSIDE TEMP
	sock.settimeout(1)
	parse=0
	sock.send("22000F \r\n")
	time.sleep(5)
	print("Outside temp= ")
	try:
		parse= sock.recv(24)
	except sock.timeout as e:
		print "timout"
	print (parse)
	OutsideTemp=parse[9] + parse[10]
	OutsideTemp=((int(OutsideTemp,16)-40)/2)
	print OutsideTemp
	#html_text= html_text + "<H4>Outside temp= " + str(OutsideTemp) + " oC</H4>"
	return "<H4> Outside temp= " + str(OutsideTemp) + " oC</H4>"


def main():
	#set the MAC address to the bluetooth socket.
	sock=bluetooth.BluetoothSocket(bluetooth.RFCOMM)
	html_text=""
	try:
		sock.connect((bd_addr,port))	
		print "Connected"	
		WakeVolt(sock)
		html_text=GetFuelRemaining(sock)
#		html_text=html_text+GetOutsideTemp(sock)
		html_text=html_text+GetBatteryRemaining(sock)
		html_text=html_text+GetBatteryVoltage(sock)
		html_text=html_text+GetChargerAmp(sock)
		html_text=html_text+GetBatteryTemp(sock)
		html_text=html_text+GetLVBatteryRemaining(sock)
		html_text=html_text+time.ctime()
		print html_text
		WriteFile(html_text)
		sock.close()
#		break
	except:
		print "Could not connect at this time"
		

#	else:
#		print "Cannot connect at this time"
#		print time.ctime()

#	sock.close()
#Start the program and run main()
main()
#Schedule to run the program in intervals.
schedule.every(1).hour.do(main)
while True:
	schedule.run_pending()
	time.sleep(1)
