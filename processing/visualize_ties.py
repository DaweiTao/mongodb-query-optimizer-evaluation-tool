from experiment.save_load import load_t_grid
from experiment.save_load import load_grid
from matplotlib import pyplot as plt
from matplotlib import colors
import matplotlib.patches as mpatches

from os import path

import copy

import numpy as np
from numpy import dot
from numpy.linalg import norm


def cosine_similarity(v1, v2):
    a = np.array(v1)
    b = np.array(v2)
    cos_sim = dot(a, b) / (norm(a) * norm(b))
    return cos_sim


def show_ties(cos_matrix,
              normalized_matrix,
              alpha_matrix,
              plan_matrix,
              result_dir,
              granularity):

    plt.figure(num=0, figsize=(10, 10))
    plt.figure(num=1, figsize=(10, 10))
    plt.figure(num=2, figsize=(10, 10))
    plt.figure(num=3, figsize=(10, 10))

    cmap_cos = copy.copy(plt.cm.get_cmap("Accent"))
    cmap_cos.set_over('black')
    cmap_cos.set_under('green')
    cmap_normalized = copy.copy(plt.cm.get_cmap("Accent"))
    cmap_normalized.set_over('black')
    cmap_normalized.set_under('yellow')
    cmap_alpha = copy.copy(plt.cm.get_cmap("Accent"))
    cmap_alpha.set_over('black')
    cmap_alpha.set_under('Green')
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

        plt.figure(3)
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
    plt.pcolor(cos_matrix, cmap=cmap_cos, edgecolors='k', linewidths=1, alpha=1)
    cbar = plt.colorbar(extend='both')
    cbar.set_label("Cosine Similarity", fontsize=25)
    cbar.ax.tick_params(labelsize=18)
    format_fig()
    fig_name = "cos_sim.png"
    plt.figure(0).savefig(path.join(result_dir, fig_name), bbox_inches='tight')

    plt.figure(1)
    plt.pcolor(normalized_matrix, cmap=cmap_normalized, edgecolors='k', linewidths=1, alpha=1, vmin=0, vmax=1)
    cbar = plt.colorbar(extend='both')
    cbar.set_label("Ties (Min-Max-Normed Cos Similarity)", fontsize=25)
    cbar.ax.tick_params(labelsize=18)
    format_fig()
    fig_name = "normalized_sim.png"
    plt.figure(1).savefig(path.join(result_dir, fig_name), bbox_inches='tight')

    plt.figure(2)
    plt.pcolor(alpha_matrix, cmap=cmap_alpha, edgecolors='k', linewidths=1, alpha=1, vmin=0, vmax=1)
    cbar = plt.colorbar(extend='both')
    cbar.set_label("Alpha Value (0->Transparent, 255->Opaque)", fontsize=25)
    cbar.ax.tick_params(labelsize=18)
    format_fig()
    fig_name = "alpha_val.png"
    plt.figure(2).savefig(path.join(result_dir, fig_name), bbox_inches='tight')

    plt.figure(3)
    pc = plt.pcolor(plan_matrix, cmap=cmap_common, edgecolors='k', linewidths=1, vmin=1, vmax=4)
    format_fig()
    plt.savefig(path.join(result_dir, fig_name), bbox_inches='tight')

    for i, j in zip(pc.get_facecolors(), np.array(alpha_matrix).flatten()):
        i[3] = j

    format_fig()
    fig_name = "ties_visualization.png"
    plt.savefig(path.join(result_dir, fig_name), bbox_inches='tight')
    plt.close(fig='all')


def calculate_cosine_similarity_matrix(time_grids, granularity):
    a_time_grid, b_time_grid, cover_time_grid, coll_time_grid = time_grids

    similarity_matrix = [[0 for i in range(granularity)] for j in range(granularity)]

    for r in range(granularity):
        for c in range(granularity):
            a_t = a_time_grid[r][c]
            b_t = b_time_grid[r][c]
            # cover_t = cover_time_grid[r][c]
            coll_t = coll_time_grid[r][c]
            v1 = [a_t, b_t, coll_t]
            v2 = [1, 1, 1]
            cos_sim = cosine_similarity(v1, v2)
            similarity_matrix[r][c] = cos_sim

    return similarity_matrix


def normalize(matrix, granularity):
    matrix_np = np.array(matrix)
    max = np.amax(matrix_np)
    min = np.amin(matrix_np)
    max_min_diff = max - min
    normalized_matrix = [[0 for i in range(granularity)] for j in range(granularity)]

    for r in range(granularity):
        for c in range(granularity):
            normalized_val = (matrix[r][c] - min) / max_min_diff
            normalized_matrix[r][c] = normalized_val**2

    return normalized_matrix


grid_path = "../results/processed-result-original/uniform/"
time_grids = load_t_grid(path.join(grid_path, "comprehensive_time_grid.txt"))
optimal_plan_grid = load_grid(path.join(grid_path, "comprehensive_optimal_plan_grid.txt"))
granularity = 50
cos_m = calculate_cosine_similarity_matrix(time_grids, granularity=50)
normalized_m = normalize(matrix=cos_m, granularity=50)
alpha_m = [[None for c in range(granularity)] for r in range(granularity)]

for r in range(granularity):
    for c in range(granularity):
        alpha_m[r][c] = 1 - normalized_m[r][c]

show_ties(cos_matrix=cos_m,
          normalized_matrix=normalized_m,
          alpha_matrix=alpha_m,
          plan_matrix=optimal_plan_grid,
          result_dir="./",
          granularity=granularity)