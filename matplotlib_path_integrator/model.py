import numpy as np

from pdb import set_trace

def sigmoid(x):
    return 1. / (1 + np.exp(-x))

def normalize(vec):
    return vec / np.sum(np.sqrt(vec**2))


class PathIntegratorNet(object):
    '''
    This agent remembers where it started and can return there.

    By calling random_step() you can lead it a randomly changing direction.
    By calling return_step() you can lead it back to its nest.
    '''
    def __init__(self):
        self.heading = np.zeros([2])
        # points from here to the nest
        self.nest = np.zeros([2])

    def _remember(self):
        # Call this on every step to remember where the nest is
        self.nest -= self.heading

    def random_step(self):
        '''Randomly adjust the heading.'''
        self.heading = 0.2 * normalize(self.heading + 0.2 * (np.random.rand(2) - [0.5, 0.5]))
        self._remember()
        return self.heading

    def return_step(self):
        '''Take a step to return home.'''
        # take smaller steps as you get closer to the nest
        step_size = max(0.1 * np.sqrt(np.sum(self.nest**2)), 0.001)
        # change the heading so it points a bit closer to the nest
        heading_diff = 0.4 * step_size * (normalize(self.nest) - normalize(self.heading))
        # add noise to make it a bit realistic
        heading_diff += np.random.normal(scale=0.2 * step_size, size=[2])
        self.heading += heading_diff
        self._remember()
        return self.heading



class EvoPathIntegratorNet(object):
    '''
    This contains remnents of an attempted implementation of the model
    in "Evolving a Neural Model of Insect Path Integration" by Haferlach et al.
    '''

    def __init__(self):
        # TODO: not actually used, just for debugging, remove
        # nest position relative to this agent
        self.nest = np.array([0.0, 0.0])
        self.heading = 0.1 * np.array([np.cos(2 * np.pi * np.random.rand()),
                                        np.sin(2 * np.pi * np.random.rand())])
        # sensor directions
        self.dirs = np.array([[np.cos(np.pi * 1/3.), np.sin(np.pi * 1/3.)],
                              [np.cos(np.pi * 3/3.), np.sin(np.pi * 3/3.)],
                              [np.cos(np.pi * 5/3.), np.sin(np.pi * 5/3.)]])
        self.memory = np.zeros([3, 1])

    def random_step(self):
        self.heading = 0.2 * normalize(self.heading + 0.2 * (np.random.rand(2) - [0.5, 0.5]))
        return self.move()

    def move(self):
        # return the move this
        #self.nest = self.nest - self.heading
        #self.nest = np.clip(nest, -0.5, 0.5)
        # TODO: add noise
        X = self.dirs.dot(self.heading.reshape([-1, 1]))
        #diff = -self.memory + 0.0015 * X
        #diff /= 1. #135518.
        dt = 1.
        self.memory -= dt / 1. * X #0.0015 * X # + 1. * diff
        return self.heading

    def nest_from_memory(self):
        inv = np.linalg.pinv(self.dirs)
        vec = 1. * inv.dot(self.memory).flatten()
        return vec


    def return_step(self):
        # TODO: don't duplicate
        X = self.dirs.dot(self.heading.reshape([-1, 1]))
        # c
        memory_out = sigmoid(self.memory - 1.164)

        sig_ins = np.array([
                      [X[0], memory_out[1]], # 0
                      [X[0], memory_out[2]], # 1
                      [X[1], memory_out[0]], # 2
                      [X[1], memory_out[2]], # 3
                      [X[2], memory_out[0]], # 4
                      [X[2], memory_out[1]], # 5
                  ])
        sig_acts = sigmoid(0.667 * np.array([0.71, 3.962]).dot(sig_ins.T) - 4.372).flatten()
        p = 3.974
        right = 0
        right += p * sig_acts[0]
        right -= p * sig_acts[2]
        right += p * sig_acts[3]
        right -= p * sig_acts[5]
        right += p * sig_acts[4]
        right -= p * sig_acts[1]

        left = 0
        left -= p * sig_acts[0]
        left += p * sig_acts[2]
        left -= p * sig_acts[3]
        left += p * sig_acts[5]
        left -= p * sig_acts[4]
        left += p * sig_acts[1]

        adjust = 4 * normalize(np.array([left, right]))
        adjust += np.random.normal(scale=0.1, size=[2])

        #self.heading = 0.2 * normalize(self.heading - adjust)
        self.heading = self.heading - adjust

        return self.move()
        #return self.step(self.vec - [left, right]), (left, right), self.vec


