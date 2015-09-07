# Fundamental imports
import os, sys, inspect
from kivy.core.window import Window
# Layouts
from kivy.uix.floatlayout import FloatLayout
# Graphics Elements
from kivy.graphics import Color, Quad, Rectangle, Line
from kivy.core.image import Image

class MapCanvas(FloatLayout):
	def __init__(self, tileWidth = 64, tileHeight = 32, iCount = 14, jCount = 14, mapFile = None, **kwargs):
		super(MapCanvas, self).__init__(**kwargs)
		# Width in classic coordinates of one isometric tile:
		self.tileWidth = tileWidth
		# Height in classic coordinates of one isometric tile:
		self.tileHeight = tileHeight
		# Count of isometric tiles in the i-direction,  which corresponds to isometric x
		self.iCount = iCount
		# Count of isometric tiles in the j-direction, which corresponds to isometric y
		self.jCount = jCount
		# Width in classical coordinates, minimum being iCount * tileWidth
		self.width = self.iCount * self.tileWidth + 2 * self.tileWidth
		# Height in classical coordinates, minimum being jCount * tileHeight
		self.height = self.jCount * self.tileHeight + 2 * self.tileHeight
		# Mapfile which contains data of each tile, including sprites and etc.
		self.mapFile = mapFile
		# Bindings for the drawing functionality
		self.bind(on_touch_down = self.on_down)
		self.bind(on_touch_move = self.on_move)
		self.bind(on_touch_up = self.on_up)
		# Tracking if a mouse key is held down:
		self.leftHold = self.rightHold = self.removingTiles = False
		# Initially, no sprite is selected to paint with.
		self.selectedPaint = None
		# Initially, no tiles are selected.
		self.selectedTiles = []
		# Initially, no tiles are being previewed for change either.
		self.previewTiles = []
		# Keys on keyboard being pressed:
		self.pressedKeys = []
		# Initial position:
		self.initialPosition = []
		# Render the basic map.
		self._keyboard_open()
		self.render_map()
		self.grid = []
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

	def on_down(self, parent, touch):
		# Function for handling what happens when one clicks anywhere on the map, with the left or right mouse button.
		# Left mouse button being pressed:		
		if 'left' in touch.button:
			if self.leftHold == True: return # To filter out undesired second click-registering:
			else:
				# Register that the left mouse button is being held.
				self.leftHold = True
				# Convert classical (x,y)-coordinates to isometric (i,j)-coordinates:
				j = (- 0.5 * touch.pos[0] + 0.5 * (self.width / 2) + touch.pos[1] - self.tileHeight) // self.tileHeight
				i = (0.5 * touch.pos[0] - 0.5 * (self.width / 2) + touch.pos[1] - self.tileHeight) // self.tileHeight
				# Check if (i, j) is within the map area:
				if i <= self.iCount - 1 and j <= self.jCount - 1 and i > - 1 and j > - 1:
					# Register the initial touch-down coordinates.
					self.initialPosition = [i, j]
					# If there is no paint selected, the tile is selected.
					if self.selectedPaint == None:
						# No ctrl is held down, meaning a new selection should be made.
						if not ('lctrl' or 'rctrl') in self.pressedKeys:
							self.previewTiles.append(self.initialPosition)
							self.selectedTiles = []
							self.canvas.after.clear()
						# Otherwise, ctrl is held down. If not selecting an existing selection, a new should be added to already existing selections.
						elif not self.initialPosition in self.selectedTiles and ('lctrl' or 'rctrl') in self.pressedKeys:
							self.previewTiles.append(self.initialPosition)
						# Otherwise, ctrl is held down, and an already existing selection is chosen:
						elif self.initialPosition in self.selectedTiles and ('lctrl' or 'rctrl') in self.pressedKeys:
							self.removingTiles = True
							self.selectedTiles.remove(self.initialPosition)
							self.previewTiles.append(self.initialPosition)
							self.canvas.after.clear()
							self.highlight(self.selectedTiles)
						# If we are removing tiles, we should not be highlighting that in previewTiles.
						if self.removingTiles == False:
							self.highlight(self.previewTiles)
							
		# Right mouse button being pressed:
		elif 'right' in touch.button:
			if self.rightHold == True: return #Used to filter out undesired second click-registering.
			else:
				# Register that the right mouse button is being held.
				self.rightHold = True
				# Check if left is held. Then merely cancel whatever left is doing. If not removing tiles, remove tiles:
				if self.leftHold == True and self.removingTiles == False:
					self.previewTiles = []
					self.canvas.after.clear()
					self.highlight(self.selectedTiles)
				# If left is being held, and we are removing tiles, re-add the tiles.
				elif self.leftHold == True and self.removingTiles == True:
					self.selectedTiles += self.previewTiles
					self.previewTiles = []
					self.canvas.after.clear()
					self.highlight(self.selectedTiles)
				# Conditions for what to happen if left is not being pressed shall go below here once implimented.
				elif self.leftHold == False:
					self.selectedTiles = self.previewTiles = []
					self.canvas.after.clear()
				
	def on_move(self, parent, touch):
		# Left mouse button is being held:
		if self.leftHold == True and self.rightHold != True:
			# Convert classical (x,y)-coordinates to isometric (i,j)-coordinates:
			j = (- 0.5 * touch.pos[0] + 0.5 * (self.width / 2) + touch.pos[1] - self.tileHeight) // self.tileHeight
			i = (0.5 * touch.pos[0] - 0.5 * (self.width / 2) + touch.pos[1] - self.tileHeight) // self.tileHeight
			# Calculate the difference between the current position and the old position.
			di = i - self.initialPosition[0]
			dj = j - self.initialPosition[1]
			if di > 0: diri = 1
			else: diri = -1
			if dj > 0: dirj = 1
			else: dirj = -1
			# Before anything else, it's important that the previewTiles list is cleared of everything.
			self.previewTiles = []
			# Clear the drawn highlighted tiles in preparation. This will ensure that the dragged square will be able to update itself in real time.
			self.canvas.after.clear()
			# Adding tiles to the drawn square:
			for n in range(abs(int(di))+1):
				for m in range(abs(int(dj))+1):
					# Depending on whether we are removing tiles or not, different functionality will now happen for these square tiles.
					if self.removingTiles == False:
						# If we are not removing tiles, tiles should be added to the preview, but only if they are within the map area, and not already selected:
						# This long if-chain ensures the above critera are followed:
						if not [self.initialPosition[0] + diri * n, self.initialPosition[1] + dirj * m] in self.selectedTiles and self.initialPosition[0] + diri * n > -1 and self.initialPosition[1] + dirj * m > -1 and self.initialPosition[0] + diri * n < self.iCount and self.initialPosition[1] + dirj * m < self.jCount:
							#Assuming this condition is met, add the coordinates to the preview list:
							self.previewTiles.append([self.initialPosition[0] + diri * n, self.initialPosition[1] + dirj * m])
							#Highlight this tile:
							self.highlight([[self.initialPosition[0] + diri * n, self.initialPosition[1] + dirj * m]])
					else:
						# If we are removing tiles, the tiles we pass that are already part of the selected tiles list should be put in a backup, and removed.
						if [self.initialPosition[0] + diri * n, self.initialPosition[1] + dirj * m] in self.selectedTiles:
							self.previewTiles.append([self.initialPosition[0] + diri * n, self.initialPosition[1] + dirj * m])
							self.selectedTiles.remove([self.initialPosition[0] + diri * n, self.initialPosition[1] + dirj * m])
					
			# The selected tiles must be drawn again of course, to keep them static.
			self.highlight(self.selectedTiles)

		
	def on_up(self, parent, touch):
		if 'left' in touch.button:
			self.leftHold = False
			# Confirm previews.
			print(self.previewTiles)
			if self.removingTiles == False:
				self.selectedTiles += self.previewTiles
			print(self.selectedTiles)
			self.canvas.after.clear()
			self.highlight(self.selectedTiles)
			self.previewTiles = []

		elif 'right' in touch.button:
			self.rightHold = False		
		self.removingTiles = False
		self.previewTiles = []
		#if self.selectedPaint == None:
			#self.highlight(self.selectedTiles)
		
	def cancel_preview(self):
		self.leftHold = self.rightHold = False
		print("Preview cancelled")

	def highlight(self, coords):
		if self.canvas == None:
			print('Lacking canvas to paint on')
		elif len(coords) != 0:		
			for n in range(len(coords)):
				i = coords[n][0]
				j = coords[n][1]
				with self.canvas.after:
					x = [(i - j) * self.tileWidth / 2 + self.width / 2,
						(i - j) * self.tileWidth / 2 + self.width / 2 - self.tileWidth / 2,
						(i - j) * self.tileWidth / 2 + self.width / 2 + self.tileWidth / 2]
					y = [(i + j) * self.tileHeight / 2 + self.tileHeight,
						(i + j) * self.tileHeight / 2 + self.tileHeight * 1.5,
						(i + j) * self.tileHeight / 2 + self.tileHeight * 2]
					Color(0.8, 0.8, 0, 0.75)
					Quad(points = (x[0], y[0], x[1], y[1], x[0], y[2], x[2], y[1]))
		
	def set_graphics(self, graphics, i, j):
		pass
		
	def render_map(self):
		self.grid = [[None for n in range(self.iCount)] for m in range(self.jCount)]
		self.canvas.before.clear()
		for i in range(self.iCount):
			for j in range(self.jCount):
				x = [(i - j) * self.tileWidth / 2 + self.width / 2,
					(i - j) * self.tileWidth / 2 + self.width / 2 - self.tileWidth / 2,
					(i - j) * self.tileWidth / 2 + self.width / 2 + self.tileWidth / 2]
				y = [(i + j) * self.tileHeight / 2 + self.tileHeight,
					 (i + j) * self.tileHeight / 2 + self.tileHeight * 1.5,
					 (i + j) * self.tileHeight / 2 + self.tileHeight * 2]

				with self.canvas.before:
					Color(0.8, 0.8, 0.8, 0.8)
					Quad(points = (x[0], y[0], x[2], y[1], x[0], y[2], x[1], y[1]), Color = (0.4, .4, .4, 1))
					Color(1, 1, 1, 1)
					Line(points = (x[0], y[0], x[2], y[1], x[0], y[2], x[1], y[1], x[0], y[0]), width = 1)