import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from model import normalize, PathIntegratorNet

from pdb import set_trace

# Simulation params
# how many time steps to run the simulation in total
T = 100
# wander randomly till this time step
wander_T = 50
nest = np.array([0.5, 0.5])
# start the ant at the nest
ant_pos = np.copy(nest)
seed = 16
np.random.seed(seed)

# Visualization params
fig = plt.figure()
ax = plt.gca()
# millisecs between simulation time steps
interval = 50
# initial limits, to be adjusted as the sim progresses
xmin, xmax = 0, 1
ymin, ymax = 0, 1
# the sim proceeds by adjusting the data of these elements
# dot at ant location (red)
ant_dot, = plt.plot([], [], 'ro')
# dot at nest location (green)
nest_dot, = plt.plot([], [], 'go')
# line indicating wander path (red)
wander_line, = plt.plot([], [], 'r-')
# line indicating return path (blue)
return_line, = plt.plot([], [], 'b-')
# line indicating ant's belief about nest location (green)
nest_line, = plt.plot([], [], 'g-')


def update(t, nest_dot, nest_line, ant_dot, wander_line, return_line):
    '''
    Run one time step of the sim, restarting as necessary.
    '''
    # reset if needed
    # This isn't quite complex enough to use an object.
    global ant_positions, ant, ant_pos
    global xmin, xmax, ymin, ymax
    if t == 0:
        ant = PathIntegratorNet()
        ant_positions = [nest]
        ant_pos = np.copy(nest)
        wander_line.set_data(np.array([[], []]))
        return_line.set_data(np.array([[], []]))
        xmin, xmax = 0, 1
        ymin, ymax = 0, 1

    # update ant state
    returning = not (t < wander_T)
    if returning:
        dist_to_nest = np.sqrt(np.sum((ant_pos - nest)**2))
        if dist_to_nest < 0.1 or t >= T:
            return nest_dot, nest_line, ant_dot, wander_line, return_line
        move = ant.return_step()
    else:
        move = ant.random_step()
    ant_nest_belief = np.array([nest, nest - ant.nest])
    ant_pos = ant_pos + move
    ant_positions.append(ant_pos)

    # plot new state of the world
    nest_dot.set_data(nest)
    # comment this statement to turn of the green line
    nest_line.set_data(ant_nest_belief.T)
    ant_dot.set_data(ant_pos)
    wander_line.set_data(np.array(ant_positions[:wander_T]).T)
    if len(ant_positions) > wander_T:
        return_line.set_data(np.array(ant_positions[wander_T-1:]).T)
    # allow the ant to wander outside the initial plot limits
    xmin = min(ant_pos[0], xmin)
    xmax = max(ant_pos[0], xmax)
    ymin = min(ant_pos[1], ymin)
    ymax = max(ant_pos[1], ymax)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_xticks([])
    ax.set_yticks([])
    fig.canvas.draw()

    return nest_dot, nest_line, ant_dot, wander_line, return_line


def main():
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_title('Ant Wandering Randomly then Returning Home')
    line_ani = animation.FuncAnimation(fig, update, T, fargs=(nest_dot, nest_line, ant_dot, wander_line, return_line),
                                       interval=interval, blit=True)
    line_ani.save('pathint_{}.gif'.format(seed), dpi=80, writer='imagemagick')
    #line_ani.save('pathint_{}_nogreen.gif'.format(seed), dpi=80, writer='imagemagick')
    #plt.show()


if __name__ == '__main__':
    main()

