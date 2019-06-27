#!/usr/bin/python
import os
import sys
import signal
import time
import binascii
import struct

import matplotlib.pyplot as plt

import MkSUSBAdaptor
import MkSProtocol
import MkSConnectorArduino

IsMainRunning = True

def LoadContent(filename):
	if os.path.isfile(filename) is True:
		file = open(filename, "rb")
		data = file.read()
		file.close()
		return data
	return ""

def SignalGenerationConfig(pin, signal_count, interval):
	return struct.pack("BBHHBHH", 0xDE, 0xAD, 0x500, 0x4 + 0x5, pin, signal_count, interval)

def SignalGenerationStart():
	return struct.pack("BBH", 0xDE, 0xAD, 0x501)

def SignalGenerationBuffer(buffer, length):
	s = bytes(buffer)
	return struct.pack("BBHHH%ds" % (len(s),), 0xDE, 0xAD, 0x502, 0x4 + 0x2 + len(buffer), length, s)

def SignalGenerationStop():
	return struct.pack("BBH", 0xDE, 0xAD, 0x503)

def OnSerialAsyncDataHandler(data):
	print (data)

def signal_handler(signal, frame):
	global IsMainRunning
	IsMainRunning = False

def main():
	global IsMainRunning
	signal.signal(signal.SIGINT, signal_handler)
	
	# Load CSV file
	csvRawData  = LoadContent("csv/test.csv")
	csvDataRows = csvRawData.split("\n")
	
	csvColumns = []
	for row in csvDataRows[16::12]:
		csvColumns.append(row.split(",")[:2])
	
	Multiplier = 1
	# Configuration
	SampleRate = (Multiplier * float(csvColumns[1][0])) - (Multiplier * float(csvColumns[0][0]))
	prevSample = csvColumns[0]
	for sample in csvColumns[1:]:
		SampleRate = (SampleRate + abs(((Multiplier * float(sample[0])) - (Multiplier * float(prevSample[0]))))) / 2
		prevSample = sample
	
	SampleRate = int(1 / SampleRate)
	SamplesCount = len(csvDataRows)
	
	print (SampleRate, SamplesCount)
	
	protocol 		= MkSProtocol.Protocol()
	uart 			= MkSUSBAdaptor.Adaptor(OnSerialAsyncDataHandler)
	isConnected 	= uart.ConnectDevice(16, 3)
	print ("UART device connected")
	isConnected 	= True
	
	debug_graph = []
	if (isConnected is True):		
		packets = []
		samples = ""
		for idx, col in enumerate(csvColumns):
			isSend = idx % 499
			
			if (isSend is 0 and idx is not 0):
				txPacket = SignalGenerationBuffer(samples, 500)
				packets.append(txPacket)
				samples = ""
			
			samples += struct.pack("B", int(float(col[1]))) # Values in CSV rabge from 0.1 to 1.9, this make a binary (0/1)
			debug_graph.append(int(float(col[1])))
		
		print ("Get UUID and Type")
		txPacket = protocol.GetDeviceTypeCommand()
		rxPacket = uart.Send(txPacket, False)
		txPacket = protocol.GetDeviceUUIDCommand()
		rxPacket = uart.Send(txPacket, False)
		
		print ("Send config...")
		txPacket = SignalGenerationConfig(13, len(csvDataRows), 8)
		uart.Send(txPacket, True)
		
		# Send START command
		# txPacket = SignalGenerationStart()
		# uart.Send(txPacket, True)
		
		print ("Send buffer...")
		# Send BUFFER command
		for packet in packets:
			uart.Send(packet, True)
			time.sleep(0.0125)
			# print binascii.hexlify(sample)
		
		time.sleep(0.1)
		# Send STOP	command
		txPacket = SignalGenerationStop()
		uart.Send(txPacket, True)
		
		#plt.plot(debug_graph)
		#plt.show()
		
		#while (IsMainRunning is True):
		#	pass
	
	#uart.DisconnectDevice()
	
	#Protocol 	= MkSProtocol.Protocol()
	#Adaptor 	= MkSUSBAdaptor.Adaptor(OnSensorDeviceDataArrivedAsync)
	#Connector 	= MkSConnectorArduino.Connector(None)
	
	#Connector.SetProtocol(Protocol)
	#Connector.SetAdaptor(Adaptor)
	#Connector.SetDeviceDisconnectCallback(OnDeviceDisconnectHandler)
	
	print "Exit Node ..."

if __name__ == "__main__":
    main()