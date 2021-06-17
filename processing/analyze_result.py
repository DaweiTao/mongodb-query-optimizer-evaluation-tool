import sys
sys.path.append('../experiment')
from save_load import load_t_grid
from save_load import load_grid
from save_load import save_grid
from save_load import save_t_grid

from config_reader import get_conf
import os
import heapq
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors
from matplotlib.pyplot import cm
import matplotlib.patches as mpatches
from datetime import datetime
from os import listdir
from os.path import isfile, join
import argparse
import copy


def compare_performance(time_grid, plan_grid, granularity):
    a_t, b_t, cover_t, coll_t = time_grid
    mongo_choice = plan_grid

    performance_factors = []
    performance_grid = [[-1 for c in range(granularity)] for r in range(granularity)]
    practical_winner_grid = [[-1 for c in range(granularity)] for r in range(granularity)]

    """
        init_val    ->  0
        aIdx        ->  1
        bIdx        ->  2
        coverIdx    ->  3
        coll        ->  4

        Time grid format a|b|coverIdx|collscan
    """

    for r in range(granularity):
        for c in range(granularity):
            # find and record the performance of optimal plan based on the practical results
            h = []
            if a_t[r][c] is not None:
                heapq.heappush(h, (a_t[r][c], 1))
            if b_t[r][c] is not None:
                heapq.heappush(h, (b_t[r][c], 2))
            if cover_t[r][c] is not None:
                heapq.heappush(h, (cover_t[r][c], 3))
            if coll_t[r][c] is not None:
                heapq.heappush(h, (coll_t[r][c], 4))
            practical_winner_t, practical_winner = heapq.heappop(h)
            practical_winner_grid[r][c] = practical_winner

            # find and record mongodb's choice and its execution time
            mongo_picked_plan = mongo_choice[r][c]
            ts = [a_t[r][c], b_t[r][c], cover_t[r][c], coll_t[r][c]]
            chosen_plan_t = ts[mongo_picked_plan - 1]

            performance_factor = 1
            if practical_winner_t != 0:
                performance_factor = chosen_plan_t / practical_winner_t
            performance_grid[r][c] = performance_factor
            performance_factors.append(performance_factor)

    return performance_grid, performance_factors, practical_winner_grid


def calculate_accuracy(grid_a, grid_b, granularity):
    size = granularity ** 2
    correct_count = 0

    for j in range(granularity):
        for i in range(granularity):
            if grid_a[j][i] == grid_b[j][i]:
                correct_count += 1

    return round(correct_count * 100 / size, 2)


def generate_visual(mongo_choice_grid,
                    practical_winner_grid,
                    performance_grid,
                    avg_performance_impact,
                    accuracy,
                    result_dir,
                    identifier,
                    granularity,
                    idx_type):
    plt.figure(num=0, figsize=(10, 10))
    plt.figure(num=1, figsize=(10, 10))
    plt.figure(num=2, figsize=(12, 10))

    cmap_common = colors.ListedColormap(['orange', 'green', 'blue', 'yellow'])
    cmap_err = copy.copy(plt.cm.get_cmap("Reds"))
    cmap_err.set_over('black')
    cmap_err.set_under('green')

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

        # legend
        orange_patch = mpatches.Patch(color='orange', label='A')
        green_patch = mpatches.Patch(color='green', label='B')
        yellow_patch = mpatches.Patch(color='yellow', label='Coll')

        # mongo's choices
        plt.figure(0)
        if idx_type == 'cover':
            blue_patch = mpatches.Patch(color='blue', label='Cover')
            print("Covering index exists")
            plt.legend(handles=[orange_patch, green_patch, blue_patch, yellow_patch],
                       bbox_to_anchor=(1.01, 1.08),
                       facecolor='lightgray',
                       edgecolor=None,
                       prop={'size': 15},
                       ncol=4)
        elif idx_type == 'both':
            print("Index on A and B")
            plt.legend(handles=[orange_patch, green_patch, yellow_patch],
                       bbox_to_anchor=(1.01, 1.08),
                       facecolor='lightgray',
                       edgecolor=None,
                       prop={'size': 15},
                       ncol=4)
        elif idx_type == 'single':
            print("Index on B")
            plt.legend(handles=[green_patch, yellow_patch],
                       bbox_to_anchor=(1.01, 1.08),
                       facecolor='lightgray',
                       edgecolor=None,
                       prop={'size': 15},
                       ncol=4)

        # optimal plans
        plt.figure(1)
        if idx_type == 'cover':
            print("Covering index exists")
            plt.legend(handles=[orange_patch, green_patch, blue_patch, yellow_patch],
                       bbox_to_anchor=(1.01, 1.08),
                       facecolor='lightgray',
                       edgecolor=None,
                       prop={'size': 15},
                       ncol=4)
        elif idx_type == 'both':
            print("Index on A and B")
            plt.legend(handles=[orange_patch, green_patch, yellow_patch],
                       bbox_to_anchor=(1.01, 1.08),
                       facecolor='lightgray',
                       edgecolor=None,
                       prop={'size': 15},
                       ncol=4)
        elif idx_type == 'single':
            print("Index on B")
            plt.legend(handles=[green_patch, yellow_patch],
                       bbox_to_anchor=(1.01, 1.08),
                       facecolor='lightgray',
                       edgecolor=None,
                       prop={'size': 15},
                       ncol=4)

    plt.figure(0)
    plt.pcolor(practical_winner_grid, cmap=cmap_common, edgecolors='k', linewidths=1, vmin=1, vmax=4, alpha=1)
    format_fig()
    fig_name = "{}_practical_winner.png".format(identifier)
    plt.figure(0).savefig(join(result_dir, fig_name), bbox_inches='tight')

    plt.figure(1)
    plt.pcolor(mongo_choice_grid, cmap=cmap_common, edgecolors='k', linewidths=1, vmin=1, vmax=4, alpha=1)
    format_fig()
    fig_name = "{}_mongo_choice.png".format(identifier)
    plt.figure(1).savefig(join(result_dir, fig_name), bbox_inches='tight')

    plt.figure(2)
    plt.pcolor(performance_grid, cmap=cmap_err, edgecolors='k', linewidths=1, alpha=1, vmin=1)
    cbar = plt.colorbar(extend='both')
    cbar.set_label("Impact factor", fontsize=25)
    cbar.ax.tick_params(labelsize=18)
    format_fig()
    fig_name = "{}_summary_accuracy={:.2f}_impact_factor={:.5f}.png".format(identifier, accuracy, avg_performance_impact)
    plt.figure(2).savefig(join(result_dir, fig_name), bbox_inches='tight')
    plt.close(fig='all')


