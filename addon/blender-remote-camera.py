# Thread class structure inspired by http://merwanachibet.net/blog/blender-long-running-python-scripts/

bl_info = {
	"name": "Blender Remote Camera",
	"author": "Daniel Green (KasumiL5x)",
	"version": (1, 0),
	"blender": (2, 83, 5),
	"location": "",
	"description": "A UDP server that translates messages into camera movement.",
	"category": "Development"
}

import bpy
import mathutils
import threading
import socket
from collections import deque

class BRCSocketThread(threading.Thread):
	command_deque = deque([], maxlen=20)
	running = False
	#
	sock = None
	host = 'localhost'
	port = 4242
	BUFF_SIZE = 1024

	def __init__(self, host, port):
		threading.Thread.__init__(self)
		self.host = host
		self.port = port
	#end

	def start(self):
		print('BRC: Starting socket thread.')
		self.running = True
		threading.Thread.start(self)
	#end

	def stop(self):
		print('BRC: Stopping socket thread.')
		self.running = False
	#end

	def run(self):
		# Create the socket.
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.sock.settimeout(3)
			# server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) ???
			# https://stackoverflow.com/questions/44387712/python-sockets-how-to-shut-down-the-server
		except socket.error as err:
			print(f'BRC: Failed to create socket. Message: {err}')
			return

		# Bind the socket.
		try:
			self.sock.bind((self.host, self.port))
			print(f'BRC: Socket bound at {self.host}:{self.port}')
		except socket.error as err:
			print(f'BRC: Failed to bind socket. Message: {err}')
			return


		while self.running:
			# Receive from client.
			try:
				buff = self.sock.recvfrom(self.BUFF_SIZE)
			except:
				# print(f'BRC: Socket timeout.')
				continue
			data = buff[0]
			addr = buff[1]

			# Back from bytes to string.
			data_str = str(data, 'utf-8')

			# Add it to the queue.
			self.command_deque.append(data_str)
		#end

		# Shutdown the socket.
		print('BRC: shutting down socket.')
		self.sock.close()

		print('BRC: Socket running loop ended.')
	#end
#end

class BRCCommand(object):
  def handle(self, context, command, value) -> bool:
    return False
  #end
#end

class BRCCommand_LSX(BRCCommand):
  def handle(self, context, command, value) -> bool:
  	if command != 'LSX':
  		return False

  	try:
  		stick_val = float(value)
  	except ValueError:
  		print(f'BRC: Handled LSX command but value was not a float ({value}).')
  		return True

  	# Verified from DEV_OT_remote_camera.poll().
  	cam = context.scene.camera
  	# cam = context.selected_objects[0]
  	cam.location += mathutils.Vector((stick_val * context.scene.brc_move_mod, 0, 0)) @ cam.matrix_world.inverted()

  	return True
  #end
#end

class BRCCommand_LSY(BRCCommand):
  def handle(self, context, command, value) -> bool:
  	if command != 'LSY':
  		return False

  	try:
  		stick_val = float(value)
  	except ValueError:
  		print(f'BRC: Handled LSXY command but value was not a float ({value}).')
  		return True

  	# Verified from DEV_OT_remote_camera.poll().
  	cam = context.scene.camera
  	# cam = context.selected_objects[0]
  	cam.location += mathutils.Vector((0, 0, stick_val * context.scene.brc_move_mod)) @ cam.matrix_world.inverted()

  	return True
  #end
#end

class BRCCommand_RSX(BRCCommand):
  def handle(self, context, command, value) -> bool:
  	if command != 'RSX':
  		return False

  	try:
  		stick_val = float(value)
  	except ValueError:
  		print(f'BRC: Handled RSX command but value was not a float ({value}).')
  		return True

  	# Verified from DEV_OT_remote_camera.poll().
  	cam = context.scene.camera
  	# cam = context.selected_objects[0]

  	LOCAL_SPACE = False
  	if LOCAL_SPACE:
  		new_quat = mathutils.Quaternion((0, -1, 0), stick_val * context.scene.brc_orient_mod)
  		cam.rotation_quaternion = cam.rotation_quaternion @ new_quat
  	else:
  		new_quat = mathutils.Quaternion((0, 0, -1), stick_val * context.scene.brc_orient_mod)
  		cam.rotation_quaternion = new_quat @ cam.rotation_quaternion

  	return True
  #end
#end

