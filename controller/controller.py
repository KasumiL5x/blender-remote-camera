import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '' # https://stackoverflow.com/a/54247065
import socket
import pygame

class Controller(object):
	axis_map = {}
	button_map = {}
	dpad_map = {}
	sock = None
	deadzone = 0.2

	def setup(self) -> bool:
		pygame.init()
		pygame.joystick.init()

		if 0 == pygame.joystick.get_count():
			return False

		controller = pygame.joystick.Joystick(0)
		controller.init()

		for i in range(controller.get_numaxes()):
			self.axis_map[i] = 0.0

		for i in range(controller.get_numbuttons()):
			self.button_map[i] = False

		for i in range(controller.get_numhats()):
			self.dpad_map[i] = (0, 0)

		return True
	#end

	def connect(self):
		# Create the socket.
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		except socket.error as msg:
			print(f'Failed to create socket. Error code: {msg[0]}; Message: {msg[1]}')
			return False
		return True
	#end

	def poll(self, host, port):
		while True:
			for evt in pygame.event.get():
				if pygame.JOYAXISMOTION == evt.type:
					self.axis_map[evt.axis] = round(evt.value, 5)
				elif pygame.JOYBUTTONDOWN == evt.type:
					self.button_map[evt.button] = True
				elif pygame.JOYBUTTONUP == evt.type:
					self.button_map[evt.button] = False
				elif pygame.JOYHATMOTION == evt.type:
					self.dpad_map[evt.hat] = evt.value

				# DS4-specific mappings.
				lstick_x = self.axis_map[0]
				lstick_y = self.axis_map[1]
				rstick_x = self.axis_map[2]
				rstick_y = self.axis_map[3]

				os.system('clear')
				print('Raw:')
				print(f'LX: {lstick_x}')
				print(f'LY: {lstick_y}')
				print(f'RX: {rstick_x}')
				print(f'RY: {rstick_y}\n')

				print('Sending:')
				# Send left stick X.
				if self.stick_past_deadzone(lstick_x):
					lstick_x_str = f'LSX:{lstick_x}'
					print(lstick_x_str)
					#
					lstick_x_bytes = bytes(lstick_x_str, 'utf-8')
					self.send_data(lstick_x_bytes, host, port)

				# Send left stick Y.
				if self.stick_past_deadzone(lstick_y):
					lstick_y_str = f'LSY:{lstick_y}'
					print(lstick_y_str)
					#
					lstick_y_bytes = bytes(lstick_y_str, 'utf-8')
					self.send_data(lstick_y_bytes, host, port)

				# Send right stick X.
				if self.stick_past_deadzone(rstick_x):
					rstick_x_str = f'RSX:{rstick_x}'
					print(rstick_x_str)
					#
					rstick_x_bytes = bytes(rstick_x_str, 'utf-8')
					self.send_data(rstick_x_bytes, host, port)

				# Send right stick Y.
				if self.stick_past_deadzone(rstick_y):
					rstick_y_str = f'RSY:{rstick_y}'
					print(rstick_y_str)
					#
					rstick_y_bytes = bytes(rstick_y_str, 'utf-8')
					self.send_data(rstick_y_bytes, host, port)
		#end
	#end

	def stick_past_deadzone(self, stick_value):
		return stick_value > self.deadzone or stick_value < -self.deadzone

	def send_data(self, msg_bytes, host, port):
		try:
			self.sock.sendto(msg_bytes, (host, port))
		except socket.error as msg:
			print(f'Failed to send data. Error code: {msg[0]}; Message: {msg[1]}')
	#end

if __name__ == '__main__':
	controller = Controller()
	if controller.setup() and controller.connect():
		controller.poll('localhost', 4242)