def get_avg_time_grid(time_grid_paths, granularity, idx_type):
    avg_mongo_choice_t = [[0 for c in range(granularity)] for r in range(granularity)]
    avg_a_t = [[0 for c in range(granularity)] for r in range(granularity)]
    avg_b_t = [[0 for c in range(granularity)] for r in range(granularity)]
    avg_cover_t = [[0 for c in range(granularity)] for r in range(granularity)]
    avg_coll_t = [[0 for c in range(granularity)] for r in range(granularity)]
    n = len(time_grid_paths)
    print("n: {}".format(n))

    for tp in time_grid_paths:
        a_t, b_t, cover_t, coll_t = load_t_grid(tp)
        for r in coll_t:
            print(r)

        for r in range(granularity):
            for c in range(granularity):
                if idx_type == 'single':
                    avg_a_t[r][c] = None
                    avg_b_t[r][c] += (b_t[r][c] / n)
                    avg_coll_t[r][c] += (coll_t[r][c] / n)
                    avg_cover_t[r][c] = None
                elif idx_type == 'both':
                    avg_a_t[r][c] += (a_t[r][c] / n)
                    avg_b_t[r][c] += (b_t[r][c] / n)
                    avg_coll_t[r][c] += (coll_t[r][c] / n)
                    avg_cover_t[r][c] = None
                elif idx_type == 'cover':
                    avg_a_t[r][c] += (a_t[r][c] / n)
                    avg_b_t[r][c] += (b_t[r][c] / n)
                    avg_coll_t[r][c] += (coll_t[r][c] / n)
                    avg_cover_t[r][c] += (cover_t[r][c] / n)
    return avg_a_t, avg_b_t, avg_cover_t, avg_coll_t


def get_majority_plan_grid(plan_grid_paths, granularity):
    majority_plan_grid = [[[] for c in range(granularity)] for r in range(granularity)]

    for pp in plan_grid_paths:
        plan_grid = load_grid(pp)
        for r in range(granularity):
            for c in range(granularity):
                majority_plan_grid[r][c].append(plan_grid[r][c])

    def find_major(val_lst):
        val_occurrence_map = {}

        for i in range(len(val_lst)):
            if val_lst[i] in val_occurrence_map.keys():
                val_occurrence_map[val_lst[i]] += 1
            else:
                val_occurrence_map[val_lst[i]] = 1

        max_count = 0
        res = -1

        for i in val_occurrence_map:
            if max_count < val_occurrence_map[i]:
                res = i
                max_count = val_occurrence_map[i]

        return res

    for r in range(granularity):
        for c in range(granularity):
            vals = majority_plan_grid[r][c]
            winner = find_major(vals)
            majority_plan_grid[r][c] = winner

    return majority_plan_grid