class BRCCommand_RSY(BRCCommand):
  def handle(self, context, command, value) -> bool:
  	if command != 'RSY':
  		return False

  	try:
  		stick_val = float(value)
  	except ValueError:
  		print(f'BRC: Handled RSY command but value was not a float ({value}).')
  		return True

  	# Verified from DEV_OT_remote_camera.poll().
  	cam = context.scene.camera
  	# cam = context.selected_objects[0]

  	LOCAL_SPACE = True
  	if LOCAL_SPACE:
  		new_quat = mathutils.Quaternion((1, 0, 0), stick_val * 0.1)
  		cam.rotation_quaternion = cam.rotation_quaternion @ new_quat
  	else:
  		new_quat = mathutils.Quaternion((1, 0, 0), stick_val * 0.1)
  		cam.rotation_quaternion = new_quat @ cam.rotation_quaternion

  	return True
  #end
#end

class DEV_OT_remote_camera(bpy.types.Operator):
	bl_idname = 'dev.remote_camera'
	bl_label = 'Blender Remote Camera'
	#
	brc_thread = None
	brc_timer = None
	#
	handlers = [
		BRCCommand_LSX(),
		BRCCommand_LSY(),
		BRCCommand_RSX(),
		BRCCommand_RSY()
	]

	@classmethod
	def poll(self, context):
		# Scene camera.
		return (context.scene.camera is not None) and (context.scene.camera.rotation_mode == 'QUATERNION')

		# Must have a selected camera as the first object.
		# sel = context.selected_objects
		# return len(sel) and 'CAMERA' == sel[0].type
	#end

	# Test to print the props.
	def execute(self, context):
		# Start the socket thread.
		self.brc_thread = BRCSocketThread(context.scene.brc_hostname, context.scene.brc_port)
		self.brc_thread.start()

		self.brc_timer = context.window_manager.event_timer_add(0.05, window=context.window)
		context.window_manager.modal_handler_add(self)
		return {'RUNNING_MODAL'}
	#end

	def modal(self, context, event):
		# Stop when ESC is pressed.
		if 'ESC' == event.type:
			self.brc_thread.stop()
			context.window_manager.event_timer_remove(self.brc_timer)
			return {'CANCELLED'}
		#end

		# Respond to timer firing.
		if 'TIMER' == event.type:
			if len(self.brc_thread.command_deque):
				data = self.brc_thread.command_deque.popleft()
				
				# Split the data.
				splits = data.split(':')
				if len(splits) != 2:
					print(f'BRC: Incorrect data received ({data}).')
					return {'PASS_THROUGH'} # Graceful error handling.
				key = splits[0]
				val = splits[1]

				# Handle the data.
				command_handled = False
				for handler in self.handlers:
					if handler.handle(context, key, val):
						command_handled = True
						# print(f'EVENT HANDLED BY: {handler}')
						break
				#end

				if not command_handled:
					print(f'BRC: Failed to handle command ({data}).')
			#end
		#end

		return {'PASS_THROUGH'}
	#end
#end

class DEV_PT_remote_camera(bpy.types.Panel):
	bl_label = "Blender Remote Camera"
	bl_idname = "DEV_PT_remote_camera"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "BRC"
	bl_context = "objectmode"

	def draw(self, context):
		layout = self.layout

		layout.label(text='Select a Camera')

		box = layout.box()
		box.label(text='Server Settings')
		box.prop(context.scene, 'brc_hostname', text='Host')
		box.prop(context.scene, 'brc_port', text='Port')

		box = layout.box()
		box.label(text='Camera Settings')
		box.prop(context.scene, 'brc_move_mod', text='Move Speed')
		box.prop(context.scene, 'brc_orient_mod', text='Orient Speed')

		layout.operator(DEV_OT_remote_camera.bl_idname, text='Start Listening')
	#end
#end

def register():
	bpy.types.Scene.brc_hostname = bpy.props.StringProperty(
		name = "brc_hostname",
		default = "localhost",
		description = "Hostname"
	)
	bpy.types.Scene.brc_port = bpy.props.IntProperty(
		name = "brc_port",
		default = 4242,
		description = "Port"
	)
	bpy.types.Scene.brc_move_mod = bpy.props.FloatProperty(
		name = "brc_move_mod",
		default = 0.1,
		description = "Camera movement modifier.",
		min = 0.0
	)
	bpy.types.Scene.brc_orient_mod = bpy.props.FloatProperty(
		name = "brc_orient_mod",
		default = 0.1,
		description = "Camera orientation modifier.",
		min = 0.0
	)

	bpy.utils.register_class(DEV_OT_remote_camera)
	bpy.utils.register_class(DEV_PT_remote_camera)
#end

def unregister():
	bpy.utils.unregister_class(DEV_OT_remote_camera)
	bpy.utils.unregister_class(DEV_PT_remote_camera)

	del bpy.types.Scene.brc_hostname
	del bpy.types.Scene.brc_port
	del bpy.types.Scene.brc_move_mod
	del bpy.types.Scene.brc_orient_mod
#end

if __name__ == '__main__':
	register()