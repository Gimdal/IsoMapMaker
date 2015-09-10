#Fundamental imports
from kivy.core.window import Window

class KeyboardListener():
	def __init__(self, **kwargs):
		self._keyboard_open()
		self.pressedKeys = []
		
	def _keyboard_open(self):
		# Used to add keyboard functionality. This must be called whenever one loses focus to other text-inputs in the editor. Very important!
		# Keyboard listener:
		self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
		# Bind keyboard.
		self._keyboard.bind(on_key_down = self._on_keyboard_down)
		self._keyboard.bind(on_key_up = self._on_keyboard_up)
		
	def _keyboard_closed(self):
		# Used to remove the keyboard functionality
		self._keyboard.unbind(on_key_down = self._on_keyboard_down)
		self._keyboard.unbind(on_key_up = self._on_keyboard_up)
		self._keyboard = None
		
	def _on_keyboard_down(self, *args):
		# In args, args[1][1] is the key pressed. Add it to the list:
		if not args[1][1] in self.pressedKeys:
			self.pressedKeys.append(str(args[1][1]))
	
	def _on_keyboard_up(self, *args):
		# The key pressed lies in args[1][1]
		self.pressedKeys.remove(str(args[1][1]))