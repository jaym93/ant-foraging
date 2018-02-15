'''
 * Copyright (c) 2014, 2015 Entertainment Intelligence Lab, Georgia Institute of Technology.
 * Originally developed by Mark Riedl.
 * Last edited by Mark Riedl 05/2015
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
'''

import sys, pygame, math, numpy, random, time, copy
from pygame.locals import * 

from model import PathIntegratorNet
from constants import *
from utils import *
from core import *
from mycreategrid import *

###################
### GridNavigator
###
### Abstract base class for navigating the world on a grid.

class GridNavigator(Navigator):


	### grid: the grid, a 2D array where each element is True or False indicating navigability of that region of the corresponding region of space.
	### dimensions: the number of columns and rows in the grid: (columns, rows)
	### cellSize: the physical size of each corresponding cell in the map. Automatically set to the agent's radius x 2.

	def __init__(self):
		Navigator.__init__(self)
		self.grid = None
		self.dimensions = (0, 0)
		self.cellSize = 0
		self.cellSize = 15.0
		self.shouldRecompute = False

	def setAgent(self, agent):
		Navigator.setAgent(self, agent) #math.ceil(agent.getRadius())*2.0

    ### Set the world object
    ### self: the navigator object
    ### world: the world object
	def setWorld(self, world):
		# Store the world object
		self.world = world
		self.nestPos = (world.dimensions[0]/2, world.dimensions[1]/2)

	def createGrids(self, world):
		self.createGrid(world)
		# Draw the world
		self.drawGrid(self.world.debug)
		drawCross(self.world.debug, translateCellToCoordinates(findClosestCell(self.nestPos, self.grid, self.cellSize), self.cellSize), (255,0,0), 3)
		for r in self.world.resources:
			g = findClosestCell(r.position, self.grid, self.cellSize)
			if not self.grid[g[0]][g[1]]:
				self.world.deleteResource(r)

    ### Create the grid
    ### self: the navigator object
    ### world: the world object
	def createGrid(self, world):
		self.grid, self.dimensions = myCreateGrid(world, self.cellSize)
		return None


	def drawGrid(self, surface):
		# if self.grid is not None:
		# 	for y in range(self.dimensions[1]):
		# 		for x in range(self.dimensions[0]):
		# 			if self.grid[x][y]:
		# 				x1 = x * self.cellSize
		# 				y1 = y * self.cellSize
		# 				x2 = (x+1) * self.cellSize
		# 				y2 = (y+1) * self.cellSize
		# 				pygame.draw.line(surface, (0, 255, 0), (x1, y1), (x2, y1), 1)
		# 				pygame.draw.line(surface, (0, 255, 0), (x2, y1), (x2, y2), 1)
		# 				pygame.draw.line(surface, (0, 255, 0), (x2, y2), (x1, y2), 1)
		# 				pygame.draw.line(surface, (0, 255, 0), (x1, y2), (x1, y1), 1)
		return None

