import sys, pygame, math, numpy, random, time, copy
from pygame.locals import * 

from model import PathIntegratorNet
from constants import *
from utils import *
from core import *

class AntPathAgent(GhostAgent):
    # this close to the nest or a resource counts a touching
    NEST_DIST = 20
    RESC_DIST = 20
    # ants can see markers when at most this far away
    MARKER_DIST = 0.1
    # how many time steps to wait before removing markers (pheromones)
    MARKER_DECAY = 50
    LEAVING_MARKER_DECAY = 100

    def __init__(self, image, position, orientation, speed, world):
        super(AntPathAgent, self).__init__(image, position, orientation, speed, world)
        self.world = world
        self.nestPos = (world.dimensions[0]/2., world.dimensions[1]/2.)
        self.ant = PathIntegratorNet()
        self.nest = np.array([0.5, 0.5])
        self.antPos = np.copy(self.nest)

    def update(self, delta):
        # am I coming or going?
        relMarkers = []
        returning = self.foodAmount > 0
        if returning and distance(self.position, self.nestPos) < self.NEST_DIST:
            self.foodAmount = 0
            self.t = 0
            return None
        # find markers close to this ant (including food, which are "honorary" markers)
        # if returning:
        #	markerPositions = [m[0] for m in self.world.leaving_markers]
        #	for markerPos in markerPositions + [self.nest]:
        #		distToMarker = distance(self.antPos, markerPos)
        #		if distToMarker <= self.MARKER_DIST and np.random.rand() < 0.3:
        #			relMarkers.append(self.antPos - np.asarray(markerPos))
        if not returning:
            markerPositions = [m[0] for m in self.world.markers]
            foodPositions = []
            for sr in self.world.resources:
                foodPositions.append(coordinatesToNumpyArray(sr.position, self.world.dimensions))
            for markerPos in markerPositions + foodPositions:
                distToMarker = distance(self.antPos, markerPos)
                if distToMarker <= self.MARKER_DIST:
                    relMarkers.append(self.antPos - np.asarray(markerPos))
        # Try possible movements until we find one that works (almost Metropolis-Hastings)
        # scale prevents infinite loops in edge cases
        scale = 1.0 / 0.99
        tmpRect = self.rect.copy()
        while True:
            scale *= 0.9
            if returning:
                proposal = self.ant.proposeReturnStep(relMarkers)
            else:
                proposal = self.ant.proposeSearchStep(relMarkers)
            proposal *= scale
            target = numpyArrayToCoordinates(self.antPos + proposal, self.world.dimensions)
            tmpRect.center = numpyArrayToCoordinates(self.rect.center + proposal, self.world.dimensions)
            # would be MH if we always accepted this
            if self.world.collisionWithNonMover(target, tmpRect):
                continue
            couldMove = True
            for obstacle in self.world.getObstacles():
                if pointInsidePolygonPoints(target, obstacle.getPoints()):
                    couldMove = False
                    break
                if rayTraceWorld(self.position, target, obstacle.getLines())!= None:
                    couldMove = False
                    break
            if not couldMove:
                continue
            if target[0] < 0 or target[0] > self.world.dimensions[0] or target[1] < 0 or target[1] > self.world.dimensions[1]:
                continue
            break

        # draw green crosses to show where ants "remember" they have been
        #for loc, _ in self.ant.locations:
        #    coord = numpyArrayToCoordinates(self.nest + loc, self.world.dimensions)
        #    drawCross(self.world.background, coord, (0, 200, 0), 5)
        if USE_PHEROMONES:
            if returning:
                self.world.markers.append((self.antPos, self.MARKER_DECAY))
            else:
                self.world.leaving_markers.append((self.antPos, self.LEAVING_MARKER_DECAY))
        self.antPos = self.antPos + proposal
        self.ant.acceptHeading(proposal)
        self.turnToFace(target)
        self.move(numpyArrayToCoordinates(proposal, self.world.dimensions))
