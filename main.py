import kivy
kivy.require('1.9.0')
# Fundamental imports
import os, sys, inspect
from os import listdir
from os.path import dirname, isfile, join, split
from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
import pickle
# Disable multitouch
Config.set('input', 'mouse', 'mouse,disable_multitouch')
# UI Elements
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
# Layouts
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.dropdown import DropDown
# Graphics Elements
from kivy.core.image import Image
from kivy.graphics import Color, Quad, Rectangle, Line
# List subdirectories
import globals
# Elements from subdirectories
from canvas import MapCanvas
from mapfile import MapFile
from palettes import Palette
from keyboard import KeyboardListener
from graphicsobject import GraphicsObject, FloorObject


class RootWidget(GridLayout):
	def __init__(self, **kwargs):
		super(RootWidget, self).__init__(**kwargs)
		self.rows = 2
		self.keyboard = KeyboardListener()
		self.paletteRes = [64, 32]
		
		# # # # # # # # # # #
		# MENU BAR:
		# # # # # # # # # # #
		menu = GridLayout(size_hint_y = None, height = 20, rows = 1)
		# Parts of the Menu Bar
		# NEW MAP
		# Button to open the popup:
		newMapButton = Button(text = "New Map")
		# Layout of the popup
		newMapContent = GridLayout(rows = 2, cols = 2)
		newMapContentInputs = GridLayout(rows = 2, cols = 3)
		newMapContent.add_widget(newMapContentInputs)
		newMapContent.add_widget(Label(text = ("Define width (I) and \n height (J) and \n no. stories to create \n a new map.")))
		# Actual popup window
		self.newMapPopup = Popup(title = "New Map", content = newMapContent, size_hint = (None, None), height = 200, width = 320, auto_dismiss = False)
		# Width / Height / Stories inputs -- very important!
		self.newMapWidthInput = TextInput(input_filter = 'int', multiline = False, size_hint = (1, None), height = 28, text = "12")
		self.newMapHeightInput = TextInput(input_filter = 'int', multiline = False, size_hint = (1, None), height = 28, text = "14")
		self.newMapStoriesInput = TextInput(input_filter = "int", multiline = False, size_hint = (1, None), height = 28, text = "1")
		# Confirmation button and cancel button
		newMapOKButton = Button(text = "OK", size_hint_y = None, height = 25)
		newMapCancelButton = Button(text = "Cancel", size_hint_y = None, height = 25)
		# Add inputs, labels and buttons to the content of the popup:
		newMapContentInputs.add_widget(Label(text = "I", size_hint = (1, None), height = 25))
		newMapContentInputs.add_widget(Label(text = "J", size_hint = (1, None), height = 25))
		newMapContentInputs.add_widget(Label(text = "Stories", size_hint = (1, None), height = 25))
		newMapContentInputs.add_widget(self.newMapWidthInput)
		newMapContentInputs.add_widget(self.newMapHeightInput)
		newMapContentInputs.add_widget(self.newMapStoriesInput)
		newMapContent.add_widget(newMapOKButton)
		newMapContent.add_widget(newMapCancelButton)
		# New Map button bindings:
		newMapButton.bind(on_press = self.newMapPopup.open)
		newMapOKButton.bind(on_press = self.new_map)
		newMapCancelButton.bind(on_press = self.newMapPopup.dismiss)
		
		# SAVE MAP:
		saveMapButton = Button(text = "Save Map")
		# Save Map Button Bindings:
		saveMapButton.bind(on_press = self.save_map)
		
		# LOAD MAP:
		# Button to open the popup:
		loadMapButton = Button(text = "Load Map")
		# Layout for the popup:
		loadMapContent = GridLayout(rows = 2)
		loadMapFileScroller = ScrollView()
		loadMapListLayout = GridLayout(rows = 10, size_hint = (None, None))
		loadMapLowerRegion = GridLayout(cols = 3, size_hint = (1, None), height = 35)
		loadMapContent.add_widget(loadMapFileScroller)
		loadMapContent.add_widget(loadMapLowerRegion)
		# Actual Popup window:
		self.loadMapPopup = Popup(title = "Load Map", content = loadMapContent, size_hint = (None, None), height = 400, width = 500, auto_dismiss = False)
		# Lower Region Buttons and Label
		self.loadMapSelectedFileLabel = Label(text = "No map chosen", size_hint = (1, None), height = 35)
		loadMapOKButton = Button(text = "Load", disabled = True, size_hint = (0.2, None), height = 30)
		loadMapCancelButton = Button(text = "Cancel", size_hint = (0.2, None), height = 30)
		# Populate the MapList with files.
		mapsList = [f for f in listdir(globals.subDirectory['maps']) if (f[-4:] == ".msf")]
		for n in range(len(mapsList)):
			b = Button(text = mapsList[n], 
						size_hint = (1, None), 
						height = 30)
			b.bind(on_press = lambda x: setattr(self.loadMapSelectedFileLabel, "text", x.text))
			b.bind(on_press = lambda x: setattr(loadMapOKButton, "disabled", False))
			loadMapListLayout.add_widget(b)
		# Adding labels and buttons to the content of the popup:
		loadMapFileScroller.add_widget(loadMapListLayout)
		loadMapLowerRegion.add_widget(self.loadMapSelectedFileLabel)
		loadMapLowerRegion.add_widget(loadMapOKButton)
		loadMapLowerRegion.add_widget(loadMapCancelButton)
		# Load Map Button Bindings:
		loadMapOKButton.bind(on_press = self.load_map)
		loadMapOKButton.bind(on_release = lambda x: setattr(loadMapOKButton, "disabled", True))
		loadMapCancelButton.bind(on_release = lambda x: setattr(loadMapOKButton, "disabled", True))
		loadMapCancelButton.bind(on_press = self.loadMapPopup.dismiss)
		
		loadMapButton.bind(on_press = self.loadMapPopup.open)
		
		# Structure of the Menu Bar
		menu.add_widget(newMapButton)
		menu.add_widget(saveMapButton)
		menu.add_widget(loadMapButton)
		
		self.add_widget(menu)
		
		
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
		# Toolbar part: Eraser
		
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
		paletteOffset = 4
		leftSide = GridLayout(cols = 1,
								width = self.paletteRes[0] * 4 + 2 * paletteOffset,
								size_hint_x = None)
						
		# PARTS OF LEFT SIDE
		# Scroller for the main object palette:
		self.objectPaletteScroller = ScrollView(scroll_type = ['bars'],
										size_hint = (1, None),
										height = 4 * self.paletteRes[0],
										bar_width = 8,
										bar_color = [0, 0, 0, 1],
										bar_inactive_color = [0, 0, 0, .1],
										scroll_timeout = 0)
		self.objectPalette = Palette(size_hint = (None, None), 
									tileset = join(globals.subDirectory['graphics'], "wall base.png"), 
									keyboard = self.keyboard, 
									mapCanvas = self.mapCanvas,
									offset = paletteOffset)
		self.objectPaletteScroller.add_widget(self.objectPalette)
		
		
		# Scroller for autotile palettes
		# Add palettes to main canvas
		self.mapCanvas.palettes.append(self.objectPalette)
		
		# Structure for leftSide:
		leftSide.add_widget(Label(text = "Objects Palette", size_hint = (1, None), height = 25))
		leftSide.add_widget(self.objectPaletteScroller)

		
		# # # # # # # # # # #
		# RIGHT side of MAIN
		# # # # # # # # # # #
		rightSide = GridLayout(cols = 1,
								width = 200,
								size_hint_x = None)
		# PARTS OF RIGHT SIDE
		# Map Properties
		mapProperties = GridLayout(cols = 1, size_hint = (1, None), height = 180)
		self.mapPropertiesNameInput = TextInput(hint_text = "New Map", multiline = False, size_hint = (1, None), height = 30)
		self.mapPropertiesIDInput = TextInput(hint_text = "ID", multiline = False, size_hint = (1, None), height = 30)
		self.sizeLabel = Label(text = str("Size: " + str(self.mapCanvas.iCount) + " X " + str(self.mapCanvas.jCount) + " X " + str(len(self.mapCanvas.mapFile.stories))), size_hint = (1, None), height = 30)
		changeSizeButton = Button(text = "Change Size", size_hint = (1, None), height = 30)
		mapProperties.add_widget(Label(text = "Map Name:"))
		mapProperties.add_widget(self.mapPropertiesNameInput)
		mapProperties.add_widget(Label(text = "Map ID:"))
		mapProperties.add_widget(self.mapPropertiesIDInput)
		mapProperties.add_widget(self.sizeLabel)
		mapProperties.add_widget(changeSizeButton)
		# Story Selection
		
		# Layer Selection
		layerSelection = GridLayout(cols = 1)
		for l in range(6):
			text = "Layer " + str(5 - l)
			button = Button(text = text,
							size_hint = (1, None),
							height = 35)
			button.id = str(5 - l)
			button.bind(on_press = self.change_layer)
			layerSelection.add_widget(button)
		# Structure for rightSide:
		rightSide.add_widget(Label(text = "Map Properties",
									size_hint = (1, None),
									height = 25))
		rightSide.add_widget(mapProperties)
		rightSide.add_widget(Label(text = ("Layer Selection"),
									size_hint = (1, None),
									height = 25))
		rightSide.add_widget(layerSelection)
		
		# Add Left, Center, Right to MAIN:
		main.add_widget(leftSide)
		main.add_widget(self.centerSide)
		main.add_widget(rightSide)
		
		self.centerSide.add_widget(toolbar)

		self.centerSide.add_widget(mapCanvasScroller)
		self.centerSide.add_widget(Button(text = "Tooltip placeholder", size_hint_y = None, height = 20))
		
		self.keyboard._keyboard_open()
	
	def new_map(self, button):
		# Calls functions from canvas.py
		# Uses data from newMap-section of this .py file
		self.mapCanvas.mapFile = MapFile(i = int(self.newMapWidthInput.text), j = int(self.newMapHeightInput.text), stories = int(self.newMapStoriesInput.text) )
		self.mapCanvas.currentStory = 0
		self.mapCanvas.iCount = int(self.newMapWidthInput.text)
		self.mapCanvas.jCount = int(self.newMapHeightInput.text)
		self.mapCanvas.update_size()
		self.mapCanvas.get_coefficients()
		self.mapCanvas.clear_lists()
		self.mapCanvas.populate_lists()
		self.mapCanvas.render_map()	
		self.newMapPopup.dismiss()
	
	def save_map(self, button):
		if self.mapCanvas.mapFile.ID == "": return print("I refuse to save a nameless map!")
		saveDirectory = join(globals.subDirectory['maps'], str(self.mapCanvas.mapFile.ID) + ".msf")
		saveFile = open(saveDirectory, "wb")
		pickle.dump(self.mapCanvas.mapFile, saveFile)
		saveFile.close()
		print("Map saved as",  str(self.mapCanvas.mapFile.ID)+ ".msf")
	
	def load_map(self, button):
		file = open(join(globals.subDirectory['maps'], self.loadMapSelectedFileLabel.text), "rb")
		self.mapCanvas.mapFile = pickle.load(file)
		file.close()
		self.mapCanvas.currentStory = 0
		self.mapCanvas.iCount = int(self.newMapWidthInput.text)
		self.mapCanvas.jCount = int(self.newMapHeightInput.text)
		self.mapCanvas.update_size()
		self.mapCanvas.get_coefficients()
		self.mapCanvas.clear_lists()
		self.mapCanvas.populate_lists()
		self.mapCanvas.render_map()	
		self.newMapPopup.dismiss()
		self.loadMapPopup.dismiss()
	
	def change_layer(self, button):
		#Changes attributes in the canvas.py file
		self.mapCanvas.currentLayer = int(button.id)
		self.mapCanvas.render_map()
		
	def zoom_in(self, touch):
		#Changes attributes in the canvas.py file
		if self.mapCanvas.tileWidth == 32:
			self.zoomOut.disabled = False
		if self.mapCanvas.tileWidth < 128:
			self.mapCanvas.zoom(self.mapCanvas.tileWidth * 2, self.mapCanvas.tileHeight * 2)
			if self.mapCanvas.tileWidth == 128:
				self.zoomIn.disabled = True
		
	def zoom_out(self, touch):	
		#Changes attributes in the canvas.py file
		if self.mapCanvas.tileWidth == 128:
			self.zoomIn.disabled = False
		if self.mapCanvas.tileWidth > 32 and self.mapCanvas.tileHeight > 16:
			self.mapCanvas.zoom(self.mapCanvas.tileWidth / 2, self.mapCanvas.tileHeight / 2)
			self.mapCanvas.update_size()
			if self.mapCanvas.tileWidth == 32:
				self.zoomOut.disabled = True
		
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