################
### RandomGridNavigator
###
### The RandomGridNavigator dynamically creates a grid for the world with 4-connectivity.
### But when asked to move the agent, it computes a random path through the network and probably fails to reach its destination.
class AntAStarGridNavigator(GridNavigator):
	def __init__(self):
		GridNavigator.__init__(self)

	### Finds the shortest path from the source to the destination. It should minimally set the path.
	### self: the navigator object
	### source: the place the agent is starting from (i.e., it's current location)
	### dest: the place the agent is told to go to
	def computePath(self, source, dest):
		if self.agent != None and self.world != None and self.grid != None:
			self.source = source
			self.destination = dest

			start = findClosestCell(source, self.grid, self.cellSize)
			end = findClosestCell(dest, self.grid, self.cellSize)
			if end[0] < 0 or end [0] >= self.dimensions[0] or end[1] < 0 or end[1] >= self.dimensions[1] or not self.grid[end[0]][end[1]]:
				for r in self.world.resources:
					if r.position == self.destination:
						self.world.deleteResource(r)
						return
			current = start
			path = [] # Path holds the grid cells, needs to be translated back to real world coordinates
			open = {}
			open[start] = [0, distance(start, end)]
			close = []
			parent = {}
			while current != end:
				close.append(current)
				successors = getCellSuccessors(current, self.grid, self.dimensions)
				for i in range(len(successors)):
					s = successors[i]
					if s in close:
						continue
					d0 = open[current][0]
					if i > 3:
						d0 += 1.4
					else:
						d0 += 1
					d1 = distance(s, end)
					if not (s in open) or d0 < open[s][0]:
						open[s] = [d0, d1]
						parent[s] = current
				best = None
				dist = 100000000
				#print open, current
				if current in open:
					del open[current]
				for key in open:
					if open[key][0] + open[key][1] < dist:
						dist = open[key][0] + open[key][1]
						best = key
				current = best
			if current == end:
				while current != start:
					path.insert(0, current)
					current = parent[current]
				path.insert(0, current)
			else:
				return None

			self.setPath(translatePathToCoordinates(path, self.cellSize))
			self.source = source
			self.destination = translateCellToCoordinates(end, self.cellSize) #stop at the closest cell to the destination
			if len(path) > 0:
				first = self.path.pop(0)
				if first is not None:
					self.agent.moveToTarget(first)

	def updateDestination(self):
		# print("update des")
		if self.agent.foodAmount > 0:
			self.computePath(self.agent.position, self.nestPos)
			return None
		resources = []
		for r in self.world.resources:
			resources.append(r.position)
		if len(resources) == 0:
			return None
		next = random.randint(0, len(resources)-1)
		self.computePath(self.agent.position, resources[next])

################
### GreedyGridNavigator
###
### The GreedyGridNavigator dynamically creates a grid with 4-connectivity
### But when asked to move the agent, it computes a path through the network always moving closer to the destination and probably fails to reach its destination.
	def update(self, delta):
		if distance(self.agent.position, self.nestPos) < 20:
			self.agent.foodAmount = 0
		elif self.destination != None and distance(self.destination, self.nestPos) > 10 and self.agent.foodAmount > 0:
			self.computePath(self.agent.position, self.nestPos)


class AntGreedyGridNavigator(GridNavigator):

	def __init__(self):
		GridNavigator.__init__(self)

	def computePath(self, source, dest):
		self.shouldRecompute = False
		if self.agent != None and self.world != None and self.grid != None:
			self.source = source
			self.destination = dest
			self.agent.moveToTarget(dest)
			start = findClosestCell(source, self.grid, self.cellSize)
			end = findClosestCell(dest, self.grid, self.cellSize)
			if end[0] < 0 or end [0] >= self.dimensions[0] or end[1] < 0 or end[1] >= self.dimensions[1] or not self.grid[end[0]][end[1]]:
				for r in self.world.resources:
					if r.position == self.destination:
						self.world.deleteResource(r)
						return
			current = start
			path = [current] # Path holds the grid cells, needs to be translated back to real world coordinates
			count = 0
			last = current
			while current != end and count < 30:
				count = count + 1
				successors = getCellSuccessors(current, self.grid, self.dimensions, last)
				last = current
				best = None
				dist = 0
				for s in successors:
					d = distance(s, end)
					if best == None or d < dist:
						best = s
						dist = d
				current = best
				path.append(current)
			if count == 30:
				self.shouldRecompute = True
			self.setPath(translatePathToCoordinates(path, self.cellSize))
			self.source = source
			self.destination = translateCellToCoordinates(end, self.cellSize) #stop at the closest cell to the destination
			if len(path) > 0:
				first = self.path.pop(0)
				if first is not None:
					self.agent.moveToTarget(first)

	def updateDestination(self):
		if self.agent.foodAmount > 0:
			self.computePath(self.agent.position, self.nestPos)
			return None
		resources = []
		for r in self.world.resources:
			resources.append(r.position)
		if len(resources)== 0:
			if distance(self.agent.position, self.nestPos) > 20:
				self.computePath(self.agent.position, self.nestPos)
			return None
		next = random.randint(0, len(resources)-1)
		self.computePath(self.agent.position, resources[next])

	def update(self, delta):
		if distance(self.agent.position, self.nestPos) < 20:
			self.agent.foodAmount = 0
		elif self.destination != None and distance(self.destination, self.nestPos) > 10 and self.agent.foodAmount > 0:
			self.computePath(self.agent.position, self.nestPos)


