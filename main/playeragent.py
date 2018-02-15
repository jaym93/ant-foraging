import sys, pygame, math, numpy, random, time, copy
from pygame.locals import * 

from model import PathIntegratorNet
from constants import *
from utils import *
from core import *

class PlayerAgent(Agent):
	MARKER_DECAY = 100

	def __init__(self, image, position, orientation, speed, world):
		Agent.__init__(self, image, position, orientation, speed, world)
		self.world = world
		self.nestPos = (world.dimensions[0]/2., world.dimensions[1]/2.)

	def update(self, delta):
		returning = self.foodAmount > 0
		if distance(self.position, self.nestPos) < 20:
			self.foodAmount = 0
		if returning:
			antPos = coordinatesToNumpyArray(self.position, self.world.dimensions)
			self.world.markers.append((antPos, self.MARKER_DECAY))
		Agent.update(self, delta)
