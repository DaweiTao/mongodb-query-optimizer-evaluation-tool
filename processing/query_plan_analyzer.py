import heapq
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors
import matplotlib.patches as mpatches
from datetime import datetime

from save_load import load_grid
from save_load import load_t_grid


def remove_outliers(grid, x, outlierConstant=2):
    """
    IQR
    :param grid:
    :param x:
    :param outlierConstant:
    :return:
    """
    a = np.array(x)
    upper_quartile = np.percentile(a, 75)
    lower_quartile = np.percentile(a, 25)
    IQR = (upper_quartile - lower_quartile) * outlierConstant
    quartileSet = (lower_quartile - IQR, upper_quartile + IQR)

    for r in range(len(grid)):
        for c in range(len(grid)):
            if grid[r][c] <= quartileSet[0] or grid[r][c] >= quartileSet[1]:
                print("Removing outlier: {}".format(grid[r][c]))
                grid[r][c] = 1


def find_practical_winner(plan_grid_path, time_grid_path, granularity):
    mongo_choice, a, b, cover, coll = load_t_grid(plan_grid_path)
    mongo_picked_winner = load_grid(time_grid_path)

    err_grid = [[-1 for c in range(granularity)] for r in range(granularity)]
    practical_winner_grid = [[-1 for c in range(granularity)] for r in range(granularity)]
    performance_factors = []

    """
        init_val    ->  0
        aIdx        ->  1
        bIdx        ->  2
        coverIdx    ->  3
        coll        ->  4

        Time grid format [winning|a|b|coverIdx|collscan]
    """

    for r in range(granularity):
        for c in range(granularity):
            # mongodb's choice
            mongo_picked_plan = mongo_picked_winner[r][c]
            mongo_picked_plan_t = mongo_choice[r][c]

            # find and record practical winner
            h = []
            heapq.heappush(h, (a[r][c], 1))
            heapq.heappush(h, (b[r][c], 2))
            heapq.heappush(h, (cover[r][c], 3))
            heapq.heappush(h, (coll[r][c], 4))
            practical_winner_t, practical_winner = heapq.heappop(h)
            practical_winner_grid[r][c] = practical_winner

            if practical_winner != mongo_picked_plan:
                performance_factor = mongo_picked_plan_t / (practical_winner_t + 0.00001)
                err_grid[r][c] = performance_factor
                performance_factors.append(performance_factor)
            else:
                err_grid[r][c] = 1

    # remove outliers in the performance factors
    remove_outliers(err_grid, performance_factors)

    return practical_winner_grid, err_grid


def calculate_error_rate(grid_a, grid_b, granularity):
    size = granularity ** 2
    err_count = 0

    for j in range(granularity):
        for i in range(granularity):
            if grid_a[j][i] != grid_b[j][i]:
                err_count += 1

    return round(err_count * 100 / size, 2)


def format_fig(granularity):
    # x, y axis
    x = [x for x in range(granularity)]
    x_b = [xi / 100 for xi in range(0,101,2)]
    plt.xticks(x, x_b, fontsize=12)
    plt.yticks(x, x_b, fontsize=12)

    every_nth = 5

    for n, label in enumerate(plt.gca().xaxis.get_ticklabels()):
        if n % every_nth != 0:
            label.set_visible(False)

    for n, label in enumerate(plt.gca().yaxis.get_ticklabels()):
        if n % every_nth != 0:
            label.set_visible(False)

    plt.xlabel("Selectivity for range predicate on field A", fontsize=15)
    plt.ylabel("Selectivity for range predicate on field B", fontsize=15)

    # legend
    orange_patch = mpatches.Patch(color='orange', label='A')
    green_patch = mpatches.Patch(color='green', label='B')
    blue_patch = mpatches.Patch(color='blue', label='Cover')
    yellow_patch = mpatches.Patch(color='yellow', label='Coll')

    plt.figure(0)
    plt.legend(handles=[orange_patch, green_patch, blue_patch, yellow_patch],
            bbox_to_anchor=(1.05, 1),
            loc='upper left',
            borderaxespad=0.,
            facecolor='lightgray',
            framealpha=1,
            prop={'size': 15})

    plt.figure(1)
    plt.legend(handles=[orange_patch, green_patch, blue_patch, yellow_patch],
            bbox_to_anchor=(1.05, 1),
            loc='upper left',
            borderaxespad=0.,
            facecolor='lightgray',
            framealpha=1,
            prop={'size': 15})


def generate_visual(mongo_choice_grid, practical_winner_grid, err_grid, granularity):
    plt.figure(num=0, figsize=(10, 10))
    plt.figure(num=1, figsize=(10, 10))
    plt.figure(num=2, figsize=(12, 10))

    cmap_common = colors.ListedColormap(['orange', 'green', 'blue', 'yellow'])
    cmap_err = 'Reds'
    date_time = datetime.now().strftime("%m-%d-%Y_%H:%M:%S")

    plt.figure(0)
    plt.pcolor(practical_winner_grid, cmap=cmap_common, edgecolors='k', linewidths=1, vmin=1, vmax=4, alpha=1)
    format_fig(granularity=50)
    fig_name = "../experiments/rest/{}_practical_winner.png".format(date_time)
    plt.figure(0).savefig(fig_name, bbox_inches='tight')

    for r in range(51):
        print(err_grid[r])

    plt.figure(1)
    plt.pcolor(mongo_choice_grid, cmap=cmap_common, edgecolors='k', linewidths=1, vmin=1, vmax=4, alpha=1)
    format_fig(granularity=50)
    fig_name = "../experiments/rest/{}_mongo_choice.png".format(date_time)
    plt.figure(1).savefig(fig_name, bbox_inches='tight')

    plt.figure(2)
    elements = []

    for j in range(len(err_grid)):
        for i in range(len(err_grid)):
            elements.append(err_grid[j][i])

    overall_improvement = round((sum(elements) / len(elements) - 1) * 100, 2)
    print("Overall improvements: {}%".format(overall_improvement))
    plt.pcolor(err_grid, cmap=cmap_err, edgecolors='k', linewidths=1, alpha=1, vmin=1, vmax=max(elements))
    cbar = plt.colorbar()
    cbar.set_label("Impact factor", fontsize=15)
    format_fig(granularity=50)
    fig_name = "../experiments/rest/{}_summary_accuracy:{:.2f}%_potential:{:.2f}%.png".format(date_time, 100 - err_rate, overall_improvement)
    plt.figure(2).savefig(fig_name, bbox_inches='tight')


if __name__ == '__main__':
    t_path = '../experiments/exp-4.4.0-withcoll-withfix-large/time_grid.txt'
    p_path = '../experiments/exp-4.4.0-withcoll-withfix-large/plan_grid.txt'

    practical_winner, err_grid = find_practical_winner(t_path, p_path, 50)
    mongo_picked_winner = load_grid(p_path)
    err_rate = calculate_error_rate(practical_winner, mongo_picked_winner, 50)
    print("Error rate: {}%".format(err_rate))
    generate_visual(mongo_picked_winner, practical_winner, err_grid)



