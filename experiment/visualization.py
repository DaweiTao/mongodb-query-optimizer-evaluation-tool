from matplotlib import pyplot as plt
from matplotlib import colors
import matplotlib.patches as mpatches
import uuid
import os
from datetime import datetime
from save_load import *


"""
white  ->  1  ->  A
black  ->  2  ->  B
yellow ->  3  ->  tbl
"""


def display_grid(grid, path, granularity):
    plt.figure(figsize=(10, 10))
    step = int(100 / granularity)
    x = [x for x in range(granularity + 1)]
    x_b = [xi / 100 for xi in range(0, 101, step)]
    cmap = colors.ListedColormap(['white', 'black', 'blue', 'yellow'])
    plt.pcolor(grid, cmap=cmap, edgecolors='k', linewidths=1, vmin=1, vmax=5)
    # cmap = colors.ListedColormap(['white', 'green'])
    # plt.pcolor(grid, cmap=cmap, edgecolors='k', linewidths=1, vmin=0, vmax=1)
    plt.xticks(x, x_b)
    plt.yticks(x, x_b)

    # color bar settings
    # color_bar_ticks = [x for x in range(0, 256, 15)]
    # cbar = plt.colorbar(ticks=[0, 1, 2, 3])
    # cbar.ax.set_yticklabels(['NULL','IXSCAN_A', 'IXSCAN_B', 'COLLSCAN'])

    # legend
    white_patch = mpatches.Patch(color='white', label='aIdx')
    black_patch = mpatches.Patch(color='black', label='bIdx')
    blue_patch = mpatches.Patch(color='blue', label='coverIdx')
    yellow_patch = mpatches.Patch(color='yellow', label='coll')
    plt.legend(handles=[white_patch, black_patch, blue_patch, yellow_patch],
               bbox_to_anchor=(1.05, 1),
               loc='upper left',
               borderaxespad=0.,
               facecolor='gray',
               framealpha=1)

    every_nth = 5

    for n, label in enumerate(plt.gca().xaxis.get_ticklabels()):
        if n % every_nth != 0:
            label.set_visible(False)

    for n, label in enumerate(plt.gca().yaxis.get_ticklabels()):
        if n % every_nth != 0:
            label.set_visible(False)

    fig_name = "{}.png".format(uuid.uuid4().hex)
    fig_path = os.path.join(path, fig_name)
    os.makedirs(os.path.dirname(fig_path), exist_ok=True)
    plt.savefig(fig_path, bbox_inches='tight')
    plt.close()


if __name__ == '__main__':
    grid = load_grid("../intermediate-data/grid/normalDist/visited_grid.txt")
    path = "../intermediate-data/figs"
    display_grid(grid, path, 50, "exp0")

