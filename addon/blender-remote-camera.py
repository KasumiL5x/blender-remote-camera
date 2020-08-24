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
import socket

class DEV_OT_remote_camera(bpy.types.Operator):
	bl_idname = 'dev.remote_camera'
	bl_label = 'Blender Remote Camera'
	BUFF_SIZE = 1024
	sock = None

	@classmethod
	def poll(self, context):
		# Must have a selected camera as the first object.
		sel = context.selected_objects
		return len(sel) and 'CAMERA' == sel[0].type

	# Test to print the props.
	def execute(self, context):
		# Socket already valid?
		if self.sock is not None:
			print('BRC: Failed to create socket as it was already active.')
			return {'FINISHED'}

		# Create the socket.
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		except socket.error as err:
			print(f'BRC: Failed to create socket. Error code: {err[0]}; Message: {err[1]}')
			return {'FINISHED'}

		# Bind the socket.
		try:
			self.sock.bind((context.scene.brc_hostname, context.scene.brc_port))
			print(f'BRC: Socket bound at {context.scene.brc_hostname}:{context.scene.brc_port}')
		except socket.error as err:
			print(f'BRC: Failed to bind socket. Error code: {err[0]}; Message: {err[1]}')

		
		return {'RUNNING_MODAL'}

	#TODO: modal for the actual socket read and camera movement
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

	bpy.utils.register_class(DEV_OT_remote_camera)
	bpy.utils.register_class(DEV_PT_remote_camera)

def unregister():
	bpy.utils.unregister_class(DEV_OT_remote_camera)
	bpy.utils.unregister_class(DEV_PT_remote_camera)

	del bpy.types.Scene.brc_hostname
	del bpy.types.Scene.brc_port

if __name__ == '__main__':
	register()