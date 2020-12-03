import os
from visualization import *
from logger import logging_decorator


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

    for (query, b_i, a_i) in queries:
        progress = round(float(itr_count) * 100 / len(queries), 2)
        print("Progress {}%".format(progress))

        # display result
        if itr_count % 50 == 0:
            display_grid(plan_grid,
                         os.path.join(fig_dir, query_file_name.replace(".txt", "")),
                         granularity,
                         collection_name)

        # timeout
        # t_win, t_a, t_b, t_cover, t_tbl = timeout, timeout, timeout, timeout, timeout

        # measure time consumption of executing each query plan
        print("Forcing collscan")
        table_scan_explain = collection.find(query).hint([("$natural", 1)]).explain()
        t_tbl = table_scan_explain["executionStats"]["executionTimeMillis"]

        print("Forcing aIdx")
        idx_a_explain = collection.find(query).hint("aIdx").explain()
        t_a = idx_a_explain["executionStats"]["executionTimeMillis"]

        print("Forcing bIdx")
        idx_b_explain = collection.find(query).hint("bIdx").explain()
        t_b = idx_b_explain["executionStats"]["executionTimeMillis"]

        print("Forcing coverIdx")
        idx_cover_explain = collection.find(query).hint("coverIdx").explain()
        t_cover = idx_cover_explain["executionStats"]["executionTimeMillis"]

        # measure time consumption of executing winning plan
        print("Finding winner")
        exec_explain = collection.find(query).explain()
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

        print("Winnning Plan: {}".format(winning_plan))
        print("Time: Winning: {}, a: {}, b: {}, cover: {} ,collscan: {}".format(t_win, t_a, t_b, t_cover, t_tbl))
        print("=" * 60)

        itr_count += 1

    save_grid(plan_grid, os.path.join(grid_dir, collection_name,
                                      "plan_grid{}".format(query_file_name.replace("query", ""))))
    save_grid(time_grid, os.path.join(grid_dir, collection_name,
                                      "time_grid{}".format(query_file_name.replace("query", ""))))

    display_grid(plan_grid, os.path.join(fig_dir, collection_name, query_file_name.replace(".txt", "")),
                 granularity, collection_name)
    return
