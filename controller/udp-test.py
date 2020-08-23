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

	print(f'Received data from {addr}: {data}')

s.close()