import os
import sys
import signal
import time
import binascii
import struct
import array

import matplotlib.pyplot as plt
import matplotlib.animation as animation

DataBuffer = []

def Animate(i):
	ax1.clear()
	ax1.plot([x for x in range(0, len(DataBuffer))], DataBuffer)
	ax2.plot([x for x in range(0, len(DataBuffer))], [x for x in range(0, len(DataBuffer))])

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
# ani = animation.FuncAnimation(fig, Animate, interval=1000)
ax2 = fig.add_subplot(1,1,1)

def signal_handler(signal, frame):
	pass

def main():
	global IsMainRunning
	signal.signal(signal.SIGINT, signal_handler)
	
	file = open("algo_data.txt", "rb")
	data = file.read()
	file.close()
	
	
	
	for item in data.split("\r\n"):
		if item is not "":
			DataBuffer.append(float(item))
	
	for sample in DataBuffer:
		pass
	
	ax1.plot([x for x in range(0, len(DataBuffer))], DataBuffer)
	ax2.plot([x for x in range(0, len(DataBuffer))], [10 for x in range(0, len(DataBuffer))])
	
	plt.show()
	
	print "Exit Node ..."

if __name__ == "__main__":
    main()