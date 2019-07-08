import os
import sys
import signal
import time
import binascii
import struct
import array

import matplotlib.pyplot as plt
import MkSUSBAdaptor

IsMainRunning = True
DataCounter = 0
DataBuffer = []

def OnSerialAsyncDataHandler(data):
	global IsMainRunning, DataCounter, DataBuffer
	DataCounter += len(data)
	DataBuffer += array.array('B', data).tolist()
	print (DataCounter)
	
	if DataCounter > 4000:
		DataCounter = 0
		plt.plot(DataBuffer[:])
		plt.show()
		IsMainRunning = False

def signal_handler(signal, frame):
	global IsMainRunning
	IsMainRunning = False

def main():
	global IsMainRunning
	signal.signal(signal.SIGINT, signal_handler)
	
	uart 			= MkSUSBAdaptor.Adaptor(OnSerialAsyncDataHandler)
	isConnected 	= uart.ConnectDevice(4, 3)
	print ("UART device connected")
	
	if (isConnected is True):
		while (IsMainRunning is True):
			pass
	
	print "Exit Node ..."

if __name__ == "__main__":
    main()