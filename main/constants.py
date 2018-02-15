"""
 * Copyright (c) 2014, 2015 Entertainment Intelligence Lab, Georgia Institute of Technology.
 * Originally developed by Mark Riedl.
 * Last edited by Matthew Guzdial 01/2016
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

import os

print("Press enter for defaults")
def prompt(txt, default=""):
    ipt = raw_input("{} (default={}): ".format(txt, default))
    if ipt == "":
        return default
    return ipt

NUMANTS = int(prompt("Enter number of ants", default=10))
ALGO = int(prompt("Agent: 0 for a star, 1 for path integrator, 2 for greedy, 3 for path integrator without pheromones", default=1))
if ALGO == 3:
    ALGO = 1
    USE_PHEROMONES = False
else:
    USE_PHEROMONES = True

SCREEN = [1024, 768]
WORLD = [1024, 768]
TICK = 60

SPEED = (5, 5)

NUMOBSTACLES = 3
OBSTACLERADIUS = 200
OBSTACLESIGMA = 50
OBSTACLEMIN = 25
OBSTACLEPOINTS = 7
OBSTACLEGRIDSIZE = 50
NUMRESOURCES = 10
SEED = 2
HITPOINTS = 25
BASEHITPOINTS = 75
TOWERHITPOINTS = 50

ASTARANT = os.path.join("sprites", "spartan1.gif")
PATHANT = os.path.join("sprites", "spartan2.gif")
GREEDYANT = os.path.join("sprites", "spartan3.gif")
CONTROLLABLEANT = os.path.join("sprites", "spartan4.gif")
SMALLBULLET = os.path.join("sprites", "bullet.gif")
RESOURCE = os.path.join("sprites", "crystal.gif")
CRYSTAL = os.path.join("sprites", "crystal.gif")
TREE = os.path.join("sprites", "tree.gif")
TOWER = os.path.join("sprites", "tower.gif")

SMALLBULLETSPEED = (20, 20)
SMALLBULLETDAMAGE = 1
BIGBULLETSPEED = (20, 20)
BIGBULLETDAMAGE = 5
FIRERATE = 10
DODGERATE = 10

INFINITY = float("inf")
EPSILON = 0.000001

