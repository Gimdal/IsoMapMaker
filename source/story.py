# Elements from subdirectories
from tile import Tile

class Story():
	def __init__(self, i = 14, j = 14, layerCount = 6, **kwargs):
	# Stories contain a single matrix, which holds a Tile object for each tile in the map.
		self.matrix = [[ Tile(i = m, j = i, layerCount = layerCount) for n in range(j)] for m in range(i)]