import os


def save_doc(path, a_list, b_list, length):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    f = open(path, "w+")
    for i in range(length):
        f.write("{},{}\n".format(a_list[i], b_list[i]))
    f.close()


def load_doc(path):
    a_s = []
    b_s = []

    try:
        with open(path, "r") as f:
            for line in f:
                tokens = line.split(",")
                a_s.append(int(tokens[0].rstrip("\n")))
                b_s.append(int(tokens[1].rstrip("\n")))
    except FileNotFoundError:
        pass

    return zip(a_s, b_s)


def save_grid(grid, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    f = open(path, "w+")

    for j in range(len(grid)):
        for i in range(len(grid)):
            f.write(str(grid[j][i]))

            if i != len(grid) - 1:
                f.write(",")

        f.write("\n")
    f.close()


def load_grid(path):
    lines = open(path, "r")
    grid = []

    for l in lines:
        tokens = l.split(",")
        temp_l = None
        try:
            temp_l = [int(x) for x in tokens]
        except:
            temp_l = [float(x) for x in tokens]

        grid.append(temp_l)
    lines.close()
    return grid


def save_query(path, a_min, a_max, b_min, b_max, b_i, a_i):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    f = open(path, "a+")
    info = [a_min, a_max, b_min, b_max, b_i, a_i]
    info = [str(x) for x in info]
    f.write(",".join(info))
    f.write("\n")
    f.close()


def load_query(path):
    lines = open(path, "r")
    queries = []

    for l in lines:
        nums = l.split(",")
        a_lower_bound = int(nums[0])
        a_upper_bound = int(nums[1])
        b_lower_bound = int(nums[2])
        b_upper_bound = int(nums[3])
        b_i = int(nums[4])
        a_i = int(nums[5])

        query = {"a": {"$gte": a_lower_bound, "$lt": a_upper_bound},
                 "b": {"$gte": b_lower_bound, "$lt": b_upper_bound}}
        queries.append((query, b_i, a_i))

    return queries


def save_t_grid(grid, granularity, path):
    a_grid, b_grid, cover_grid, coll_grid = grid
    os.makedirs(os.path.dirname(path), exist_ok=True)
    f = open(path, "a+")
    t_grid = [[None for c in range(granularity)] for r in range(granularity)]

    for r in cover_grid:
        print(r)

    for r in range(granularity):
        for c in range(granularity):
            a_t = "NULL"
            b_t = "NULL"
            cover_t = "NULL"
            coll_t = "NULL"

            if a_grid[r][c]:
                a_t = int(a_grid[r][c])

            if b_grid[r][c]:
                b_t = int(b_grid[r][c])

            if cover_grid[r][c]:
                cover_t = int(cover_grid[r][c])

            if coll_grid[r][c]:
                coll_t = int(coll_grid[r][c])

            t_lst = [str(a_t), str(b_t), str(cover_t), str(coll_t)]
            t_entry = "|".join(t_lst)
            t_grid[r][c] = t_entry

    save_grid(t_grid, path)


def load_t_grid(path):
    grid_file = open(path, "r")
    grid = []

    for row in grid_file:
        tokens = row.split(",")
        temp_l = [x for x in tokens]
        grid.append(temp_l)

    grid_file.close()

    # winning_grid = [[-1 for i in range(len(grid))] for j in range(len(grid))]
    a_grid = [[-1 for i in range(len(grid))] for j in range(len(grid))]
    b_grid = [[-1 for i in range(len(grid))] for j in range(len(grid))]
    cover_grid = [[-1 for i in range(len(grid))] for j in range(len(grid))]
    coll_grid = [[-1 for i in range(len(grid))] for j in range(len(grid))]

    for j in range(len(grid)):
        for i in range(len(grid)):
            # times = grid[j][i].split("|")
            # winning_grid[j][i] = int(times[0])
            # a_grid[j][i] = int(times[1])
            # b_grid[j][i] = int(times[2])
            # cover_grid[j][i] = int(times[3])
            # coll_grid[j][i] = int(times[4])

            a_grid[j][i], b_grid[j][i], cover_grid[j][i], coll_grid[j][i] = None, None, None, None
            ts = grid[j][i].split("|")

            if ts[0] != 'NULL':
                a_grid[j][i] = int(ts[0])

            if ts[1] != 'NULL':
                b_grid[j][i] = int(ts[1])

            if ts[2] != 'NULL':
                cover_grid[j][i] = int(ts[2])

            if ts[3] != 'NULL':
                coll_grid[j][i] = int(ts[3])

            # if ts[1] != 'NULL':
            #     a_grid[j][i] = int(ts[1])
            #
            # if ts[2] != 'NULL':
            #     b_grid[j][i] = int(ts[2])
            #
            # if ts[3] != 'NULL':
            #     cover_grid[j][i] = int(ts[3])
            #
            # if ts[4] != 'NULL':
            #     coll_grid[j][i] = int(ts[4])

    return a_grid, b_grid, cover_grid, coll_grid
