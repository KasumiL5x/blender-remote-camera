# Basic structure from https://pythontic.com/modules/socket/udp-client-server-example

import socket
import sys

HOST = 'localhost'
PORT = 4242
BUFF_SIZE = 1024

# Create the UDP socket.
try:
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	print('Socket created.')
except socket.error as msg:
	print(f'Failed to create socket. Error code: {msg[0]}; Message: {msg[1]}')
	sys.exit()

# Bind the socket.
try:
	s.bind((HOST, PORT))
	print(f'Socket bound at {HOST}:{PORT}')
except socket.error as msg:
	print(f'Failed to bind socket. Error code: {msg[0]}; Message: {msg[1]}')
	sys.exit()

# Listen forever.
while True:
	# Receive from client.
	buff = s.recvfrom(BUFF_SIZE)
	data = buff[0]
	addr = buff[1]

	if not data:
		break

	# Back from bytes to string.
	data_str = str(data, 'utf-8')

	# The expected format is "KEY:VALUE".
	splits = data_str.split(':')
	if len(splits) != 2:
		break
	key = splits[0]
	val = splits[1]

	# LSX
	if 'LSX' == key:
		try:
			stick_val = float(val)
			print(f'LSX > {stick_val}')
		except ValueError:
			pass

	# LSY
	if 'LSY' == key:
		try:
			stick_val = float(val)
			print(f'LSY > {stick_val}')
		except ValueError:
			pass

	# RSX
	if 'RSX' == key:
		try:
			stick_val = float(val)
			print(f'RSX > {stick_val}')
		except ValueError:
			pass

	# RSY
	if 'RSY' == key:
		try:
			stick_val = float(val)
			print(f'RSY > {stick_val}')
		except ValueError:
			pass

	# print(f'Received data from {addr}: {data}')

s.close()