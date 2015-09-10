# Graphics object:
class GraphicsObject():
	def _init_(self, **kwargs):
		# Graphics Objects are rectangles, with sprites on them to give the illusion of being quads.
		# Sprites should be given on the form: 
		# ['filename', [ [lower left corner of the region making up the sprite] ], [width, height] ]
		# If the middle argument, self.sprite[1] has more arguments than 1, it is animated.
		self.sprite = None
	
	def set_sprite(self, sprite):
		self.sprite = sprite
		
	def get_sprite(self):
		return self.sprite

# Floor tile:
class FloorObject(GraphicsObject):
	def _init_(self, **kwargs):
		super(FloorTile, self).__init__(**kwargs)
		# Floor tiles are a set of four quads, which together form a single quad. The sprites of these are made from flat texture images.
		# The sprite therefore consists of 4 lists:
		# self.sprite = [l, r, t, b]
		# l = left, r = right, t = top, b = bottom
		# Each corresponding to a list of:
		# ['filename', [ [lower left corner of the region making up the sprite] ], [width, height] ]
		# If any of self.sprite[n][1] has more than one argument, then the auto-floortile is animated.
		self.sprite = [None, None, None, None]