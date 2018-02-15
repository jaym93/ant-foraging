"""
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
"""

import sys, pygame, math, numpy, random, time, copy
from pygame.locals import *

import worldgenerator
from constants import *
from utils import *
from core import *
from gridnavigator import *
from antagent import *
from playeragent import *


def cloneNavGrid(oldNav, newNav):
    newNav.setWorld(oldNav.world)
    newNav.grid, newNav.dimensions = oldNav.grid, oldNav.dimensions


def makeAgent(atype, world, mainNav):
    if atype in [ASTARANT, GREEDYANT]:
        if atype == ASTARANT:
            nav = AntAStarGridNavigator()
        elif atype == GREEDYANT:
            nav = AntGreedyGridNavigator()
        cloneNavGrid(mainNav, nav)
        # newNav.grid, newNav.dimensions = nav.grid, nav.dimensions
        agent = GhostAgent(atype, (SCREEN[0] / 2, SCREEN[1] / 2), 0, SPEED, world)
        agent.setNavigator(nav)
    elif atype == PATHANT:
        agent = AntPathAgent(atype, (SCREEN[0] / 2, SCREEN[1] / 2), 0, SPEED, world)
    return agent


# a procedurally generated map
# mapType = 'proc1'
# initial example map
mapType = 'randomshape'

world = GameWorld(SEED, WORLD, SCREEN)
obstacles = worldgenerator.generateObstacles(mapType)
world.initializeNest()
world.initializeTerrain(obstacles, (0, 0, 0), 4, TREE)
world.initializeBaselineResources(NUMRESOURCES)

types = [ASTARANT, PATHANT, GREEDYANT]
mainNav = GridNavigator()
mainNav.setWorld(world)
mainNav.createGrids(world)

playerAnt = PlayerAgent(CONTROLLABLEANT, (SCREEN[0] / 2, SCREEN[1] / 2), 0, SPEED, world)
world.setPlayerAgent(playerAnt)

for i in range(NUMANTS):
    # agent = makeAgent(types[i % 3], world, mainNav)
    # 0 for a star, 1 for path integrator, 2 for greedy
    agent = makeAgent(types[ALGO], world, mainNav)
    world.addNPC(agent)

world.debugging = True
world.run()
