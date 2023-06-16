import time
import board
import adafruit_dht
from bluetooth import *

# DHT11 - VCC : 5V, GND : GND, GPIO : D20
socket = BluetoothSocket( RFCOMM )
socket.connect(("98:D3:31:FD:17:10", 1))	

dht11 = adafruit_dht.DHT11(board.D18)
check = False
count = 0
pre_temp = 0

# BLE transport
def ble():
	# socket = BluetoothSocket( RFCOMM )
	# socket.connect(("98:D3:31:FD:17:10", 1))
	global check
	
	if check:
		msg = "turn on"
	
	else:
		msg = "turn off"
		
	socket.send(msg)
	# socket.close()
	
while True:
	try:
		# read sensor value
		temp = dht11.temperature
		if pre_temp != temp:
			print(f"temperature = {temp:.1f}C")
		# turn on
		if not check:
			pre_temp = temp
			
			if temp >= 26:
				check = True
				ble()
				print("turn on")
			else:
				pass
		
		else:
			if temp > pre_temp:
				pre_temp = temp
				count = 0
				
			elif count == 3:
				check = False
				pre_temp = 0
				ble()
				print("turn off")
				
			elif temp < pre_temp:
				pre_temp = temp
				count += 1
				print(count)
			
			else:
				pass

		
	except:
		pass
		
	time.sleep(2)
		
	
