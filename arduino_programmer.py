#########################################
# ARDUINO MICROPYTHON UPDATER    		#
#########################################
from machine import UART
from machine import Pin
import select
import time
import sys
import socket

IP_SERVER = '192.168.1.5'
# IP_SERVER = '192.168.7.12'
PORT = 50000

Max_Retries = 10

rst = Pin(2, Pin.OUT)    # create output pin on GPIO2
rst.high()               # set pin to high

class uartStream:
	def __init__(self, uart):
		self.uart = uart

	def read(self, n):
		tmp = self.uart.read(n)
		return tmp

	def write(self, n):
		self.uart.write(n)

def acknowledge(uStream):
	res = uStream.read(2)
	if res is not None:
		# for item in res:
		# 	print(item)
		if "\x14\x10" in res:
			return True
		else:
			return False
	else:
		return False

def setup_bootloader(ser):
	# reset arduino
	rst.low()                # set pin to low
	time.sleep_ms(200)
	rst.high()                # set pin to low
	time.sleep_ms(100)
	# get in sync with the AVR
	for i in range(Max_Retries):
		ser.write(b'\x30\x20') # STK_GET_SYNC # STK_CRC_EOP
		if not acknowledge(ser):
			continue
		else:
			break
	if i == Max_Retries-1:
		print("Unable to establish sync after %d retries." % Max_Retries)
		return False
	# enter programming mode
	ser.write(b'\x50\x20')
	if not acknowledge(ser):
		return False

	ser.write('\x75\x20')
	response = ser.read(5)
	if response is not None:
		pass
		# for item in response:
		# 	print (item)
	else:
		return False
	return True


def run(hex_file, ip=IP_SERVER, port=PORT):

	uart = UART(0, 57600)
	uart.init(57600, bits=8, parity=None, stop=1, timeout=1000)
	ser = uartStream(uart)
	if hex_file:
		print("Hex File to Program: %s" %  hex_file)
	else:
		sys.exit(1)
		pass
	server_addr = ip
	addr_info = socket.getaddrinfo(server_addr, port)
	addr = addr_info[0][-1]
	s = socket.socket()
	s.connect(addr)

	s.send("hello")
	data = s.recv(10)
	if 'welcome' in str(data, 'utf8'):
		print("connected")
		s.send(hex_file)
		data = s.recv(10)
		if 'ok' in str(data, 'utf8'):
			print("file read OK")
			if setup_bootloader(ser):
				print("programming arduino ...")
				s.send("ready")
				while True:
					data = s.recv(1024)
					if data == 0:
						print("socket receive 0 bytes - server close")
						break
					ser.write(data)
					if not acknowledge(ser):
						break
					else:
						s.send("\x14\x10")
				s.close()
		elif 'error' in str(data, 'utf8'):
			print("file read FAIL")
	# reset arduino
	print("resetting arduino")
	rst.low()                # set pin to low
	time.sleep_ms(200)
	rst.high()                # set pin to low
	time.sleep_ms(100)	
	print("done")


	

