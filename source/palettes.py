# Fundamentals
from os.path import join
# Layouts
from kivy.uix.floatlayout import FloatLayout
# Graphics Elements
from kivy.core.image import Image
from kivy.graphics import Color, Rectangle
# Elements from subdirectories


class Palette(FloatLayout):
	def __init__(self, tileset = None, res = [64, 32], keyboard = None, mapCanvas = None, **kwargs):
		super(Palette, self).__init__(**kwargs)
		# Tileset is an path
		self.tileset = tileset
		# TilesetImage is the image file of the path
		self.tilesetImage = []
		self.imageRes = []
		# Palette dimensions
		self.offset = 4
		self.width = res[0] * 4 + self.offset * 2
		self.height = res[1] * 2 + self.offset * 2
		# Resolution for tiles in the palette. 
		self.res = res
		# Register which canvas is being painted on:
		self.mapCanvas = mapCanvas
		# Listen to keyboard changes:
		self.keyboard = keyboard
		# Bindings
		self.bind(on_touch_down = self.on_down)
		self.bind(on_touch_move = self.on_move)
		self.bind(on_touch_up = self.on_up)
		# Populate the palette
		self.populate_palette()
	
	def on_down(self, parent, touch):
		# Check if the touch-down position is within the palette:
		if touch.pos[0] > self.offset and touch.pos[0] < self.width - self.offset and touch.pos[1] > self.offset and touch.pos[1] < self.height - self.offset:
			#Convert the touch.pos arguments into the tile-number
			x = touch.pos[0] // (self.width / 4)
			y = touch.pos[1] // (self.width / 8)
			# Highlight the tile.
			self.highlight(x, y)
			self.mapCanvas.selectedPaint = [self.tileset, [ [ [x * self.imageRes[0], y * self.imageRes[1] ] ] ], [self.imageRes[0], self.imageRes[1]] ]
		else:
			print("not touching the palette!")
		
		
	def on_move(self, parent, touch):
		pass
		
	def on_up(self, parent, touch):
		pass
		
	def highlight(self, x, y):
		self.canvas.after.clear()
		with self.canvas.after:
			Color(0, 0.5, 1, 0.4)
			Rectangle(size = self.res, pos = (x * self.res[0] + self.offset, y * self.res[1] + self.offset))
		self.mapCanvas.selectedPaint = self.tilesetImage.get_region(x *  self.imageRes[0], y * self.imageRes[1], self.imageRes[0], self.imageRes[1] )
		with self.canvas.after:
			Color(1, 1, 1, 1)
			Rectangle(texture = self.mapCanvas.selectedPaint, size = (self.mapCanvas.tileWidth, self.mapCanvas.tileHeight), pos = (4,self.height -self.mapCanvas.tileHeight - 4 ))
		
	def populate_palette(self):
		if self.tileset != None:
			# Set image
			self.tilesetImage = Image(self.tileset).texture
			#self.backgroundImage = Image("emptytile.png").texture
			# Find the resolution of this image:
			self.imageRes = [self.tilesetImage.width / 4 , self.tilesetImage.width / 8]
			# Set new dimensions
			self.width = self.res[0] * 4 + self.offset * 2
			self.height = self.res[1] * (self.tilesetImage.height / (self.tilesetImage.width / 8)) + self.offset * 2
			# Draw the background:
			with self.canvas.before:
				Color(1, 1, 1, 1)
				Rectangle( size = self.size, pos = (self.offset, self.offset))
			# Draw the tileset in the palette
			for x in range(4):
				for y in range(int(self.tilesetImage.height / (self.tilesetImage.width / 8))):
					with self.canvas:
						Color(1, 1, 1, 1)
						#Rectangle(texture = self.backgroundImage, size = self.res, pos = (x * self.res[0] + self.offset, y * self.res[1] + self.offset ) )
						Rectangle(texture = self.tilesetImage.get_region(x * self.imageRes[0], y * self.imageRes[1], self.imageRes[0], self.imageRes[1]), size = self.res, pos = (x * self.res[0] + self.offset, y * self.res[1] + self.offset ))
		else:
			with self.canvas:
				Color(1, 1, 1, 1)
				Rectangle(size = (self.width, self.height - 8), pos = (4, 4))
				
class WallPalette(Palette):
	def __init__(self, res = [64, 96], **kwargs):
		super(WallPalette, self).__init__(**kwargs)