#this program is designed to convert the midi input from an Akai APC40 mkII to OSC commands that can be interpreted by a Hog 4 Lighting Console.
#Definitions for this program:
#Outbound - communications from Computer to APC40
#Inbound - communications from APC40 to Computer
#OSC In - commands from Hog 4 t0 Computer
#OSC Out - commands from Computer to Hog 4

import threading
import rtmidi
import time
from osc4py3.as_eventloop import *
from osc4py3 import oscbuildparse
from osc4py3 import oscmethod as osm
import json
import os

class Outbound():
	
	def __init__(self, mode=1, port=-1):
		self.jsonFileName = os.path.join(os.path.dirname(os.path.realpath(__file__)), "colorConfig.json")
		self.ConfigData_JSON = open(self.jsonFileName).read()
		self.ConfigData = json.loads(self.ConfigData_JSON)

		self.mode = mode
		self.port = port
		self.midiOut = rtmidi.MidiOut()
		self.buttonMapOutbound = {
			"flash": 0x30,
			"pause": 0x31,
			"choose": 0x32,
			"go": 0x33,
			"stop": 0x34,
			"device left": 0x3A,
			"device right": 0x3B,
			"goback": 0x42,
			"master": 0x50,
		}

		

		
		if self.port != -1:
			self.midiOut.open_port(self.port)
		else:
			self.midiOut.open_port(name='APC40 mkII')
		self.setApcMode()

		self.colorButtonMap = {} #dictionary with tuple as key (path, number), and tuple as value(midiNote Address, colorIndex)
		#populate colorButtonMap from json data
		for i in range(len(self.ConfigData["map"])):
			address = self.ConfigData["map"][i]["address"]
			path = self.ConfigData["map"][i]["path"]
			number = self.ConfigData["map"][i]["number"]
			colorIndex = self.ConfigData["map"][i]["colorIndex"]
			self.rgbLedUpdate(address, 'on', colorIndex)
			self.colorButtonMap[(path, number)] = (address, colorIndex)

	def setApcMode(self):
		self.modeMsg = [0xF0, 0x47, 0x7F, 0x29, 0x60, 0x00, 0x04, 0x41, 0x08, 0x02, 0x01, 0xF7]
		if self.mode == 0:
			self.modeMsg[7] = 0x40
		elif self.mode == 1:
			self.modeMsg[7] = 0x41
		elif self.mode == 2: 
			self.modeMsg[7] = 0x42
		self.midiOut.send_message(self.modeMsg)

	def rgbLedUpdate(self, number, state, color=0):
		self.rgbUpdateMsg = []
		#set message type and LED Status
		if state == 'on':
			self.rgbUpdateMsg.append(0x90)
		elif state == 'flash':
			self.rgbUpdateMsg.append(0x9E)
		elif state == 'off':
			self.rgbUpdateMsg.append(0x80)
		if (number >=0 and number <=39) or (number >=82 and number <=86):
			self.rgbUpdateMsg.append(number)
		if (color >=0 and color <=127):
			self.rgbUpdateMsg.append(color)
		self.midiOut.send_message(self.rgbUpdateMsg)

	def trackLedUpdate(self, track, state, button):
		self.trackUpdateMsg = []
		#print(track, state, button)
		if state == 1:
			self.trackUpdateMsg.append(0x90 + track)
			self.trackUpdateMsg.append(self.buttonMapOutbound[button])
			self.trackUpdateMsg.append(127)
			
		elif state == 0:
			self.trackUpdateMsg.append(0x80 + track)
			self.trackUpdateMsg.append(self.buttonMapOutbound[button])
			self.trackUpdateMsg.append(0)
		self.midiOut.send_message(self.trackUpdateMsg)



