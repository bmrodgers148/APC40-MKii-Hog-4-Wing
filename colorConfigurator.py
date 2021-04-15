import os
import json

keepGoing = True

numbers = {  #Logical renumbering of RGB Buttons on APC40 mkII. Numbering goes from left to right, top to bottom.
1 : 32,
2 : 33,
3 : 34,
4 : 35,
5 : 36,
6 : 37,
7 : 38,
8 : 39,
9 : 40,
10 : 24,
11 : 25,
12 : 26,
13 : 27,
14 : 28,
15 : 29,
16 : 30,
17 : 31,
18 : 41,
19 : 16,
20 : 17,
21 : 18,
22 : 19,
23 : 20,
24 : 21,
25 : 22,
26 : 23,
27 : 42,
28 : 8,
29 : 9,
30 : 10,
31 : 11,
32 : 12,
33 : 13,
34 : 14,
35 : 15,
36 : 43,
37 : 0,
38 : 1,
39 : 2,
40 : 3,
41 : 4,
42 : 5,
43 : 6,
44 : 7,
45 : 44
}
	


def saveJson():
	ConfigData_Filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "colorConfig.json")
	ConfigData_JSON = open(ConfigData_Filename, 'w')
	ConfigData = {}
	ConfigData["map"] = buttons
	json.dump(ConfigData, ConfigData_JSON, indent=1)
	exit()

def menuLoop():
	choice = 0
	choice = input("\n1. Set color and cue path. \n2. Look up color index number. \n3. Save Changes and Exit.\n")
	if choice == '1':
		choice = int(input("Enter button number to make changes or type 100 to change all buttons."))
		if(choice >= 1 and choice <= 45):
			inVar = 0
			print("\nButton #: " + str(choice))
			int(choice)
			while(inVar != 4):
				print("Midi Address: " + str(buttons[numbers[choice]]["address"]))
				print("1. Cue Path: " + str(buttons[numbers[choice]]["path"]))
				print("2. Cuelist/Scene Number: " + str(buttons[numbers[choice]]["number"]))
				print("3. Color Index Number: " + str(buttons[numbers[choice]]["colorIndex"]))
				print("4. Exit \n")
				inVar = int(input())
				if (inVar == 1):
					buttons[numbers[choice]]["path"] = int(input("Cue Path. Enter 0 for cuelist, 1 for scene, or 2 for macro."))
				elif (inVar == 2):
					buttons[numbers[choice]]["number"] = int(input("Cue or Scene number."))
				elif (inVar == 3):
					buttons[numbers[choice]]["colorIndex"] = int(input("Color by index Number (0-127)"))
		elif(choice == 100):
			inVar = 0
			for i in range(45):
				print("\nButton #: " + str(i+1))
				print("Midi Address: " + str(buttons[numbers[i+1]]["address"]))
				print("1. Cue Path: " + str(buttons[numbers[i+1]]["path"]))
				print("2. Cuelist/Scene Number: " + str(buttons[numbers[i+1]]["number"]))
				print("3. Color Index Number: " + str(buttons[numbers[i+1]]["colorIndex"]))
				print("4. Continue \n")
				inVar = int(input())
				if (inVar == 1):
					buttons[numbers[i+1]]["path"] = int(input("Cue Path. Enter 0 for cuelist, 1 for scene, or 2 for macro."))
				elif (inVar == 2):
					buttons[numbers[i+1]]["number"] = int(input("Cue or Scene number."))
				elif (inVar == 3):
					buttons[numbers[i+1]]["colorIndex"] = int(input("Color by index Number (0-127)"))
	elif choice == '2':
		for i in range(45):
			buttons[numbers[i+1]]["colorIndex"] = 45+i
			#[numbers[i+1]]["colorIndex"] = 45 + i
			if buttons[numbers[i+1]]["colorIndex"] > 127:
				buttons[numbers[i+1]]["colorIndex"] = 127
			
	elif choice == '3':
		saveJson()












if __name__ == "__main__":
	try:
		ConfigData_Filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "colorConfig.json")
		ConfigData_JSON = open(ConfigData_Filename).read()
		ConfigData = json.loads(ConfigData_JSON)
		buttons = ConfigData["map"]
		
		while True:
			menuLoop()
			#time.sleep(0.001)
	except KeyboardInterrupt:
		print('')
	finally:
		print("Exit.")