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
	def __init__(self, tileWidth = 64, tileHeight = 32, jCount = 14, iCount = 12, mapFile = None, keyboard = None, **kwargs):
		super(MapCanvas, self).__init__(**kwargs)
		# Width in classic coordinates of one isometric tile:
		self.tileWidth = tileWidth
		# Height in classic coordinates of one isometric tile:
		self.tileHeight = tileHeight
		# Count of isometric tiles in the i-direction,  which corresponds to isometric x
		self.iCount = iCount
		# Count of isometric tiles in the j-direction, which corresponds to isometric y
		self.jCount = jCount
		# Offset for size
		self.offset = [2 * self.tileWidth, 2 * self.tileHeight]
		# Width in classical coordinates, minimum being iCount * tileWidth
		self.width = self.iCount * self.tileWidth + self.offset[0]
		# Height in classical coordinates, minimum being jCount * tileHeight
		self.height = self.jCount * self.tileHeight + self.offset[1]
		# Mapfile which contains data of each tile, including sprites and etc.
		if mapFile != None:
			self.mapFile = mapFile
		else:
			self.mapFile = MapFile(i = iCount, j = jCount, stories = 1)
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
		# Set up renderList.
		self.renderList = [ [ [ [ [None] for row in range(self.jCount) ] for column in range(self.iCount)  ] for l in range(self.mapFile.layerCount)] for s in range(self.mapFile.storyCount)]
		# This should result in renderList[story][layer][i][j]
		# Next is animatedList
		self.animatedList = [ [] for l in range(self.mapFile.layerCount)]
		
		self.populate_lists()
		self.render_map()
		# Keyboard listener:
		self.keyboard = keyboard		

	def on_down(self, parent, touch):
		# Function for handling what happens when one clicks anywhere on the map, with the left or right mouse button.
		# Left mouse button being pressed:		
		if 'left' in touch.button:
			if self.leftHold == True: return # To filter out undesired second click-registering:
			else:
				# Register that the left mouse button is being held.
				self.leftHold = True
				# Convert classical (x,y)-coordinates to isometric (i,j)-coordinates:
				j = int((- 0.5 * touch.pos[0] + (self.width / 4) + touch.pos[1] - self.tileHeight) // self.tileHeight)
				i = int((0.5 * touch.pos[0] - (self.width / 4) + touch.pos[1] - self.tileHeight) // self.tileHeight)

				# Check if (i, j) is within the map area:
				if i <= self.iCount - 1 and j <= self.jCount - 1 and i > - 1 and j > - 1:
					# Register the initial touch-down coordinates.
					self.initialPosition = [i, j]
					# If there is no paint selected, the tile is selected.
					if self.selectedPaint == None:
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
			j = (- 0.5 * touch.pos[0] + (self.width / 4) + touch.pos[1] - self.tileHeight) // self.tileHeight
			i = (0.5 * touch.pos[0] - (self.width / 4) + touch.pos[1] - self.tileHeight) // self.tileHeight
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
					'''
					else:
						self.selectedTiles.append(self.previewT
						# If we are removing tiles, the tiles we pass that are already part of the selected tiles list should be put in a backup, and removed.
						if [self.initialPosition[0] + diri * n, self.initialPosition[1] + dirj * m] in self.selectedTiles:
							self.previewTiles.append([self.initialPosition[0] + diri * n, self.initialPosition[1] + dirj * m])
							self.selectedTiles.remove([self.initialPosition[0] + diri * n, self.initialPosition[1] + dirj * m])
					'''
			# The selected tiles must be drawn again of course, to keep them static.
			self.highlight(self.selectedTiles)

		
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
					x = [(i - j) * self.tileWidth / 2 + self.width / 2,
						(i - j) * self.tileWidth / 2 + self.width / 2 - self.tileWidth / 2,
						(i - j) * self.tileWidth / 2 + self.width / 2 + self.tileWidth / 2]
					y = [(i + j) * self.tileHeight / 2 + self.tileHeight,
						(i + j) * self.tileHeight / 2 + self.tileHeight * 1.5,
						(i + j) * self.tileHeight / 2 + self.tileHeight * 2]
					Color(0.8, 0.8, 0, 0.75)
					Quad(points = (x[0], y[0], x[1], y[1], x[0], y[2], x[2], y[1]))
		
	def set_graphics(self, graphics, i, j, layer):
		self.mapFile.stories[self.currentStory].matrix[int(i)][int(j)].set_graphics(layer, graphics)
		self.populate_lists()
		self.render_map()
		
	def populate_lists(self):
		for s in range(self.currentStory + 1):
			for l in range(1):
				for i in range(self.iCount):
					for j in range(self.jCount):
						
						tile = self.mapFile.stories[self.currentStory].matrix[i][j]
						type = tile.get_graphics_type(l)
						if type[0] != None:
							graphicsInfo = tile.graphics[l]
							image = Image(graphicsInfo[0]).texture
							x = (i - j) * self.tileWidth / 2 + self.width / 2
							y = (i + j) * self.tileHeight / 2 + self.tileHeight
							if type[0] == 'object' and type[1] == False:
								# Object means a rectangle, not animated means it goes into renderList
								self.renderList[s][l][i][j] = Rectangle(texture = image.get_region(graphicsInfo[1][0][0][0], graphicsInfo[1][0][0][1], graphicsInfo[2][0], graphicsInfo[2][1]), size = (self.tileWidth, self.tileHeight), pos = (x - self.tileWidth/2, y) )
							'''
						elif type == ['object', True]:
							# If the object is animated, it goes into the animatedTiles list, and also gets a frame-value:
							self.animatedList[l].append( [Rectangle(texture = image.get_region(graphicsInfo[1][0][0], graphcisInfo[1][0][1], graphicsInfo[2][0], graphicsInfo[2][1]), size = (self.tileWidth, self.tileHeight), pos = (x - self.tileWidth/2, y)), 1] )
						elif type == ['autotile', False]:
							# Autotile means 4 quads, not animated means it goes into renderList:
							a = Quad(texture = image.get_region(graphicsInfo[1][0][0], graphicsInfo[1][0][1], graphicsInfo[2][0], graphicsInfo[2][1]), points = (x, y, x - self.tileWidth / 4, y + self.tileHeight / 4, x, y + self.tileHeight / 2, x + self.tileWidth / 4, y + self.tileHeight / 4 ) )
							b = Quad(texture = image.get_region(graphicsInfo[1][1][0], graphcisInfo[1][1][1], graphicsInfo[2][0], graphicsInfo[2][1]), points = (x - self.tileWidth / 4, y + self.tileWidth / 4, x - self.tileWidth / 2, y + self.tileHeight / 2, x - self.tileWidth / 4, y + self.tileHeight * 3 / 2, x, y + self.tileHeight / 4 ))
							c = Quad(texture = image.get_region(graphicsInfo[1][2][0], graphcisInfo[1][2][1], graphicsInfo[2][0], graphicsInfo[2][1]), points = (x, y + self.tileWidth / 2, x - self.tileWidth / 4, y + self.tileHeight* 3 / 2, x, y + self.tileHeight, x + self.tileWidth / 4, y + self.tileHeight * 3 / 2 ))
							d = Quad(texture = image.get_region(graphicsInfo[1][3][0], graphcisInfo[1][3][1], graphicsInfo[2][0], graphicsInfo[2][1]), points = (x + self.tileWidth / 4, y + self.tileWidth / 4, x, y + self.tileHeight / 2, x + self.tileWidth / 4, y + self.tileWidth * 3 / 2, x + self.tileWidth /2, y + self.tileWidth / 4 ))
							self.renderList[s][l][i][j] = [a, b, c, d]
						elif type == ['autotile', True]:
							a = Quad(texture = image.get_region(graphicsInfo[1][0][0], graphcisInfo[1][0][1], graphicsInfo[2][0], graphicsInfo[2][1]), points = (x, y, x - self.tileWidth / 4, y + self.tileHeight / 4, x, y + self.tileHeight / 2, x + self.tileWidth / 4, y + self.tileHeight / 4 ) )
							b = Quad(texture = image.get_region(graphicsInfo[1][1][0], graphcisInfo[1][1][1], graphicsInfo[2][0], graphicsInfo[2][1]), points = (x - self.tileWidth / 4, y + self.tileWidth / 4, x - self.tileWidth / 2, y + self.tileHeight / 2, x - self.tileWidth / 4, y + self.tileHeight * 3 / 2, x, y + self.tileHeight / 4 ))
							c = Quad(texture = image.get_region(graphicsInfo[1][2][0], graphcisInfo[1][2][1], graphicsInfo[2][0], graphicsInfo[2][1]), points = (x, y + self.tileWidth / 2, x - self.tileWidth / 4, y + self.tileHeight* 3 / 2, x, y + self.tileHeight, x + self.tileWidth / 4, y + self.tileHeight * 3 / 2 ))
							d = Quad(texture = image.get_region(graphicsInfo[1][3][0], graphcisInfo[1][3][1], graphicsInfo[2][0], graphicsInfo[2][1]), points = (x + self.tileWidth / 4, y + self.tileWidth / 4, x, y + self.tileHeight / 2, x + self.tileWidth / 4, y + self.tileWidth * 3 / 2, x + self.tileWidth /2, y + self.tileWidth / 4 ))
							self.animatedList[l].append([ [a, b, c, d], 1])
							'''
	
	def render_tile(self, i, j, layer, story):
		type = 	self.mapFile.stories[story].matrix[i][j].get_graphics_type(layer)
		if type[0] != None:
			graphicsInfo = tile.graphics[layer]
			image = Image(graphicsInfo[0]).texture
			x = (i - j) * self.tileWidth / 2 + self.width / 2
			y = (i + j) * self.tileHeight / 2 + self.tileHeight
			if type[0] == 'object' and type[1] == False:
				# Object means a rectangle, not animated means it goes into renderList
				self.renderList[story][layer][i][j] = Rectangle(texture = image.get_region(graphicsInfo[1][0][0][0], graphicsInfo[1][0][0][1], graphicsInfo[2][0], graphicsInfo[2][1]), size = (self.tileWidth, self.tileHeight), pos = (x - self.tileWidth/2, y) )
			self.canvas.before.add(Color(1, 1, 1, 1))
			self.canvas.before.add(self.renderList[story][l][i][j])
	
	def render_map(self):
		self.canvas.before.clear()
		grid = []
		for i in range(self.iCount):
				for j in range(self.jCount):
					x = [(i - j) * self.tileWidth / 2 + self.width / 2,
						(i - j) * self.tileWidth / 2 + self.width / 2 - self.tileWidth / 2,
						(i - j) * self.tileWidth / 2 + self.width / 2 + self.tileWidth / 2]
					y = [(i + j) * self.tileHeight / 2 + self.tileHeight,
						(i + j) * self.tileHeight / 2 + self.tileHeight * 1.5,
						(i + j) * self.tileHeight / 2 + self.tileHeight * 2]
					self.canvas.before.add(Color(0.8, 0.8, 0.8, 1))
					self.canvas.before.add(Quad(points = (x[0], y[0], x[1], y[1], x[0], y[2], x[2], y[1])))
					grid.append(Line(points = (x[0], y[0], x[1], y[1], x[0], y[2], x[2], y[1], x[0], y[0])))
		
		for i in range(len(grid)):
			self.canvas.before.add(Color(1, 1, 1, 1))
			self.canvas.before.add(grid[i])		
		
		for s in range(self.currentStory + 1):
			for l in range(len(self.renderList[s])):
				for k in range(len(self.animatedList[l])):
					self.canvas.before.add(self.animatedList[l][k][0])
				for i in range(len(self.renderList[s][l])):
					for j in range(len(self.renderList[s][l][i])):
						if self.renderList[s][l][len(self.renderList[s][l]) - i - 1][len(self.renderList[s][l][i]) - j - 1] != [None]:
							self.canvas.before.add(Color(1, 1, 1, 1))
							self.canvas.before.add(self.renderList[s][l][len(self.renderList[s][l]) - i - 1][len(self.renderList[s][l][i]) - j - 1])			
						
		
