import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '' # https://stackoverflow.com/a/54247065

import pygame

class Controller(object):
	axis_map = {}
	button_map = {}
	dpad_map = {}

	def setup(self) -> bool:
		pygame.init()
		pygame.joystick.init()

		if 0 == pygame.joystick.get_count():
			return False

		controller = pygame.joystick.Joystick(0)
		controller.init()

		for i in range(controller.get_numbuttons()):
			self.button_map[i] = False

		for i in range(controller.get_numhats()):
			self.dpad_map[i] = (0, 0)

		return True

	def poll(self):
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

				os.system('clear')
				print(f'Buttons: {self.button_map}')
				print(f'Axes: {self.axis_map}')
				print(f'Dpad: {self.dpad_map}')

if __name__ == '__main__':
	controller = Controller()
	if controller.setup():
		controller.poll()