###############
### HELPERS
def insideObstacles(nav, array):
	grid = findClosestCell(numpyArrayToCoordinates(array, nav.world.dimensions), nav.grid, nav.cellSize)
	#print grid, nav.grid[grid[0]][grid[1]]
	if not nav.grid[grid[0]][grid[1]]:
		return True
	# point = translateCellToCoordinates(grid, nav.cellSize)
	# for obstacle in nav.world.getObstacles():
	# 	if obstacle.pointInside(point):
	# 		return True
	return False

def insideBorder(array):
	return array[0] > 0 and array[0] < 1 and array[1] > 0 and array[1] < 1

def translateCoordinatesToCell(point, grid, cellsize):
    # I could do this mathematically, but I am lazy.
    best = None
    dist = 0.0
    for x in range(len(grid)):
        for y in range(len(grid[x])):
            centery = (y * cellsize) + (cellsize/2.0)
            centerx = (x * cellsize) + (cellsize/2.0)
            d = distance(point, (centerx, centery))
            if best is None or d < dist:
                best = (x, y)
                dist = d
    return best

def translateCellToCoordinates(cell, cellsize):
	return ( (cell[0]*cellsize) + (cellsize/2.0), (cell[1]*cellsize) + (cellsize/2.0) )

def findClosestCell(point, grid, cellsize):
	return translateCoordinatesToCell(point, grid, cellsize)

def getCellSuccessors(cell, grid, dimensions, last = None):
	if cell == None:
		print(cell,"None")
	successors = []
	if cell[0] > 0 and grid[cell[0]-1][cell[1]]:
		successors.append( (cell[0]-1, cell[1]) )
	if cell[0] < dimensions[0]-1 and grid[cell[0]+1][cell[1]]:
		successors.append( (cell[0]+1, cell[1]) )
	if cell[1] > 0 and grid[cell[0]][cell[1]-1]:
		successors.append( (cell[0], cell[1]-1) )
	if cell[1] < dimensions[1]-1 and grid[cell[0]][cell[1]+1]:
		successors.append( (cell[0], cell[1]+1) )
	if cell[0] > 0 and cell[1] > 0 and grid[cell[0]-1][cell[1]-1]:
		successors.append( (cell[0]-1, cell[1]-1))
	if cell[0] > 0 and cell[1] < dimensions[1]-1 and grid[cell[0]-1][cell[1]+1]:
		successors.append( (cell[0]-1, cell[1]+1))
	if cell[0] < dimensions[0]-1 and cell[1] > 0 and grid[cell[0]+1][cell[1]-1]:
		successors.append( (cell[0]+1, cell[1]-1))
	if cell[0] < dimensions[0]-1 and cell[1] < dimensions[1]-1 and grid[cell[0]+1][cell[1]+1]:
		successors.append( (cell[0]+1, cell[1]+1))
	if len(successors) > 1 and last is not None and last in successors:
		successors.remove(last)
	return successors

def translatePathToCoordinates(path, cellsize):
	newpath = []
	for cell in path:
		newpath.append(translateCellToCoordinates(cell, cellsize))
	return newpath

def clearShot(start, end, world):
	if rayTraceWorld(start, end, world.getLines()) != None:
		return False
	return True
