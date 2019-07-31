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

class SampleSummaryWindow():
	def __init__(self, data):
		self.Sum 			= 0
		self.LeftIndex 		= 0
		self.RightIndex 	= 0
		self.LeftItem		= 0
		self.RightItem 		= 0
		self.Buffer 		= data
	
	def MoveWindowRight(self, sample):
		if (self.RightIndex - self.LeftIndex < 16):
			pass
		else:
			self.Sum 		-= self.LeftItem
			self.LeftItem 	+= 1
			self.LeftItem 	= self.Buffer[self.LeftItem]
		
		self.Sum += sample
		self.RightIndex += 1
	
	def GetRightIndex(self):
		return self.RightIndex
	
	def GetLeftIndex(self):
		return self.LeftIndex
	
	def GetWindowSummary(self):
		return self.Sum

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
	
	WindowFront = SampleSummaryWindow(DataBuffer)
	WindowBack 	= SampleSummaryWindow(DataBuffer)
	
	for item in data.split("\r\n"):
		if item is not "":
			DataBuffer.append(int(item))
	
	for idx, sample in enumerate(DataBuffer):
		WindowFront.MoveWindowRight(sample)
		
		if (WindowFront.GetLeftIndex() - WindowBack.GetRightIndex() == 1):
			WindowBack.MoveWindowRight(sample)
	
	ax1.plot([x for x in range(0, len(DataBuffer))], DataBuffer)
	ax2.plot([x for x in range(0, len(DataBuffer))], [10 for x in range(0, len(DataBuffer))])
	
	plt.show()
	
	print "Exit Node ..."

if __name__ == "__main__":
    main()