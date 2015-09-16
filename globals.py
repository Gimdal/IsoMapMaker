import os, sys, inspect
from os.path import dirname, isfile, join, split
# List subdirectories
subDirectory = {}
subDirectory['graphics'] = (os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0], "graphics"))))
subDirectory['autotiles'] = (os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0], join("graphics","autotiles")))))
subDirectory['walls'] = (os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0], join("graphics","walls")))))
subDirectory['source'] = (os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0], "source"))))
subDirectory['maps'] =(os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0], "maps"))))

# Add subdirectories to path
for i in subDirectory.values():
	if i not in sys.path:
		sys.path.insert(0, i)
		print("Added: ", i)