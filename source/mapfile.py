# Elements from subdirectories
from tile import Tile
from story import Story
from graphicsobject import GraphicsObject, FloorObject

class MapFile():
	def __init__(self, name = "New Map", ID = 0000, i = 14, j = 14, stories = 1, layerCount = 6, **kwargs):
		self.stories = [ Story(i = i, j = j, layerCount = layerCount) for m in range(stories) ]
		self.storyCount = stories
		self.layerCount = layerCount
		self.name = name
		self.ID = ID