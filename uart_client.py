import os
import sys
import signal
import time
import binascii
import struct
import array

if sys.version_info[0] < 3:
	import thread
else:
	import _thread
import threading

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import MkSUSBAdaptor

DATABAFFERFRAMELENGTH = 16386

IsMainRunning 	= True
DataCounter 	= 0
DataBuffer 		= []

DataLock = threading.Lock()

def Animate(i):
	#print("ENTER")
	DataLock.acquire()
	if (len(DataBuffer) > DATABAFFERFRAMELENGTH):
		ax1.clear()
		ax1.plot([x for x in range(0, DATABAFFERFRAMELENGTH)], DataBuffer[:DATABAFFERFRAMELENGTH])
		del DataBuffer[:DATABAFFERFRAMELENGTH]
	DataLock.release()	
	#print("EXIT")

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ani = animation.FuncAnimation(fig, Animate, interval=100)

def OnSerialAsyncDataHandler(data):
	global IsMainRunning, DataCounter, DataBuffer, line, xdata, ydata
	DataCounter = len(data)
	
	print("D_ENTER")
	DataLock.acquire()
	DataBuffer += array.array('B', data).tolist()
	DataLock.release()
	print("D_EXIT")
	
	print (len(DataBuffer))

def signal_handler(signal, frame):
	global IsMainRunning
	IsMainRunning = False

def main():
	global IsMainRunning
	signal.signal(signal.SIGINT, signal_handler)
	
	uart 			= MkSUSBAdaptor.Adaptor(OnSerialAsyncDataHandler)
	isConnected 	= uart.ConnectDevice(4, 921600, 3)
	print ("UART device connected")
	
	plt.show()
	#if (isConnected is True):
	#	while (IsMainRunning is True):
	#		pass
	
	print "Exit Node ..."

if __name__ == "__main__":
    main()