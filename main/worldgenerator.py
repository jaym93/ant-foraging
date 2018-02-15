import numpy as np
from numpy.linalg import norm
import random

from constants import *


'''
candidate parameters of interest:

size of the obstacle
number of obstacles
how "lengthy" an obstacle is
is it convex or not?
'''

def _genObstacle(rng):
    length = rng.randint(3, 10)
    offset = lambda n=300: rng.normal(n, scale=20) - n/2
    clip = lambda arr: np.clip(arr, a_min=np.array([0, 0]),
                                    a_max=np.asarray(WORLD))
    start = np.array([rng.randint(0, WORLD[0]),
                      rng.randint(0, WORLD[1])])
    obstacle = np.zeros([length, 2])
    obstacle[0] = start
    obstacle[1] = start + clip([offset(), offset()])

    def next_pt(last_i):
        # makes a convex shape (TODO: check)
        vec1 = obstacle[last_i] - obstacle[last_i-1]
        vec2 = obstacle[0] - obstacle[last_i]
        while True:
            proposal = clip([offset(), offset()])
            c1 = np.cross(proposal, vec1)
            c2 = np.cross(proposal, vec2)
            if np.sign(c1) == np.sign(c2):
                continue
            #assert np.sign(np.dot(proposal, vec1)) == np.sign(np.dot(proposal, vec2))
            if np.dot(proposal, vec1) < 0:
                continue
            return obstacle[last_i] + proposal

    for i in range(2, length):
        obstacle[i] = next_pt(i-1)
    return obstacle.tolist()
    

def procGen1(seed=8):
    rng = np.random.RandomState(seed)
    nObstacles = rng.randint(3, 8)
    obstacles = []
    for _ in range(nObstacles):
        obstacles.append(_genObstacle(rng))
    return obstacles

def sort_obstacle(obstacle):
    obstacle = list(map(np.array, obstacle))
    center = np.mean(obstacle, axis=0)
    def key(o):
        diff = o - center
        dot = np.dot([1, 0], diff)
        angle = np.arccos(dot / (np.linalg.norm([1, 0]) * np.linalg.norm(diff)))
        if dot < 0:
            angle += np.pi
        return angle
    obstacle.sort(key=key)
    angles = np.array(list(map(key, obstacle)))
    if np.min(abs(angles[1:] - angles[:-1])) < 0.2:
        return None
    result = list(map(list, obstacle))
    return result

def genPoints(run):
    width = WORLD[0]
    height = WORLD[1]
    sample = True
    while sample:
        obstacles = []
        if run==0:
            for i in range(0, random.randrange(3, 5)):
                obstacle = ((random.randint(0*width,0.5*width),random.randint(0*height,0.5*height)))
                obstacles.append(obstacle)
        if run==1:
            for i in range(0, random.randrange(3, 5)):
                obstacle = ((random.randint(0.5*width,1*width),random.randint(0*height,0.5*height)))
                obstacles.append(obstacle)
        if run==2:
            for i in range(0, random.randrange(3, 5)):
                obstacle = ((random.randint(0*width,0.5*width),random.randint(0.5*height,1*height)))
                obstacles.append(obstacle)
        if run==3:
            for i in range(0, random.randrange(3, 5)):
                obstacle = ((random.randint(0.5*width,1*width),random.randint(0.5*height,1*height)))
                obstacles.append(obstacle)
        if run==4:
            for i in range(0, random.randrange(3, 5)):
                obstacle = ((random.randint(0.25*width,0.75*width),random.randint(0.25*height,0.75*height)))
                obstacles.append(obstacle)
        obstacles = sort_obstacle(obstacles)
        if obstacles is not None:
            sample = False
    return obstacles

def generateObstacles(kind):
    if kind == 'example1':
        return [[(628, 698), (582, 717), (549, 688), (676, 548), (554, 546)],
                [(942, 484), (811, 396), (843, 299), (921, 300)],
                [(457, 422), (371, 506), (300, 515), (300, 400), (454, 350)]]
    elif kind == 'randomshape':
        return [[(82, 62), (364, 61), (200, 178), (59, 250)],
                [(192, 288), (388, 124), (376, 473), (263, 420)],
                [(472, 99), (810, 91), (624, 250)],
                [(99, 346), (392, 622), (280, 689), (156, 627), (80, 487)],
                [(466, 685), (710, 481), (587, 720), (471, 686)],
                [(969, 545), (994, 627), (675, 710)],
                [(750, 358), (909, 218), (978, 438), (940, 486)]]
    elif kind == 'randomrect':
        return [[(100, 50), (250, 50), (250, 350), (100, 350)],
                [(50, 450), (450, 450), (450, 550), (50, 550)],
                [(150, 600), (250, 600), (250, 750), (150, 750)],
                [(350, 250), (500, 250), (500, 350), (350, 350)],
                [(350, 50), (950, 50), (950, 150), (350, 150)],
                [(750, 200), (850, 200), (850, 500), (750, 500)],
                [(400, 600), (950, 600), (950, 700), (400, 700)]]
    elif kind == 'hell1':
        return [[(100, 100), (462, 100), (462, 200), (200, 200), (200, 334), (100, 334)],
                [(100, 434), (200, 434), (200, 568), (462, 568), (462, 668), (100, 668)],
                [(562, 100), (924, 100), (924, 334), (824, 334), (824, 200), (562, 200)],
                [(824, 434), (924, 434), (924, 668), (562, 668), (562, 568), (824, 568)],
                [(300, 300), (350, 300), (350, 468), (300, 468)],
                [(674, 300), (724, 300), (724, 468), (674, 468)],
                [(400, 300), (624, 300), (624, 350), (400, 350)],
                [(400, 468), (624, 468), (624, 418), (400, 418)]]
    elif kind == 'proc1':
        gens = []
        for i in range(0, 5):
            gens.append(genPoints(i))
        return gens
        # return procGen1(np.random.randint(1000))
    else:
        raise Exception('Unknown obstacle kind {}'.format(kind))
