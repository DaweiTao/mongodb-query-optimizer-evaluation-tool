from experiment.save_load import load_t_grid
from experiment.save_load import load_grid
from matplotlib import pyplot as plt
from matplotlib import colors
import matplotlib.patches as mpatches

from os import path
from os import listdir
from os.path import isfile, join

import copy
import heapq
import numpy as np


def show_ties(mongo_choice_matrix,
              mongo_choice_alpha,
              optimal_matrix,
              optimal_alpha,
              # impact_matrix,
              result_dir,
              granularity):
    plt.figure(num=0, figsize=(10, 10))
    plt.figure(num=1, figsize=(10, 10))
    plt.figure(num=2, figsize=(10, 10))

    cmap_common = colors.ListedColormap(['orange', 'green', 'blue', 'yellow'])

    def format_fig():
        # x, y axis
        step = int(100 / granularity)
        x = [x for x in range(granularity + 1)]
        x_b = [xi / 100 for xi in range(0, 101, step)]

        plt.xticks(x, x_b, fontsize=18)
        plt.yticks(x, x_b, fontsize=18)

        every_nth = 5

        for n, label in enumerate(plt.gca().xaxis.get_ticklabels()):
            if n % every_nth != 0:
                label.set_visible(False)

        for n, label in enumerate(plt.gca().yaxis.get_ticklabels()):
            if n % every_nth != 0:
                label.set_visible(False)

        plt.xlabel("Selectivity for range predicate on field A", fontsize=25)
        plt.ylabel("Selectivity for range predicate on field B", fontsize=25)

        plt.figure(0)
        orange_patch = mpatches.Patch(color='orange', label='A')
        green_patch = mpatches.Patch(color='green', label='B')
        plt.legend(handles=[orange_patch, green_patch],
                   bbox_to_anchor=(1.01, 1.08),
                   facecolor='lightgray',
                   edgecolor=None,
                   prop={'size': 15},
                   ncol=4)

        plt.figure(1)
        orange_patch = mpatches.Patch(color='orange', label='A')
        green_patch = mpatches.Patch(color='green', label='B')
        yellow_patch = mpatches.Patch(color='yellow', label='Coll')
        plt.legend(handles=[orange_patch, green_patch, yellow_patch],
                   bbox_to_anchor=(1.01, 1.08),
                   facecolor='lightgray',
                   edgecolor=None,
                   prop={'size': 15},
                   ncol=4)

    plt.figure(0)
    fig_name = "mongo_choices_show_ties.png"
    pc = plt.pcolor(mongo_choice_matrix, cmap=cmap_common, edgecolors='k', linewidths=1, vmin=1, vmax=4)
    plt.figure(0).savefig(path.join(result_dir, fig_name), bbox_inches='tight')
    for i, j in zip(pc.get_facecolors(), np.array(mongo_choice_alpha).flatten()):
        i[3] = j
    format_fig()
    plt.figure(0).savefig(path.join(result_dir, fig_name), bbox_inches='tight')

    plt.figure(1)
    fig_name = "optimal_plans_show_ties.png"
    pc = plt.pcolor(optimal_matrix, cmap=cmap_common, edgecolors='k', linewidths=1, vmin=1, vmax=4)
    plt.figure(1).savefig(path.join(result_dir, fig_name), bbox_inches='tight')
    for i, j in zip(pc.get_facecolors(), np.array(optimal_alpha).flatten()):
        i[3] = j
    format_fig()
    plt.figure(1).savefig(path.join(result_dir, fig_name), bbox_inches='tight')

    plt.close(fig='all')


def normalize(matrix, granularity):
    matrix_np = np.array(matrix)
    max = np.amax(matrix_np)
    min = np.amin(matrix_np)
    max_min_diff = max - min
    normalized_matrix = [[0 for i in range(granularity)] for j in range(granularity)]

    for r in range(granularity):
        for c in range(granularity):
            normalized_val = (matrix[r][c] - min) / max_min_diff
            normalized_matrix[r][c] = normalized_val

    return normalized_matrix


def compute_mongo_choice_alpha_matrix(winner_matrix, mongo_choice_matrix, granularity):
    alpha_matrix = [[0 for i in range(granularity)] for j in range(granularity)]
    alpha = 1 / len(mongo_choice_matrix)

    for mongo_choice_m in mongo_choice_matrix:
        for r in range(granularity):
            for c in range(granularity):
                if mongo_choice_m[r][c] == winner_matrix[r][c]:
                    alpha_matrix[r][c] += alpha

    # for r in alpha_matrix:
    #     print(r)

    return alpha_matrix


def compute_optimal_plan_alpha_matrix(time_grids, granularity):
    a_t, b_t, cover_t, coll_t = time_grids
    alpha_matrix = [[0 for c in range(granularity)] for r in range(granularity)]

    for r in range(granularity):
        for c in range(granularity):
            h = []
            if a_t[r][c]:
                heapq.heappush(h, (a_t[r][c], None))
            if b_t[r][c]:
                heapq.heappush(h, (b_t[r][c], None))
            if cover_t[r][c]:
                heapq.heappush(h, (cover_t[r][c], None))
            if coll_t[r][c]:
                heapq.heappush(h, (coll_t[r][c], None))
            first_t, _ = heapq.heappop(h)
            second_t, _ = heapq.heappop(h)
            alpha = first_t / second_t
            alpha_matrix[r][c] = alpha

    alpha_matrix = normalize(alpha_matrix, granularity)
    for r in range(granularity):
        for c in range(granularity):
            alpha_matrix[r][c] = 1 - alpha_matrix[r][c]

    return alpha_matrix


if __name__ == '__main__':
    processed_grid_path = "../results/processed-result-original/uniform/"
    intermediate_grid_path = "../results/intermediate-result-original/grid/uniform/"
    granularity = 50

    # mongo choice
    winner_grid = load_grid(path.join(processed_grid_path, "comprehensive_mongo_choice_plan_grid.txt"))
    mongo_choice_fns = [fn for fn in listdir(intermediate_grid_path) if isfile(join(intermediate_grid_path, fn)) and 'plan_grid' in fn]
    mongo_choices = [load_grid(path.join(intermediate_grid_path, fn)) for fn in mongo_choice_fns]
    mongo_choice_alpha_matrix = compute_mongo_choice_alpha_matrix(winner_grid, mongo_choices, granularity)

    # practical results
    time_grids = load_t_grid(path.join(processed_grid_path, "comprehensive_time_grid.txt"))
    optimal_plan_grid = load_grid(path.join(processed_grid_path, "comprehensive_optimal_plan_grid.txt"))
    optimal_plan_alpha_matrix = compute_optimal_plan_alpha_matrix(time_grids, granularity)

    show_ties(
        mongo_choice_matrix=winner_grid,
        mongo_choice_alpha=mongo_choice_alpha_matrix,
        optimal_matrix=optimal_plan_grid,
        optimal_alpha=optimal_plan_alpha_matrix,
        result_dir="./",
        granularity=granularity
    )