def main(args, conf):
    collection_name = args.cname
    idx_type = args.indextype
    result_dir = join(conf['path']['result_dir'], collection_name)
    os.makedirs(result_dir, exist_ok=True)
    grid_dir = join(conf['path']['grid_dir'], collection_name)
    granularity = int(conf['visual']['granularity'])
    time_grid_fns = [fn for fn in listdir(grid_dir) if isfile(join(grid_dir, fn)) and 'time_grid' in fn]
    plan_grid_fns = [fn for fn in listdir(grid_dir) if isfile(join(grid_dir, fn)) and 'plan_grid' in fn]

    print("Index type: {}".format(idx_type))
    print("Result dir: {}".format(result_dir))

    # pair a plan grid with its corresponding time grid
    def pair_grids():
        pairs = []

        for tf in time_grid_fns:
            tp_id = tf.replace('.txt', '').split('_')[-1]
            for pf in plan_grid_fns:
                if tp_id == pf.replace('.txt', '').split('_')[-1]:
                    pairs.append((tf, pf))
                    break

        return pairs

    paired_fns = pair_grids()

    # plot individual experiment result
    # for time_grid_fn, plan_grid_fn in paired_fns:
    #     print(time_grid_fn, plan_grid_fn)
    #     identifier = time_grid_fn.replace('.txt', '').split('_')[-1]
    #     tp = join(grid_dir, time_grid_fn)
    #     pp = join(grid_dir, plan_grid_fn)
    #     time_grid = load_t_grid(tp)
    #     plan_grid = load_grid(pp)
    #     performance_grid, performance_factors, practical_winner_grid = compare_performance(time_grid, plan_grid, granularity)
    #     mongo_picked_winner_grid = load_grid(pp)
    #     accuracy = calculate_accuracy(practical_winner_grid, plan_grid, granularity)
    #     avg_impact = sum(performance_factors) / len(performance_factors)
    #     generate_visual(mongo_picked_winner_grid, practical_winner_grid, performance_grid,
    #                     avg_performance_impact=avg_impact,
    #                     accuracy=accuracy,
    #                     result_dir=result_dir,
    #                     identifier=identifier,
    #                     granularity=granularity,
    #                     idx_type=idx_type)
    #     print("Accuracy: {}%".format(accuracy))
    #     print("Impact factor: {}".format(avg_impact))
    #     print("=" * 50)

    # summarize multiple experiment results to generate a comprehensive result
    time_grid_paths = [join(grid_dir, tn) for tn in time_grid_fns]
    avg_time_grid = get_avg_time_grid(time_grid_paths, granularity, idx_type)
    plan_grid_paths = [join(grid_dir, pn) for pn in plan_grid_fns]
    majority_plan_grid = get_majority_plan_grid(plan_grid_paths, granularity)
    comprehensive_impact_grid, avg_performance_factors, comprehensive_optimal_plan_grid = compare_performance(avg_time_grid, majority_plan_grid, granularity)
    comprehensive_accuracy = calculate_accuracy(majority_plan_grid, comprehensive_optimal_plan_grid, granularity)
    comprehensive_impact = sum(avg_performance_factors) / len(avg_performance_factors)
    generate_visual(majority_plan_grid, comprehensive_optimal_plan_grid, comprehensive_impact_grid,
                    avg_performance_impact=comprehensive_impact,
                    accuracy=comprehensive_accuracy,
                    result_dir=result_dir,
                    identifier='comprehensive',
                    granularity=granularity,
                    idx_type=idx_type)

    # save processed results
    save_t_grid(avg_time_grid, granularity, join(result_dir, "comprehensive_time_grid.txt"))
    save_grid(majority_plan_grid, join(result_dir, "comprehensive_mongo_choice_plan_grid.txt"))
    save_grid(comprehensive_optimal_plan_grid, join(result_dir, "comprehensive_optimal_plan_grid.txt"))
    save_grid(comprehensive_impact_grid, join(result_dir, "comprehensive_impact_grid.txt"))

    print("Comprehensive results:")
    print("Accuracy: {}%".format(comprehensive_accuracy))
    print("Impact factor: {}".format(comprehensive_impact))
    print("=" * 50)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This program visualize the experiment results')
    parser.add_argument('cname',
                        choices=['uniform', 'linear', 'normal', 'zipfian'],
                        metavar='COLLECTIONNAME',
                        help='specify collection name')
    parser.add_argument('indextype',
                        choices=['single', 'both', 'cover'],
                        metavar='INDEXTYPE',
                        help='specify index type')
    args = parser.parse_args()
    conf = get_conf('../experiment/config.ini')
    main(args, conf)