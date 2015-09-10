import kivy
kivy.require('1.9.0')
# Fundamental imports
import os, sys, inspect
from os.path import dirname, isfile, join, split
from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
# Disable multitouch
Config.set('input', 'mouse', 'mouse,disable_multitouch')
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
subDirectory['autotiles'] = (os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0], join("graphics","autotiles")))))
subDirectory['walls'] = (os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0], join("graphics","walls")))))
subDirectory['source'] = (os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0], "source"))))
# Add subdirectories to path
for i in subDirectory.values():
	if i not in sys.path:
		sys.path.insert(0, i)
		print("Added: ", i)
# Elements from subdirectories
from canvas import MapCanvas
from palettes import Palette
from keyboard import KeyboardListener
from graphicsobject import GraphicsObject, FloorObject


class RootWidget(GridLayout):
	def __init__(self, **kwargs):
		super(RootWidget, self).__init__(**kwargs)
		self.rows = 2
		self.keyboard = KeyboardListener()
		# MENU BAR:
		self.add_widget(Button(text = "Placeholder for menu bar", size_hint_y = None, height = 20))
		self.paletteRes = [64, 32]
		
		# MAIN
		main = GridLayout(cols = 3)
		self.add_widget(main)
		
		# Center of MAIN
		self.centerSide = GridLayout(rows = 3)
		
		# Widgets of the Center area:
		self.mapCanvasScroller = ScrollView(scroll_type = ['bars'],
										bar_width = 8,
										bar_color = [0, 0, 0, 1], 
										bar_inactive_color = [0, 0, 0, .1], 
										scroll_timeout = 0)									
		self.mapCanvas = MapCanvas(size_hint = (None, None), keyboard = self.keyboard)
		
		
		# Left side of MAIN
		leftSide = GridLayout(cols = 1,
								width = self.paletteRes[0] * 4 + 8,
								size_hint_x = None)
						
		# Aspects of leftSide:
		# Scroller for the main doodad palette:
		self.objectPaletteScroller = ScrollView(scroll_type = ['bars'],
										bar_width = 8,
										bar_color = [0, 0, 0, 1],
										bar_inactive_color = [0, 0, 0, .1],
										scroll_timeout = 0)
		self.objectPalette = Palette(size_hint = (None, None), tileset = join(subDirectory['graphics'], "tileset base.png"), keyboard = self.keyboard, mapCanvas = self.mapCanvas)
		self.objectPaletteScroller.add_widget(self.objectPalette)
		
		# Structure for leftSide:
		leftSide.add_widget(Label(text = "Objects Palette", size_hint = (1, None), height = 25))
		leftSide.add_widget(self.objectPaletteScroller)
		
		# Right side of MAIN
		rightSide = GridLayout(cols = 1,
								width = 200,
								size_hint_x = None)
		
		# Add Left, Center, Right to MAIN:
		main.add_widget(leftSide)
		main.add_widget(self.centerSide)
		main.add_widget(rightSide)
		
		rightSide.add_widget(Button())
		self.centerSide.add_widget(Button(text = "Tool placeholders", size_hint_y = None, height = 25))

		self.mapCanvasScroller.add_widget(self.mapCanvas)
		self.centerSide.add_widget(self.mapCanvasScroller)
		self.centerSide.add_widget(Button(text = "Tooltip placeholder", size_hint_y = None, height = 20))
		
		self.keyboard._keyboard_open()

		
class MapMaker(App):
	def build(self):
		# width and height are that of the map, will depend on map later, random for now
		self.root = RootWidget(cols = 1)
		# listen to size and position changes
		self.root.bind(pos = self.updateLayout, size = self.updateLayout)
		with self.root.canvas.before:
			Color(0.5, 0.5, 0.5, 1)
			self.background = Rectangle()

	def updateLayout(self, instance, value):
		self.background.pos = instance.pos
		self.background.size = instance.size
		
		return self.root
		
if __name__ == "__main__":
	MapMaker().run()