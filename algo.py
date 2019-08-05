import os
import sys
import signal
import time
import binascii
import struct
import array

import matplotlib.pyplot as plt
import matplotlib.animation as animation

WINDOW_SIZE = 6
RawData = []

class Pulse():
	def __init__(self, left, right, samples):
		self.LeftIndex 		= left
		self.RightIndex 	= right
		self.MiddleIndex 	= 0
		self.SamplesCount 	= samples
	
	def GetMiddle(self):
		if (self.RightIndex < self.LeftIndex):
			return 0
		
		if (self.RightIndex == self.LeftIndex):
			return 0
		
		if (self.MiddleIndex == 0):
			self.MiddleIndex = self.LeftIndex + ((self.RightIndex - self.LeftIndex) / 2)
		
		return self.MiddleIndex

class SampleSummaryWindow():
	def __init__(self, data):
		self.Sum 			= 0
		self.LeftIndex 		= 0
		self.RightIndex 	= 0
		self.LeftItem		= 0
		self.RightItem 		= 0
		self.Buffer 		= data
	
	def MoveWindowRight(self, sample):
		if (self.RightIndex - self.LeftIndex < WINDOW_SIZE):
			pass
		else:
			self.LeftIndex 	+= 1
			self.LeftItem 	= self.Buffer[self.LeftIndex]
		
		if (self.RightIndex > WINDOW_SIZE):
			self.Sum -= self.LeftItem
		
		self.Sum += sample
		self.RightIndex += 1
	
	def GetRightIndex(self):
		return self.RightIndex
	
	def GetLeftIndex(self):
		return self.LeftIndex
	
	def GetWindowSummary(self):
		return self.Sum
	
	def GetWindowDeviation(self):
		SumDeviation = 0;
		for idx in range(WINDOW_SIZE):
			corrT1 = self.Buffer[idx + self.LeftIndex]
			corrT2 = self.Buffer[(idx+1) + self.LeftIndex]
			SumDeviation = self.Buffer[idx + self.LeftIndex]

def Animate(i):
	ax1.clear()
	ax1.plot([x for x in range(0, len(RawData))], RawData)
	ax2.plot([x for x in range(0, len(RawData))], [x for x in range(0, len(RawData))])

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
# ani = animation.FuncAnimation(fig, Animate, interval=1000)
ax2 = fig.add_subplot(1,1,1)
ax3 = fig.add_subplot(1,1,1)
ax4 = fig.add_subplot(1,1,1)

def signal_handler(signal, frame):
	pass

def main():
	global IsMainRunning
	signal.signal(signal.SIGINT, signal_handler)
	
	file = open("algo_data.txt", "rb")
	data = file.read()
	file.close()
	
	EnergyDiffSignal 	= []
	EdgesSignal 		= []
	PulseSignal 		= []
	PulseList 			= []
	
	for item in data.split("\r\n"):
		if item is not "":
			RawData.append(int(item))
	
	frames = 0
	for row in RawData[::2048]:
		DataBuffer	= RawData[(frames * 2048):((frames + 1) * 2048)]
		frames+=1
		WindowFront 		= SampleSummaryWindow(DataBuffer)
		WindowBack 			= SampleSummaryWindow(DataBuffer)
		SumSignal 			= 0
		SamplesCount		= 0
		for idx, sample in enumerate(DataBuffer):
			WindowFront.MoveWindowRight(sample)
			
			if (WindowFront.GetLeftIndex() - WindowBack.GetRightIndex() == 1):
				WindowBack.MoveWindowRight(DataBuffer[idx - WINDOW_SIZE])
			
			EnergyDiffSignal.append(WindowFront.GetWindowSummary() - WindowBack.GetWindowSummary())
			
			if (sample > 25):
				SumSignal += sample
				SamplesCount += 1
		
		if (SamplesCount > 0):
			AvgSample = (SumSignal / SamplesCount)
		
			for sample in EnergyDiffSignal:
				if (sample > AvgSample):
					EdgesSignal.append(AvgSample)
				elif (sample < -AvgSample):
					EdgesSignal.append(-AvgSample)
				else:
					EdgesSignal.append(0)

			PulseLeftIndex 		= 0
			PulseSampleCount 	= 0
			IsPulse 			= False
			# Gradient
			PrevSample = EdgesSignal[0]
			for idx, sample in enumerate(EdgesSignal[1:]):
				if (sample != PrevSample):
					if (PrevSample is 0):
						if (sample > 0):
							# Raising edge (positive) - Start pulse
							PulseSignal.append(50)
							if (IsPulse is False):
								PulseLeftIndex = idx - 1
							IsPulse = True
							PulseSampleCount += 1
						else:
							# Raising edge (negative)
							PulseSignal.append(50)
							IsPulse = True
							PulseSampleCount += 1
					elif (PrevSample > 0):
						if (sample is 0):
							# Falling edge (positive)
							PulseSignal.append(50)
							IsPulse = True
							PulseSampleCount += 1
						else:
							# Error
							pass
					elif (PrevSample < 0):
						if (sample is 0):
							# Falling edge (negative) - End pulse
							PulseSignal.append(0)
							IsPulse = False
							PulseList.append(Pulse(PulseLeftIndex, idx - 1, PulseSampleCount))
							
							PulseLeftIndex 		= 0
							PulseRightIndex 	= 0
							PulseSampleCount 	= 0
						else:
							# Error
							pass
					else:
						# Error
						pass
				else:
					# No change
					if (PrevSample is 0):
						if (IsPulse == True):
							PulseSignal.append(50)
							PulseSampleCount += 1
						else:
							PulseSignal.append(0)
					else:
						PulseSignal.append(50)
				PrevSample = sample
			
	ax1.plot([x for x in range(0, len(RawData))], RawData)
	ax2.plot([x for x in range(0, len(EnergyDiffSignal))], EnergyDiffSignal)
	ax3.plot([x for x in range(0, len(EdgesSignal))], EdgesSignal)
	ax4.plot([x for x in range(0, len(PulseSignal))], PulseSignal)
	
	plt.plot([0, len(RawData)], [AvgSample, AvgSample], 'k-', lw=1)
	plt.plot([0, len(RawData)], [-AvgSample, -AvgSample], 'k-', lw=1)
	
	for pulse in PulseList:
		middle = pulse.GetMiddle()
		plt.plot([middle, middle], [25, 225], 'k-', lw=1)
	
	plt.show()
	
	print "Exit Node ..."

if __name__ == "__main__":
    main()