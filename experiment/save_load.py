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
    query_info = []

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
        query_info.append((query, b_i, a_i))

    return query_info


def load_t_grid(path):
    grid_file = open(path, "r")
    grid = []

    for l in grid_file:
        tokens = l.split(",")
        temp_l = [x for x in tokens]
        grid.append(temp_l)

    grid_file.close()

    winning_grid = [[-1 for i in range(len(grid))] for j in range(len(grid))]
    a_grid = [[-1 for i in range(len(grid))] for j in range(len(grid))]
    b_grid = [[-1 for i in range(len(grid))] for j in range(len(grid))]
    cover_grid = [[-1 for i in range(len(grid))] for j in range(len(grid))]
    coll_grid = [[-1 for i in range(len(grid))] for j in range(len(grid))]

    for j in range(len(grid)):
        for i in range(len(grid)):
            times = grid[j][i].split("|")
            winning_grid[j][i] = int(times[0])
            a_grid[j][i] = int(times[1])
            b_grid[j][i] = int(times[2])
            cover_grid[j][i] = int(times[3])
            coll_grid[j][i] = int(times[4])

    return winning_grid, a_grid, b_grid, cover_grid, coll_grid
