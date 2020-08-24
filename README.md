# Blender Remote Camera
> A Blender plugin to remotely control the scene camera over UDP network sockets.

### What/Why?
This project was created to explore Blender's addon ecosystem and to learn the paradigms it uses.  Why? Good question.

There are two components in this project — a Blender addon and a client application that emits commands from controller input.

## Usage
### Client Application
Run the `controller/controller.py` script. It is configured to send both sticks X/Y values for a DS4, so feel free to change this where applicable.
The client will send out formatted network packets over UDP, which the plugin will receive and interpret.

### Blender Addon
Install the Blender addon from the file `addon/blender-remote-camera.py`. Once enabled it will be available from your sidebar in a tab titled `BRC` nearby `Item`/`Tool`/`View`.

The panel can be used to configure the server settings (defaults will work with the client app) and the runtime settings.

Pressing the `Start Listening` button will enable the command. To cancel it, make sure the 3D viewport has focus and press `ESC`.

If the `Start Listening` button is grayed out, your camera isn't configured. For this plugin, the scene camera needs to be present and have its rotation mode set to `Quaternion` (by default this is set to `XYZ Euler`.

## Tech Stack
* Blender v2.83.5
* Python 3.x (client app)
* pygame (for reading DS4 in the client app)

## Preview
Curious but don't want to try it? Gotcha covered fam.

### Complete Video
![](https://github.com/KasumiL5x/blender-remote-camera/raw/master/demo/demo.gif)

### The UI Within Blender
![](https://github.com/KasumiL5x/blender-remote-camera/raw/master/demo/ui.png)
