# Elements from subdirectories

class Tile():
	def __init__(self, layerCount = 6, occupant = None, enterDir = [True, True, True, True, True, True, True, True], stepCost = [0, 0, 0], terrainType = None, trigger = None, i = 0, j = 0, tileWidth = 64, tileHeight = 32, **kwargs):
		# Layers, per story
		self.layerCount = layerCount
		# Is this tile blocked by something on this story?
		self.occupant = occupant
		# When not blocked, from which directions can one enter? This is important to ensure that one cannot walk across certain ledges:
		# This bears the form of [left, top-left, top, top-right, right, bottom-right, bottom, bottom-left]
		self.enterDir = enterDir
		# If in a battle, how many steps does it cost to pass this tile?
		# This bears the form of cost for [walking, riding, flying].
		self.stepCost = stepCost
		# Which terrain does this tile count as?
		self.terrainType = terrainType
		# When a unit steps over this tile, is anything triggered?
		self.trigger = trigger
		# Isometric coordinates
		self.coords = [i, j]
		# Initially, no sprites are stored in a Tile, but as one draws on the map-canvas, sprites are added here.
		# These are later accessed to draw rectangles or quads depending on the circumstances.
		# The list has the form of [ [graphics for layer 0], [graphics for layer 1], ...] with sprite containing information on:
		# - filename: to find the .png file.
		# - [ [ [x, y] ] ] where (x, y) marks the lower-left corner in the texture from the filename from which a rectangle is to be drawn.
		#				If there is more than 1 [x,y] in the innermost brackets, it means it's animated.
		#				If there is more than 1 innermost bracket, it means it's an autotile.
		# - [sizex, sizey], indicating the size for the get_region command.
		self.graphics = [ [None] for n in range(self.layerCount) ]
	
	def set_graphics(self, layer, object):
		self.graphics[layer] = object
		print("set_graphics reports:", self.graphics[layer][1][0][0])
	
	def get_graphics_type(self, layer):
		# Determines whether the sprite on this layer is a static object, animated-object, autotile object or animated autotile object.
		# Returns on the form [base object, animated] with base object = object, autotile, and animated = True, False.
		baseobject = None,
		animated = False
		#print("from the tile file:", self.graphics[0])
		if self.graphics[layer] == [None]:
			baseobject =  None
			animated = False
			#print("None-type graphics")
		elif len(self.graphics[layer][1]) == 1 and len(self.graphics[layer][1][0]) == 1:
			#print("One sprite, one frame = static object")
			baseobject = 'object'
			animated = False
		return [baseobject, animated]
		#print(baseobject, animated)
		'''
		elif  self.graphics[layer] != [None] and len(self.graphics[layer][1]) == 1:	# and len(self.graphics[layer][1][0] == 1):
			#The first object checks the number of sprites to be drawn in one tile. If 1, it's an object.
			#The second object checks the number of frames. If 1, it's static
			baseobject, animated = 'object', False
			
		elif self.graphics[layer] != [None] and len(self.graphics[layer][1]) == 1 and len(self.graphics[layer][1][0] != 1):
			#The first object checks the number of sprites to be drawn in one tile. If 1, it's an object.
			#The second object checks the number of frames. If not 1, it's animated
			baseobject, animated = 'object', True
		elif self.graphics[layer] != [None] and len(self.graphics[layer][1]) == 4 and len(self.graphics[layer][1][0] == 1):		
			#The first object checks the number of sprites to be drawn in one tile. If 4, it's an autotile.
			#The second object checks the number of frames. If 1, it's static
			baseobject, animated = 'autotile', False
		elif self.graphics[layer] != [None] and len(self.graphics[layer][1]) == 4 and len(self.graphics[layer][1][0] != 1):	
			#The first object checks the number of sprites to be drawn in one tile. If 4, it's an autotile.
			#The second object checks the number of frames. If not 1, it's animated
			baseobject, animated = 'autotile', True
		'''
		
	def set_trigger(self, trigger):
		self.trigger = trigger
	
	def set_dir(self, dirNo, dirVal):
		if dirNo == 'All':
			self.enterDir = [dirVal for m in range(8)]
		else:
			self.enterDir[dirNo] = dirVal
	
	def set_occupant(self, occupant):
		self.occupant = occupant
		
	def get_occupant(self):
		if self.occupant != None:
			return self.occupant
	
	def get_graphics(self, layer, object):
		# This calls the sprite stored on a layer
		# This calls the get_sprite function in the GraphicsObject or FloorObject saved on that layer.
		self.graphics[layer].get_sprite