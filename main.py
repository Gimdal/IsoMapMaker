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
		
		# # # # # # # # # # #
		# CENTER side of MAIN
		# # # # # # # # # # #
		self.centerSide = GridLayout(rows = 3)
		# PARTS OF CENTER SIDE
		# Scroller for the map canvas
		mapCanvasScroller = ScrollView(scroll_type = ['bars'],
										bar_width = 8,
										bar_color = [0, 0, 0, 1], 
										bar_inactive_color = [0, 0, 0, .1], 
										scroll_timeout = 0)									
		self.mapCanvas = MapCanvas(size_hint = (None, None), keyboard = self.keyboard)
		mapCanvasScroller.add_widget(self.mapCanvas)
		self.mapCanvas.update_size()
		
		# Toolbar
		toolbar = GridLayout(size_hint = (1, None), 
									height = 30,
									rows = 1)
		# Toolbar part: Zoom In
		self.zoomIn = Button(text = ("Zoom In"))
		self.zoomIn.bind(on_press = self.zoom_in)
		# Toolbar part: Zoom Out
		self.zoomOut = Button(text = ("Zoom Out"))
		self.zoomOut.bind(on_press = self.zoom_out)
		
		toolbar.add_widget(self.zoomIn)
		toolbar.add_widget(self.zoomOut)
		
		
		
		# # # # # # # # # # #
		# LEFT side of MAIN
		# # # # # # # # # # #
		leftSide = GridLayout(cols = 1,
								width = self.paletteRes[0] * 4 + 8,
								size_hint_x = None)
						
		# PARTS OF LEFT SIDE
		# Scroller for the main object palette:
		self.objectPaletteScroller = ScrollView(scroll_type = ['bars'],
										bar_width = 8,
										bar_color = [0, 0, 0, 1],
										bar_inactive_color = [0, 0, 0, .1],
										scroll_timeout = 0)
		self.objectPalette = Palette(size_hint = (None, None), tileset = join(subDirectory['graphics'], "tileset base.png"), keyboard = self.keyboard, mapCanvas = self.mapCanvas)
		self.objectPaletteScroller.add_widget(self.objectPalette)
		# Scroller for wall palettes
		self.wallPaletteScroller = ScrollView(scroll_type = ['bars'],
										bar_width = 8,
										bar_color = [0, 0, 0, 1],
										bar_inactive_color = [0, 0, 0, .1],
										scroll_timeout = 0)
		self.wallPalette = Palette(size_hint = (None, None), res = [64, 96], tileset = join(subDirectory['walls'], "wall base.png"), keyboard = self.keyboard, mapCanvas = self.mapCanvas)
		self.wallPaletteScroller.add_widget(self.wallPalette)
		
		# Scroller for autotile palettes
		# Add palettes to main canvas
		self.mapCanvas.palettes.append(self.objectPalette)
		self.mapCanvas.palettes.append(self.wallPalette)
		
		# Structure for leftSide:
		leftSide.add_widget(Label(text = "Objects Palette", size_hint = (1, None), height = 25))
		leftSide.add_widget(self.objectPaletteScroller)
		leftSide.add_widget(Label(text = "Wall Palette", size_hint = (1, None), height = 25))
		leftSide.add_widget(self.wallPaletteScroller)
		
		# # # # # # # # # # #
		# RIGHT side of MAIN
		# # # # # # # # # # #
		rightSide = GridLayout(cols = 1,
								width = 200,
								size_hint_x = None)
		# PARTS OF RIGHT SIDE
		# Layer Selection
		layerSelection = GridLayout(cols = 1)
		for l in range(6):
			text = "Layer " + str(l)
			button = Button(text = text,
							size_hint = (1, None),
							height = 35)
			button.id = str(l)
			button.bind(on_press = self.change_layer)
			layerSelection.add_widget(button)
		# Structure for rightSide:
		rightSide.add_widget(Label(text = ("Layer Selection"),
									size_hint = (1, None),
									height = 25))
		rightSide.add_widget(layerSelection)
		# Add Left, Center, Right to MAIN:
		main.add_widget(leftSide)
		main.add_widget(self.centerSide)
		main.add_widget(rightSide)
		
		rightSide.add_widget(Button())
		self.centerSide.add_widget(toolbar)

		self.centerSide.add_widget(mapCanvasScroller)
		self.centerSide.add_widget(Button(text = "Tooltip placeholder", size_hint_y = None, height = 20))
		
		self.keyboard._keyboard_open()
		
	def change_layer(self, button):
		self.mapCanvas.currentLayer = int(button.id)
		
	def zoom_in(self, touch):
		if self.mapCanvas.tileWidth == 32:
			self.zoomOut.color = (1, 1, 1, 1)
		if self.mapCanvas.tileWidth < 128:
			self.mapCanvas.zoom(self.mapCanvas.tileWidth * 2, self.mapCanvas.tileHeight * 2)
			if self.mapCanvas.tileWidth == 128:
				self.zoomIn.color = (0.5, 0.5, 0.5, 1)
		
	def zoom_out(self, touch):	
		if self.mapCanvas.tileWidth == 128:
			self.zoomIn.color = (1, 1, 1, 1)
		if self.mapCanvas.tileWidth > 32 and self.mapCanvas.tileHeight > 16:
			self.mapCanvas.zoom(self.mapCanvas.tileWidth / 2, self.mapCanvas.tileHeight / 2)
			self.mapCanvas.update_size()
			if self.mapCanvas.tileWidth == 32:
				self.zoomOut.color = (0.5, 0.5, 0.5, 1)
		
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