Ant Foraging Simulation
===
This program simulates simple ant foraging behavior, allowing ablation studies
and comparison of different agents.

Agents:
0 = A star
1 = path integrator
2 = greedy
3 = path integrator without pheromone trails

Other variables:
* number of ants
* use a human ant or not
    * If this is enabled then there will be a red ant which is controllable
      by the user via the arrow keys. By controlling this ant the user can
      guide the rest of the ants toward food they have not yet found by
      leaving pheromone trails in the appropriate locations.


Instructions for running the thing
===

Requirements:
* Use a python 2 environment (it might even require python 2.7; I haven't tried 2.6)
* Install requirements

    $ pip install -r requirements.txt

To run the simulation:

    $ cd main/
    $ python runants.py
    (enter desired variable values or press enter for defaults)
    ... simulation runs in a new window

To exit the simulation press Ctrl-C on the command line.


Important Files
===
`main/core.py`: This keeps track of objects in the simulation. In particular, `GameWorld` encompasses the main loop of the simulation in its `run` method.

`main/antagent.py`: This and the `main/model.py` file contain the code for our path integrator + pheromones agent.

`main/gridnavigator.py`: This contains the A* and greedy agents.

`matplotlib_path_integrator/model.py`: This contains an initial implementation of the path integrator agent. It also contains a failed attempt at implementing the (evolved) neural net path integrator from "Evolving a Neural Model of Insect Path Integration" by Haferlach et al.