class Inbound():
	def __init__(self, port=-1):
		self.jsonFileName = os.path.join(os.path.dirname(os.path.realpath(__file__)), "colorConfig.json")
		self.ConfigData_JSON = open(self.jsonFileName).read()
		self.ConfigData = json.loads(self.ConfigData_JSON)

		self.midiIn = rtmidi.MidiIn()
		self.port = port
		self.buttonMapInbound = {
			0x30 : "flash",
			0x31 : "pause",
			0x32 : "choose",
			0x33 : "go",
			0x42 : "goback",
			}
		for i in range(len(self.ConfigData["map"])):
			address = self.ConfigData["map"][i]["address"]
			path = self.ConfigData["map"][i]["path"]
			number = self.ConfigData["map"][i]["number"]
			colorIndex = self.ConfigData["map"][i]["colorIndex"]
			self.buttonMapInbound[int(self.ConfigData["map"][i]["address"])] = (self.ConfigData["map"][i]["path"], self.ConfigData["map"][i]["number"])

		#print(self.buttonMapInbound)
		if self.port != -1:
			self.midiIn.open_port(self.port)
		else:
			self.midiIn.open_port(name='APC40 mkII')
		self.midiIn.set_callback(self.callback)

	def callback(self, event, data=None):
		message, deltatime = event
		#print(message)
		if (message[1] ==7 and (message[0] >= 0xB0 and message[0] <= 0xB7)):
			self.faderProcess(message)
		elif (message[1] >= 0x30 and message[1] <= 0x34) or message[1] == 0x42:
			self.trackButtonProcess(message)
		elif (message[1] <= 0x27 or (message[1] >= 0x52 and message[1] <= 0x56)):
			self.clipButtonProcess(message)

	def faderProcess(self, message): 
		trackNum = message[0] - 176
		if message[2] > 0:
			value = (message[2] * 2) + 1
		else:
			value = 0
			#print(trackNum, value)
		hog4out.sendFader(trackNum, value)

	def trackButtonProcess(self, message):
		if message[0] > 143:
			trackNum = message[0] - 144
			button = self.buttonMapInbound[message[1]]
			#print(button, trackNum)
			hog4out.sendMasterButton(button, trackNum, 1)
		elif message[0] > 127 and message[0] < 143:
			trackNum = message[0] - 128
			button = self.buttonMapInbound[message[1]]
			#print(button, trackNum)
			hog4out.sendMasterButton(button, trackNum, 0)

	def clipButtonProcess(self, message):
		if message[0] == 144:
			data = self.buttonMapInbound[message[1]]
			hog4out.sendPlayback(data[0], data[1])
			




class OSCOut():
	def __init__(self, ip, port, name):
		self.outboundIP = str(ip)
		self.outboundPort = int(port)
		self.oscName = name
		osc_startup()
		osc_udp_client(self.outboundIP, self.outboundPort, self.oscName)
		msg = oscbuildparse.OSCMessage("/test/message", ',is', [123, "test"])
		osc_send(msg, self.oscName)

	def sendFader(self, number, value):
		number = number + 11
		msg = oscbuildparse.OSCMessage("/hog/hardware/fader/"+str(number), ',i', [value])
		osc_send(msg, self.oscName)
		#osc_process()
		#print(msg)

	def sendMasterButton(self, button, number, state):
		number = number + 11
		msg = oscbuildparse.OSCMessage("/hog/hardware/" + button + "/" +str(number), ',i', [state])
		osc_send(msg, self.oscName)

	def sendPlayback(self, path, number):
		msg = oscbuildparse.OSCMessage("/hog/playback/go/" + str(path), ",i", [number])
		#print(msg)
		osc_send(msg, self.oscName)
		#print(msg)


class OSCIn():
	def __init__(self, ip, port, name):
		self.inboundIP = ip
		self.inboundPort = port
		self.inboundName = name
		#osc_startup()
		osc_udp_server(self.inboundIP, self.inboundPort, self.inboundName)
		osc_method("/hog/playback/go/*", self.playbackUpdateGo, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
		osc_method("/hog/status/led/*", self.masterLedUpdate, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
		osc_method("/hog/playback/release/*", self.playbackUpdateRelease, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
		#print("trap2")

	def playbackUpdateGo(self, address):
		#print("playbackUpdate")
		pattern = address.split("/")
		parts = pattern[5].split(".")
		#print(parts)
		path = int(pattern[4])
		number = int(parts[0])
		address, color = apc40out.colorButtonMap[(path, number)]
		apc40out.rgbLedUpdate(address, 'off', color)
		apc40out.rgbLedUpdate(address, 'flash', color)

	def playbackUpdateRelease(self, address):
		#print("playbackUpdate")
		pattern = address.split("/")
		parts = pattern[5].split(".")
		path = int(pattern[4])
		number = int(parts[0])
		address, color = apc40out.colorButtonMap[(path, number)]
		apc40out.rgbLedUpdate(address, 'on', color)


		

	def masterLedUpdate(self, address, x):
		#print("ledupdate")
		pattern = address.split("/")
		button = pattern[4]
		number = int(pattern[5])
		number = number - 11
		value = int(x)
		if value == 1:
			apc40out.trackLedUpdate(number, 1, button)
		elif value == 0:
			apc40out.trackLedUpdate(number, 0, button)




if __name__ == "__main__":
	apc40out = Outbound(port=3)
	apc40in = Inbound(port=3)
	hog4out = OSCOut("192.168.8.207", 7001, "hog4")
	hog4in = OSCIn("192.168.8.115", 8000, "hog 4 In")
	print("Successful startup. Press ctrl + c to exit")
	#osc_startup()
	#osc_udp_server("192.168.1.80", 8000, "input")
	#osc_method("/hog/status/led/*", masterLedUpdate, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)



	try:
    # Just wait for keyboard interrupt,
    # everything else is handled via the input callback.
		while True:
			osc_process()
			#time.sleep(0.001)
	except KeyboardInterrupt:
		print('')
	finally:
		osc_terminate()
		print("Exit.")

