import kivy
kivy.require('1.9.0')
# Fundamental imports
import os, sys, inspect
from os.path import dirname, isfile, join, split
from kivy.app import App
from kivy.config import Config
# Disable multitouch
Config.set('input', 'mouse', 'mouse,disable_multitouch')
from kivy.core.window import Window
# UI Elements
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
# Layouts
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.dropdown import DropDown
# Graphics Elements
from kivy.core.image import Image
from kivy.graphics import Color, Quad, Rectangle, Line
# List subdirectories
subDirectory = {}
subDirectory['graphics'] = (os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0], "graphics"))))
subDirectory['source'] = (os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0], "source"))))
# Add subdirectories to path
for i in subDirectory.values():
	if i not in sys.path:
		sys.path.insert(0, i)
		print(i)
# Elements from subdirectories
from canvas import MapCanvas

#paletteTileRes = 32
#tileRes = 32
#terrainTypes = ['grass', 'forest', 'mountain', 'river', 'lava', 'ice']


class RootWidget(GridLayout):
	def __init__(self, **kwargs):
		super(RootWidget, self).__init__(**kwargs)
		self.rows = 2
		i_count = 12 
		j_count = 12
		iso_width = 64
		iso_height = 32
		self.add_widget(Button(text = "Placeholder for menu bar", size_hint_y = None, height = 20))
		main = GridLayout(cols = 3)
		leftSide = GridLayout(cols = 1,
								width = 200,
								size_hint_x = None)
		self.centerSide = GridLayout(rows = 3)
		rightSide = GridLayout(cols = 1,
								width = 200,
								size_hint_x = None)
		main.add_widget(leftSide)
		main.add_widget(self.centerSide)
		main.add_widget(rightSide)
		self.add_widget(main)
		leftSide.add_widget(Button())
		rightSide.add_widget(Button())
		self.centerSide.add_widget(Button(text = "Tool placeholders", size_hint_y = None, height = 25))
		self.mapCanvasScroller = ScrollView(scroll_type = ['bars'],
										bar_width = 8,
										bar_color = [0, 0, 0, 1], 
										bar_inactive_color = [0, 0, 0, .1], 
										scroll_timeout = 0)									
		self.mapCanvas = MapCanvas(size_hint = (None, None), size = (4000, 3000))
		self.mapCanvasScroller.add_widget(self.mapCanvas)
		self.centerSide.add_widget(self.mapCanvasScroller)
		self.centerSide.add_widget(TextInput(text = "Tooltip placeholder", size_hint_y = None, height = 20, multiline = False))
		#Test population
		base = Image(join(subDirectory['graphics'], 'isotilebase.png')).texture
		
					
class MapMaker(App):
	def build(self):
		# width and height are that of the map, will depend on map later, random for now
		self.root = RootWidget(cols = 1)
		# listen to size and position changes
		self.root.bind(pos = self.updateLayout, size = self.updateLayout)
		with self.root.canvas.before:
			Color(0.5, 0.5, 0.5, 1)
			self.background = Rectangle()
		
		return self.root
		print(self.root.children)
	def updateLayout(self, instance, value):
		self.background.pos = instance.pos
		self.background.size = instance.size
		
		return self.root
		
if __name__ == "__main__":
	MapMaker().run()