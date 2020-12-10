import heapq
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors
import matplotlib.patches as mpatches
from datetime import datetime
from os import listdir
from os.path import isfile, join
import argparse
import sys
sys.path.append('../experiment')
from save_load import load_t_grid
from save_load import load_grid
from config_reader import get_conf
import os


def remove_outliers(grid, x, outlierConstant=3):
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


def find_practical_winner(time_grid, plan_grid, granularity):
    mongo_choice_t, a_t, b_t, cover_t, coll_t = time_grid
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

        Time grid format [winning|a|b|coverIdx|collscan]
    """

    for r in range(granularity):
        for c in range(granularity):
            # mongodb's choice
            mongo_picked_plan = mongo_choice[r][c]
            mongo_picked_plan_t = mongo_choice_t[r][c]

            # find and record practical winner
            h = []
            heapq.heappush(h, (a_t[r][c], 1))
            heapq.heappush(h, (b_t[r][c], 2))
            heapq.heappush(h, (cover_t[r][c], 3))
            heapq.heappush(h, (coll_t[r][c], 4))
            practical_winner_t, practical_winner = heapq.heappop(h)
            practical_winner_grid[r][c] = practical_winner

            if practical_winner != mongo_picked_plan:
                performance_factor = (mongo_picked_plan_t - practical_winner_t) / (practical_winner_t + 0.00001)
                performance_grid[r][c] = performance_factor
                performance_factors.append(performance_factor)
                # if performance_factor < 0:
                #     print("performance factor: {}".format(str(performance_factor)))
            else:
                performance_grid[r][c] = 0

    # remove outliers in the performance factors
    remove_outliers(performance_grid, performance_factors)

    return practical_winner_grid, performance_grid


def calculate_accuracy(grid_a, grid_b, granularity):
    size = granularity ** 2
    correct_count = 0

    for j in range(granularity):
        for i in range(granularity):
            if grid_a[j][i] == grid_b[j][i]:
                correct_count += 1

    return round(correct_count * 100 / size, 2)


def format_fig(granularity):
    # x, y axis
    step = int(100 / granularity)
    x = [x for x in range(granularity + 1)]
    x_b = [xi / 100 for xi in range(0, 101, step)]

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


def generate_visual(mongo_choice_grid, practical_winner_grid, performance_grid, accuracy, result_dir, identifier, granularity):
    os.makedirs(os.path.dirname(result_dir), exist_ok=True)
    plt.figure(num=0, figsize=(10, 10))
    plt.figure(num=1, figsize=(10, 10))
    plt.figure(num=2, figsize=(12, 10))

    cmap_common = colors.ListedColormap(['orange', 'green', 'blue', 'yellow'])
    cmap_err = 'Reds'

    plt.figure(0)
    plt.pcolor(practical_winner_grid, cmap=cmap_common, edgecolors='k', linewidths=1, vmin=1, vmax=4, alpha=1)
    format_fig(granularity=granularity)
    fig_name = "{}_practical_winner.png".format(identifier)
    plt.figure(0).savefig(join(result_dir, fig_name), bbox_inches='tight')

    plt.figure(1)
    plt.pcolor(mongo_choice_grid, cmap=cmap_common, edgecolors='k', linewidths=1, vmin=1, vmax=4, alpha=1)
    format_fig(granularity=granularity)
    fig_name = "{}_mongo_choice.png".format(identifier)
    plt.figure(1).savefig(join(result_dir, fig_name), bbox_inches='tight')

    plt.figure(2)
    elements = []

    for j in range(len(performance_grid)):
        for i in range(len(performance_grid)):
            elements.append(performance_grid[j][i])

    overall_improvement = round((sum(elements) / len(elements)) * 100, 2)
    print("Overall improvements: {}%".format(overall_improvement))
    plt.pcolor(performance_grid, cmap=cmap_err, edgecolors='k', linewidths=1, alpha=1, vmin=min(elements), vmax=max(elements))
    cbar = plt.colorbar()
    cbar.set_label("Impact factor", fontsize=15)
    format_fig(granularity=granularity)
    fig_name = "{}_summary_accuracy:{:.2f}%_potential:{:.2f}%.png".format(identifier, accuracy, overall_improvement)
    plt.figure(2).savefig(join(result_dir, fig_name), bbox_inches='tight')
    plt.close(fig='all')


def get_avg_time_grid(time_grid_paths, granularity):
    avg_mongo_choice_t = [[0 for c in range(granularity)] for r in range(granularity)]
    avg_a_t = [[0 for c in range(granularity)] for r in range(granularity)]
    avg_b_t = [[0 for c in range(granularity)] for r in range(granularity)]
    avg_cover_t = [[0 for c in range(granularity)] for r in range(granularity)]
    avg_coll_t = [[0 for c in range(granularity)] for r in range(granularity)]
    n = len(time_grid_paths)

    for tp in time_grid_paths:
        mongo_choice_t, a_t, b_t, cover_t, coll_t = load_t_grid(tp)
        for r in range(granularity):
            for c in range(granularity):
                avg_mongo_choice_t[r][c] += mongo_choice_t[r][c] / n
                avg_a_t[r][c] += a_t[r][c] / n
                avg_b_t[r][c] += b_t[r][c] / n
                avg_coll_t[r][c] += coll_t[r][c] / n
                avg_cover_t[r][c] += cover_t[r][c] / n
    return avg_mongo_choice_t, avg_a_t, avg_b_t, avg_cover_t, avg_coll_t


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
    grid_dir = join(conf['path']['grid_dir'], collection_name)
    granularity = int(conf['visual']['granularity'])
    time_grid_fns = [fn for fn in listdir(grid_dir) if isfile(join(grid_dir, fn)) and 'time_grid' in fn]
    plan_grid_fns = [fn for fn in listdir(grid_dir) if isfile(join(grid_dir, fn)) and 'plan_grid' in fn]

    pairs = []

    for tf in time_grid_fns:
        tp_id = tf.replace('.txt', '').split('_')[-1]
        for pf in plan_grid_fns:
            if tp_id == pf.replace('.txt', '').split('_')[-1]:
                pairs.append((tf, pf))
                break

    for time_grid_fn, plan_grid_fn in pairs:
        print(tf, pf)
        identifier = time_grid_fn.replace('.txt', '').split('_')[-1]
        tp = join(grid_dir, time_grid_fn)
        pp = join(grid_dir, plan_grid_fn)
        time_grid = load_t_grid(tp)
        plan_grid = load_grid(pp)
        practical_winner_grid, performance_grid = find_practical_winner(time_grid, plan_grid, granularity)
        mongo_picked_winner_grid = load_grid(pp)
        result_dir = conf['path']['result_dir']
        accuracy = calculate_accuracy(practical_winner_grid, mongo_picked_winner_grid, granularity)
        generate_visual(mongo_picked_winner_grid, practical_winner_grid, performance_grid,
                        accuracy=accuracy,
                        result_dir=result_dir,
                        identifier=identifier,
                        granularity=granularity)
        print("Accuracy: {}%".format(accuracy))
        print("=" * 50)

    time_grid_paths = [join(grid_dir, tn) for tn in time_grid_fns]
    avg_time_grid = get_avg_time_grid(time_grid_paths, granularity)
    plan_grid_paths = [join(grid_dir, pn) for pn in plan_grid_fns]
    majority_plan_grid = get_majority_plan_grid(plan_grid_paths, granularity)
    practical_winner_grid, performance_grid = find_practical_winner(avg_time_grid, majority_plan_grid, granularity)
    mongo_picked_winner_grid = load_grid(pp)
    result_dir = conf['path']['result_dir']
    accuracy = calculate_accuracy(practical_winner_grid, mongo_picked_winner_grid, granularity)
    generate_visual(mongo_picked_winner_grid, practical_winner_grid, performance_grid,
                    accuracy=accuracy,
                    result_dir=result_dir,
                    identifier='avg',
                    granularity=granularity)
    print("Accuracy: {}%".format(accuracy))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This program visualize the experiment results')
    parser.add_argument('cname',
                        choices=['uniform', 'linear', 'normal', 'zipfian'],
                        metavar='COLLECTIONNAME',
                        help='specify collection name')
    args = parser.parse_args()
    conf = get_conf('../experiment/config.ini')
    main(args, conf)



