How to Run The Experiment
====


Build Database
----
If no existing database, run:

    $ python3 experiment/experiment_core.py COLLECTIONNAME -b [options]

Available `COLLECTIONNAME`:
* `uniform`
* `normal`
* `linear`
* `zipfian` 

Available options:
* `uniform` - default option, which generates a dataset with unifrom distribution
* `normal` - normal distribution
* `linear` - linear distribution
* `zipfian` - zipfian distribution

This command automatically create three indexes:
* An index on field A
* An index on field B
* A cover index on both field A and B

**Note**: 

The script will persist the dataset into `dataset_path` specified in the config file.


Generate Query For the Experiment
----
If this is the first time running the experiment, run:
    
    $ python3 experiment/experiment_core.py COLLECTIONNAME -q REPITITION

`REPITITION` is the number of experiments done for each pixel generated for the visualization.
It is recommended to set `REPITITION` to any integer >= 2. 

During the process, auto generated queries will be saved
* The script will persist all queries into `query_dir`/`COLLECTIONNAME` directory.
* If `repetition` > 1, then multiple query files can be found in `query_dir`.


Force MongoDB to Execute All Query Plan Candidates
----
To execute all queries, run:

    $ python3 experiment/experiment_core.py COLLECTIONNAME -r

The script will persist results into `query_dir` specified in the config file. Results including:
* plan_grid: a n * n grid records winning plans
* time_grid: a n * n grid records time for executing different query plans

If `repetition` > 1, then multiple plan_grid and time_grid can be found in `query_dir`.

During the process, intermidate results will be saved in these three directories:
* `grid_dir`: stores two kinds of 2D array
    * plan_grid: stores winning plans
    * time_grid: records execution time of query plans 
* `fig_dir`: visualize what query plans did MongoDB pick during runtime

**Note**: Use **different** sets of directory for V0, V1 and V2. Please check [> Instructions](./prerequisites.md) 
for recommend settings.

Naming convention of query files:
* A universally unique identifier (UUID) is assigned to each query file. 
	* Format: `query_<UUID>.txt`
	* An example would be: `query_6d478179f7dd41099067c9bb7d09abd7.txt`
* The UUID is used to associate queries with corresponding results. 

Naming convention of grid files:
*  time grid: `time_grid_<UUID>.txt`, where UUID refering to the query file which is used to generate this grid  
*  plan grid: `plan_grid_<UUID>.txt`, where UUID refering to the query file which is used to generate this grid  


Generate Visualzation
---
Run:

    $ python3 processing/analyze_result.py COLLECTIONNAME INDEXTYPE
    
Available `COLLECTIONNAME`:
* `uniform`
* `normal`
* `linear`
* `zipfian`

Available `INDEXTYPE`:
* `cover` -  (on default choose this one) an index on A, an index on B and a covering index on both field
* `single` - an index on A, or an index on B
* `both` - an index on A, and an index on B

**Note**: On default use the `cover` option, otherwise it is required to...
1. Decide what index you would like to use.
2. Remove rest of indices from the database.
3. Set the `grid_dir` and `fig_dir` directory in the config file.
3. Repeat experiment to execute query & generate intermediate results.
4. Use the desired option: either `single` or `both`.

The script can read results of previous experiments and output visualizations and grids 
to `result_dir`/`COLLECTIONNAME` directory.

Naming convention of figures:
* MongoDB's choice of query plans: `comprehensive_mongo_choice.png`
* The real best query plans: `comprehensive_practical_winner.png`
* The impact figure: `comprehensive_summary_accuracy=<accuracy>_impact_factor=<factor>.png`, where
    *  `<accuracy>` is (the total number of correct choice / the total number of cases).
    *  `<factor>` is the average impact factor: sum(impact factor for each case) / total number of cases.

Naming convention of girds:
* MongoDB's choices: 
`comprehensive_mongo_choice_plan_grid.txt`
```
    init_val    ->  0
    aIdx        ->  1
    bIdx        ->  2
    coverIdx    ->  3
    coll        ->  4
```
* The real best query plan (i.e. the plan with the shortest execution time): `comprehensive_optimal_plan_grid.txt`
* The impact grid `comprehensive_impact_grid.txt`