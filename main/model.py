import numpy as np
from scipy.stats import multivariate_normal as normal

from utils import *


class PathIntegratorNet(object):
    # scale headings by this much
    SCALE = 0.03
    # how many past locations to remember
    LOC_MEMORY = 10
    '''
    This agent remembers where it started and can return there.

    By calling random_step() you can lead it a randomly changing direction.
    By calling return_step() you can lead it back to its nest.
    '''

    def __init__(self):
        self.heading = np.zeros([2])
        # points from here to the nest
        self.nest = np.zeros([2])
        self.locations = []
        self.cont = 0

    def _remember(self):
        # Call this on every step to remember where the nest is
        self.nest -= self.heading
        newLocations = []
        for loc, timeToDeath in self.locations:
            if timeToDeath <= 0:
                continue
            newLocations.append((loc, timeToDeath - 1))
        # where I am now relative to the nest
        newLocations.append((-self.nest, self.LOC_MEMORY))
        self.locations = newLocations

    def _probKeep(self, pos):
        if len(self.locations) == 0:
            return 1.
        # compute Metropolis Hastings acceptance probability for mixture model
        norm = normal(pos, cov=0.4 * np.eye(2))
        currPdf = norm.pdf(pos)
        proposalPdf = 0.
        for loc, _ in self.locations:
            proposalPdf += norm.pdf(loc)
        proposalPdf /= len(self.locations)
        acceptProb = proposalPdf / currPdf
        return acceptProb

    def proposeSearchStep(self, relMarkers=tuple()):
        '''
	Randomly adjust the heading.
	There are two stages of proposals, tracked here, says that ants
	shouldn't stay in one place for too long.
	'''
        while True:
            var = np.mean(np.var([l[0] for l in self.locations], axis=0))
            # move in the same direction for a while when position stagnates
            if self.cont > 0:
                self.cont -= 1
                newHeading = self.heading
            elif var < 1e-4:
                self.cont = 20
                newHeading = self.heading
            # move to markers if any are close by
            elif len(relMarkers) > 0 and np.random.rand() <= 0.9:
                def scoreMark(mark):
                    # TODO: could try other things here
                    dist = sum(m ** 2 for m in mark)
                    headingSim = np.dot(self.nest, normalize(mark))
                    return headingSim

                bestMarker = max(relMarkers, key=scoreMark)
                newHeading = -bestMarker
            # just randomly adjust the heading
            else:
                newHeading = self.heading
            newHeading += 0.1 * (np.random.rand(2) - [0.5, 0.5])
            newHeading = self.SCALE * normalize(newHeading)
            newPos = -(self.nest - newHeading)
            # reject sample?
            # TODO: seed should be controllable from somewhere
            if self._probKeep(newPos) >= np.random.rand():
                break
        return newHeading

    def proposeReturnStep(self, relMarkers):
        '''Take a step to return home.'''
        while True:
            # take smaller steps as you get closer to the nest
            step_size = max(0.2 * np.sqrt(np.sum(self.nest ** 2)), 0.001)
            var = np.mean(np.var([l[0] for l in self.locations], axis=0))
            # move in the same direction for a while when position stagnates
            if self.cont > 0:
                self.cont -= 1
                new_heading = self.heading
            elif var < 1e-4:
                self.cont = 20
                new_heading = self.heading
            # override with red pheromones when they're around
            #elif len(relMarkers) > 0 and np.random.rand() <= 0.9:
            #    print(len(relMarkers))
            #    def scoreMark(mark):
            #        # TODO: could try other things here
            #        dist = sum(m ** 2 for m in mark)
            #        headingSim = -np.dot(self.nest, normalize(mark))
            #        return headingSim
            #    bestMarker = max(relMarkers, key=scoreMark)
            #    new_heading = -bestMarker
            # change the heading so it points a bit closer to the nest
            else:
                # heading_diff = step_size * (normalize(self.nest) - normalize(self.heading))
                heading_diff = step_size * (normalize(self.nest) - normalize(self.heading))
                new_heading = self.SCALE * normalize(self.heading + heading_diff)
            
            # add noise to make it a bit realistic
            new_heading += np.random.normal(scale=0.2 * step_size, size=[2])
            new_pos = -(self.nest - new_heading)
            # reject sample?
            if self._probKeep(new_pos) >= np.random.rand():
                break
        return new_heading

    def acceptHeading(self, heading):
        self.heading = heading
        self._remember()
