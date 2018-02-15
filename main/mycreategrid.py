'''
 * Copyright (c) 2014, 2015 Entertainment Intelligence Lab, Georgia Institute of Technology.
 * Originally developed by Mark Riedl.
 * Last edited by Mark Riedl 05/2015
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
'''

import sys, pygame, math, numpy, random, time, copy
from pygame.locals import *

from constants import *
from utils import *
from core import *
from decimal import ROUND_CEILING

# Creates a grid as a 2D array of True/False values (True =  traversable). Also returns the dimensions of the grid as a (columns, rows) list.
def myCreateGrid(world, cellsize):
	grid = []
	sizex = int(math.floor(world.dimensions[0]/cellsize))
	sizey = int(math.floor(world.dimensions[1]/cellsize))
		
	dimensions = (sizex, sizey)
	### YOUR CODE GOES BELOW HERE ###
	for i in range(dimensions[0]):
		col = []
		for j in range(dimensions[1]):
			isPassable = True
			points = [(cellsize*i, cellsize*j), (cellsize*(i+1), cellsize*j), (cellsize*(i+1), cellsize*(j+1)), (cellsize*i, cellsize*(j+1))]
			for obstacle in world.getObstacles():
				if obstacle.pointInside(points[0]) or obstacle.pointInside(points[1]) or obstacle.pointInside(points[2]) or obstacle.pointInside(points[3]):
					isPassable = False
					break
				shouldBreak = False
				for line in obstacle.getLines():
					if rayTrace(points[0], points[1], line)!=None or rayTrace(points[1], points[2], line)!=None or rayTrace(points[2], points[3], line)!=None or rayTrace(points[0], points[3], line)!=None:
						isPassable = False
						shouldBreak = True
						break
				if shouldBreak:
					break
			col.append(isPassable)
		grid.append(col)
	### YOUR CODE GOES ABOVE HERE ###
	return grid, dimensions
