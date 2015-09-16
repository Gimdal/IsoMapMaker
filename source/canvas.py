# Fundamental imports
import os, sys, inspect
from kivy.core.window import Window
# Layouts
from kivy.uix.floatlayout import FloatLayout
# Graphics Elements
from kivy.graphics import Color, Quad, Rectangle, Line
from kivy.core.image import Image
# Elements from subdirectories
from keyboard import KeyboardListener
from mapfile import MapFile

class MapCanvas(FloatLayout):
	def __init__(self, tileWidth = 64, tileHeight = 32, jCount = 23, iCount = 23, mapFile = None, keyboard = None, **kwargs):
		super(MapCanvas, self).__init__(**kwargs)
		# Width in classic coordinates of one isometric tile:
		self.tileWidth = tileWidth
		# Height in classic coordinates of one isometric tile:
		self.tileHeight = tileHeight
		# Count of isometric tiles in the i-direction,  which corresponds to isometric x
		self.iCount = iCount
		# Count of isometric tiles in the j-direction, which corresponds to isometric y
		self.jCount = jCount
		# Mapfile which contains data of each tile, including sprites and etc.
		if mapFile != None:
			self.mapFile = mapFile
		else:
			self.mapFile = MapFile(i = iCount, j = jCount, stories = 1)
		# Palettes
		self.palettes = []
		# Set size
		self.update_size()
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
		# Initial position:
		self.initialPosition = []
		# Current story
		self.currentStory = 0
		# Current layer
		self.currentLayer = 0
		# Keyboard listener:
		self.keyboard = keyboard
		# Get coefficients for i-j coordinates:
		self.get_coefficients()
		# Set up renderList and animatedList:
		self.clear_lists()
		self.populate_lists()
		# Render the map
		self.render_map()
		
		
	def update_size(self):
		# Offset for size	
		self.offset = [50, 50]
		# Width in classical coordinates, minimum being iCount * tileWidth
		self.width = (self.iCount + self.jCount) * self.tileWidth / 2 + 2 * self.offset[0]
		# Height in classical coordinates, minimum being jCount * tileHeight
		self.height = (self.iCount + self.jCount) * self.tileHeight / 2 + 2 * self.offset[1] + (len(self.mapFile.stories)) * 3 * self.tileHeight
		if self.parent != None:
			if self.parent.width > self.width:
				print("increasing x offset")
				self.width += (self.parent.width - self.width) / 2
			if self.parent.height > self.height:
				self.height += (self.parent.height - self.height) / 2 
		self.get_coefficients()
		
	def zoom(self, width, height):
		self.tileWidth = width
		self.tileHeight = height
		self.update_size()
		self.canvas.before.clear()
		self.canvas.after.clear()
		self.clear_lists()
		self.populate_lists()
		self.render_map()
		self.highlight(self.selectedTiles)
		
	def clear_lists(self):
		self.canvas.before.clear()
		self.renderList = [ [ [ [ [None] for row in range(self.jCount) ] for column in range(self.iCount)  ] for l in range(self.mapFile.layerCount)] for s in range(self.mapFile.storyCount)]
		self.animatedList =  [ [] for l in range(self.mapFile.layerCount)]
	
	def get_coefficients(self):
		self.ratio = self.tileHeight / self.tileWidth
		# For i:
		self.iCoeffMin = self.offset[1] + self.ratio * (self.offset[0] + self.jCount * self.tileWidth / 2)
		self.iCoeffMax = self.offset[1] + (self.jCount + self.iCount) * self.tileHeight / 2 + self.ratio * (self.offset[0] + self.iCount * self.tileWidth / 2)
		self.iCoeffSR = (self.iCoeffMax - self.iCoeffMin) / self.iCount
		# For j:
		self.jCoeffMin = self.offset[1] - self.ratio * (self.offset[0] + self.jCount * self.tileWidth / 2)
		self.jCoeffMax =  self.offset[1] + (self.jCount + self.iCount) * self.tileHeight / 2 - self.ratio * (self.offset[0] + self.iCount * self.tileWidth / 2)
		self.jCoeffSR = (self.jCoeffMax - self.jCoeffMin) / self.jCount	
		
	def get_coordinates(self, x, y):
		j = int((y - self.tileHeight / self.tileWidth * x - self.jCoeffMin) / self.jCoeffSR)
		i = int( (y + self.tileHeight / self.tileWidth * x - self.iCoeffMin) / self.iCoeffSR  )
		return [i, j]
		
	def on_down(self, parent, touch):
		# Function for handling what happens when one clicks anywhere on the map, with the left or right mouse button.
		# Left mouse button being pressed:		
		if 'left' in touch.button:
			if self.leftHold == True: return # To filter out undesired second click-registering:
			else:
				self.leftHold = True
				coords = self.get_coordinates(touch.pos[0], touch.pos[1])
				i = coords[0]
				j = coords[1]	
				print(i, j)
				# Check if (i, j) is within the map area:
				if i <= self.iCount - 1 and j <= self.jCount - 1 and i > - 1 and j > - 1:
					# Register the initial touch-down coordinates.
					print("in the map!")
					self.initialPosition = [i, j]
					print("initial position is:", self.initialPosition)
					# If there is no paint selected, the tile is selected.
					if self.selectedPaint == None:
						print("no paint!")
						# No ctrl is held down, meaning a new selection should be made.
						if not ('lctrl' or 'rctrl') in self.keyboard.pressedKeys:
							self.previewTiles.append(self.initialPosition)
							self.selectedTiles = []
							self.canvas.after.clear()
						# Otherwise, ctrl is held down. If not selecting an existing selection, a new should be added to already existing selections.
						elif not self.initialPosition in self.selectedTiles and ('lctrl' or 'rctrl') in self.keyboard.pressedKeys:
							self.previewTiles.append(self.initialPosition)
						# Otherwise, ctrl is held down, and an already existing selection is chosen:
						elif self.initialPosition in self.selectedTiles and ('lctrl' or 'rctrl') in self.keyboard.pressedKeys:
							self.removingTiles = True
							self.selectedTiles.remove(self.initialPosition)
							self.previewTiles.append(self.initialPosition)
							self.canvas.after.clear()
							self.highlight(self.selectedTiles)
						# If we are removing tiles, we should not be highlighting that in previewTiles.
						if self.removingTiles == False:
							self.highlight(self.previewTiles)
					else:
						if self.renderList[self.currentStory][self.currentLayer][i][j] != [None]:
							self.canvas.before.remove(self.renderList[self.currentStory][self.currentLayer][i][j])
						self.set_graphics(graphics = self.selectedPaint, i = i, j = j, layer = self.currentLayer)
		# Right mouse button being pressed:
		elif 'right' in touch.button:
			if self.rightHold == True: return #Used to filter out undesired second click-registering.
			else:
				# Register that the right mouse button is being held.
				self.rightHold = True
				if self.selectedPaint == None:
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
				else:
					self.selectedPaint = None
					self.clear_palette_selection()
					self.canvas.after.clear()
					
	def clear_palette_selection(self):
		if self.palettes != None or len(self.palettes) != 0:
			for k in range(len(self.palettes)):
				self.palettes[k].canvas.after.clear()
						
	def on_move(self, parent, touch):
		# Left mouse button is being held:
		if self.leftHold == True and self.rightHold != True:
			# Convert classical (x,y)-coordinates to isometric (i,j)-coordinates:
			coords = self.get_coordinates(touch.pos[0], touch.pos[1])
			i = coords[0]
			j = coords[1]
			# Calculate the difference between the current position and the old position.
			try:
				di = i - self.initialPosition[0]
				dj = j - self.initialPosition[1]
				if di > 0: diri = 1
				else: diri = -1
				if dj > 0: dirj = 1
				else: dirj = -1
			except:
				return
			# Before anything else, it's important that the previewTiles list is cleared of everything.
			self.previewTiles = []
			if self.selectedPaint == None:
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
				# The selected tiles must be drawn again of course, to keep them static.
				self.highlight(self.selectedTiles)
			else:
				pass
		
	def on_up(self, parent, touch):
		if 'left' in touch.button:
			self.leftHold = False
			# Confirm previews.
			if self.removingTiles == False:
				self.selectedTiles += self.previewTiles
		
			self.canvas.after.clear()
			self.highlight(self.selectedTiles)

		elif 'right' in touch.button:
			self.rightHold = False		
		
		self.removingTiles = False
		self.previewTiles = []
		self.initialPosition = []

	def highlight(self, coords):
		if self.canvas == None:
			print('Lacking canvas to paint on')
		elif len(coords) != 0:	
			for n in range(len(coords)):
				i = coords[n][0]
				j = coords[n][1]
				with self.canvas.after:
					x = [(i - j) * self.tileWidth / 2 + self.offset[0] + self.jCount * self.tileWidth/2 ,
						(i - j) * self.tileWidth / 2 + self.offset[0] + self.jCount * self.tileWidth/2 - self.tileWidth / 2,
						(i - j) * self.tileWidth / 2 + self.offset[0] + self.jCount * self.tileWidth/2 + self.tileWidth / 2]
					y = [(i + j) * self.tileHeight / 2 + self.offset[1],
						(i + j) * self.tileHeight / 2 + self.tileHeight * 0.5 + self.offset[1],
						(i + j) * self.tileHeight / 2 + self.tileHeight * 1 + self.offset[1]]
					Color(0.8, 0.8, 0, 0.75)
					Quad(points = (x[0], y[0], x[1], y[1], x[0], y[2], x[2], y[1]))
		
	def set_graphics(self, graphics, i, j, layer):
		self.unrender_tile(i, j, self.currentStory)
		self.mapFile.stories[self.currentStory].matrix[int(i)][int(j)].set_graphics(layer, graphics)
		self.populate_lists()
		self.render_tile(i, j, layer, self.currentStory)
		
	def populate_lists(self):	
		for s in range(self.currentStory + 1):
			for l in range(len(self.renderList[s])):
				for i in range(self.iCount):
					for j in range(self.jCount):		
						tile = self.mapFile.stories[self.currentStory].matrix[i][j]
						type = tile.get_graphics_type(l)
						if type[0] != None:
							graphicsInfo = tile.graphics[l]
							image = Image(graphicsInfo[0]).texture
							x = (i - j) * self.tileWidth / 2 + self.offset[0] + self.jCount * self.tileWidth / 2 
							y = (i + j) * self.tileHeight / 2 + self.offset[1]
							if (type[0] == 'object' or type[0] == 'wall') and type[1] == False:
								# Object means a rectangle, not animated means it goes into renderList
								self.renderList[s][l][i][j] = Rectangle(texture = image.get_region(graphicsInfo[1][0][0][0], graphicsInfo[1][0][0][1], graphicsInfo[2][0], graphicsInfo[2][1]), 
																		size = (self.tileWidth, self.tileWidth * graphicsInfo[2][1] / graphicsInfo[2][0]), 
																		pos = (x - self.tileWidth / 2, y) )
							
	def unrender_tile(self, i, j, s):
		for l in range(len(self.renderList[s])):
			if self.renderList[s][l][i][j] != [None]:
				self.canvas.before.remove(self.renderList[s][l][i][j])
	
	def render_tile(self, i, j, layer, story):
		tile = self.mapFile.stories[self.currentStory].matrix[i][j]
		type = 	self.mapFile.stories[story].matrix[i][j].get_graphics_type(layer)
		if type[0] != None:
			graphicsInfo = tile.graphics[layer]
			image = Image(graphicsInfo[0]).texture
			x = (i - j) * self.tileWidth / 2 +  self.offset[0] + self.jCount * self.tileWidth/2 
			y = (i + j) * self.tileHeight / 2 + self.offset[1] 
			self.renderList[story][layer][i][j].texture =  image.get_region(graphicsInfo[1][0][0][0], graphicsInfo[1][0][0][1], graphicsInfo[2][0], graphicsInfo[2][1])
			print("Type is:", type[0])
			if type[0] == 'object'  and type[1] == False:
				# Object means a rectangle, not animated means it goes into renderList
				self.renderList[story][layer][i][j].size = (self.tileWidth, self.tileWidth * graphicsInfo[2][1] / graphicsInfo[2][0])
				self.renderList[story][layer][i][j].pos =  (x - self.tileWidth/2, y)
				self.canvas.before.add(Color(1, 1, 1, 1))
				for l in range(len(self.renderList[story])):
					if self.renderList[story][l][i][j] != [None]:
						self.canvas.before.add(self.renderList[story][l][i][j])


	def render_map(self):
		self.canvas.before.clear()
		grid = []
		for i in range(self.iCount):
				for j in range(self.jCount):
					x = [(i - j) * self.tileWidth / 2 + self.offset[0] + self.jCount * self.tileWidth/2 ,
						(i - j) * self.tileWidth / 2 + self.offset[0] + self.jCount * self.tileWidth/2 - self.tileWidth / 2,
						(i - j) * self.tileWidth / 2  + self.offset[0] + self.jCount * self.tileWidth/2 + self.tileWidth / 2]
					y = [(i + j) * self.tileHeight / 2 + self.offset[1] + self.currentStory * self.tileHeight * 3,
						(i + j) * self.tileHeight / 2 + self.tileHeight * 0.5 + self.offset[1] + self.currentStory * self.tileHeight * 3,
						(i + j) * self.tileHeight / 2 + self.tileHeight + self.offset[1] + self.currentStory * self.tileHeight * 3]
					if self.currentLayer == 0:
						self.canvas.before.add(Color(0.8, 0.8, 0.8, 1))
					else:
						self.canvas.before.add(Color(0.3, 0.3, 0.5, 1))
					self.canvas.before.add(Quad(points = (x[0], y[0], x[1], y[1], x[0], y[2], x[2], y[1])))
					grid.append(Line(points = (x[0], y[0], x[1], y[1], x[0], y[2], x[2], y[1], x[0], y[0])))
		
		for i in range(len(grid)):
			if self.currentLayer == 0:
				self.canvas.before.add(Color(1, 1, 1, 1))
			else:
				self.canvas.before.add(Color(0.4, 0.4, 1, 1))
			self.canvas.before.add(grid[i])		
		
		for s in range(self.currentStory + 1):
			for l in range(len(self.renderList[s])):
				for k in range(len(self.animatedList[l])):
					self.canvas.before.add(self.animatedList[l][k][0])
				for i in range(len(self.renderList[s][l])):
					for j in range(len(self.renderList[s][l][i])):
						if self.renderList[s][l][len(self.renderList[s][l]) - i - 1][len(self.renderList[s][l][i]) - j - 1] != [None]:
							if l == self.currentLayer:
								self.canvas.before.add(Color(1, 1, 1, 1))
							elif l < self.currentLayer:
								self.canvas.before.add(Color(0.5, 0.5, 0.7, 1))
							elif l > self.currentLayer:
								self.canvas.before.add(Color(1, 1, 1, 0.2))
							self.canvas.before.add(self.renderList[s][l][len(self.renderList[s][l]) - i - 1][len(self.renderList[s][l][i]) - j - 1])			
						
		
