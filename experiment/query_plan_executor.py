import os
from visualization import *
from logger import logging_decorator
from pprint import pprint


@logging_decorator
def exec_query(collection,
               collection_name,
               granularity,
               queries,
               query_file_name,
               fig_dir,
               grid_dir):
    """
    This method map query plans to different int values

    init_val    ->  0
    aIdx        ->  1
    bIdx        ->  2
    coverIdx    ->  3
    coll        ->  4

    Time grid format [winning|a|b|coverIdx|collscan]
    """

    time_grid = [[-1 for i in range(granularity)] for j in range(granularity)]
    plan_grid = [[0 for i in range(granularity)] for j in range(granularity)]
    itr_count = 0
    fig_id = 0
    timeout = 999999

    for (query, b_i, a_i) in queries:
        progress = round(float(itr_count) * 100 / len(queries), 2)
        print("Progress {}%".format(progress))

        # display result
        if progress % 2 < 0.001:
            display_grid(plan_grid,
                         os.path.join(fig_dir,
                                      collection_name,
                                      query_file_name.replace(".txt", "")),
                         granularity,
                         id="fig_{:0>5d}".format(fig_id))
            fig_id += 1

        # timeout
        # t_win, t_a, t_b, t_cover, t_tbl = timeout, timeout, timeout, timeout, timeout
        projection = {"_id": 0, "a": 1, "b": 1}

        # measure time consumption of executing each query plan
        print("Forcing collscan")
        table_scan_explain = collection.find(query, projection).hint([("$natural", 1)]).explain()
        t_tbl = table_scan_explain["executionStats"]["executionTimeMillis"]

        print("Forcing aIdx")
        t_a = timeout
        if "aIdx" in collection.index_information():
            idx_a_explain = collection.find(query, projection).hint("aIdx").explain()
            t_a = idx_a_explain["executionStats"]["executionTimeMillis"]

        print("Forcing bIdx")
        idx_b_explain = collection.find(query, projection).hint("bIdx").explain()
        t_b = idx_b_explain["executionStats"]["executionTimeMillis"]

        print("Forcing coverIdx")
        t_cover = timeout
        if "coverIdx" in collection.index_information():
            idx_cover_explain = collection.find(query, projection).hint("coverIdx").explain()
            t_cover = idx_cover_explain["executionStats"]["executionTimeMillis"]

        # run the query without hint
        print("Finding winner")
        exec_explain = collection.find(query, projection).explain()
        t_win = exec_explain["executionStats"]["executionTimeMillis"]

        # record time
        # NOTE: FORMAT [winning|a|b|coverIdx|collscan]
        t_s = [str(t_win), str(t_a), str(t_b), str(t_cover), str(t_tbl)]
        time_grid[b_i][a_i] = "|".join(t_s)

        # map color
        winning_plan = str(exec_explain['queryPlanner']['winningPlan'])

        if 'aIdx' in winning_plan:
            plan_grid[b_i][a_i] = 1
        elif 'bIdx' in winning_plan:
            plan_grid[b_i][a_i] = 2
        elif 'coverIdx' in winning_plan:
            plan_grid[b_i][a_i] = 3
        elif 'COLLSCAN' in winning_plan:
            plan_grid[b_i][a_i] = 4

        pprint(exec_explain['queryPlanner'])
        print("Time: Winning: {}, a: {}, b: {}, cover: {} ,collscan: {}".format(t_win, t_a, t_b, t_cover, t_tbl))
        print("=" * 60)

        itr_count += 1

    save_grid(plan_grid, os.path.join(grid_dir, collection_name,
                                      "plan_grid{}".format(query_file_name.replace("query", ""))))
    save_grid(time_grid, os.path.join(grid_dir, collection_name,
                                      "time_grid{}".format(query_file_name.replace("query", ""))))

    display_grid(plan_grid,
                 os.path.join(fig_dir,
                              collection_name,
                              query_file_name.replace(".txt", "")),
                 granularity,
                 id="fig_{:0>5d}".format(fig_id))
    return
