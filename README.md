Mongodb-query-optimizer-evaluation-tool
=====

Description
----
This project aims at evaluating the effectiveness of Mongodb query optimizer. 

We define query optimizer effectiveness as the capability of the query optimizer to consistently choose the best execution plan among all alternatives. One of our initial steps has been to create a generalized query model for evaluating the effectiveness of thequery optimizer. We present an innovative approach to visualize and analyze the accuracy of the optimiser. By using this approach, we identify places where the MongoDB (v4.4.0) query optimizer chooses suboptimalquery plans. 

Through a series of experiments, we conclude that FPTP has preference bias for index scans. Weidentify the root cause of the preference bias issue and draw further conclusions about impact on the actualquery performance. Moreover, we purposed an effective solution to this particular issue.

Python Prerequisites
-----
In order to run the experiment, Python 3.7+ is required, and several Python
modules must be installed. Note that on macOS the system python is
still python2. You will need to use homebrew or macports or similar to
obtain python3.

To install the required Python modules, run:

    $ pip install -r requirements.txt
    
Where to Get MongoDB Source Code
----- 
We use three different versions of MongoDB for the experiment, including v4.4.0 release and two other modifed versions:

* V0: the original MongoDB v4.4.0 release
    * `$ wget https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-amazon2-4.4.0.tgz`
* V1: we add collection scan to query plan candidates (based on MongoDB v4.4.0 source code)
    * https://github.com/DaweiTao/mongo/releases/tag/v4.4.0-collscan-added
* V2: we adjust the productvity of all fetch operations (based on MongoDB v4.4.0 source code)
    * https://github.com/DaweiTao/mongo/releases/tag/v4.4.0-fptp-mod

To compile source code and execute binaries, please check [building-mongodb-from-source.md](https://github.com/DaweiTao/mongodb-query-optimizer-evaluation-tool/tree/main/docs/building-mongodb-from-source.md)
   

How to Run the Experiment
=======
Specify Configurations
------

Specify configurations in the the configuration file [config.ini](https://github.com/DaweiTao/mongodb-query-optimizer-evaluation-tool/blob/main/experiment/config.ini)

An example would be:
```
[db]
db_name = experiment0
dataset_size = 1000000
connection_string = <connection_string>

[visual]
granularity = 50

[path]
log_file_path = ../exp.log
dataset_dir = ../dataset
query_dir = ../intermediate-result/query
grid_dir = ../intermediate-result/grid
fig_dir = ../intermediate-result/fig
result_dir = ../processed-result/
```

Build Database
-----
If no existing database, run:

    $ python3 experiment/experiment_core COLLECTIONNAME -b [options]

Available `COLLECTIONNAME`:
* uniform 
* normal
* linear
* zipfian 

Available options:
* uniform - default option, which generates a dataset with unifrom distribution
* normal - normal distribution
* linear - linear distribution
* zipfian - zipfian distribution

This command automatically create three indexes:
* An index on field A
* An index on field B
* A cover index on both field A and B

**Note**: 

The script will persist the dataset into `dataset_path` specified in the config file.


Generate Query For the Experiment
------
If this is the first time running the experiment, run:
    
    $ python3 experiment/experiment_core COLLECTIONNAME -q REPITITION

The script will persist all queries into `query_dir` specified in the config file.
If `repetition` > 1, then multiple query files can be found in `query_dir`.


During the process, intermidate results will be saved in these three directories:
* `query_dir`: stores query files 
* `grid_dir`: stores two kinds of 2D array
    * plan_grid: stores winning plans
    * time_grid: records execution time of query plans 
* `fig_dir`: visualize what query plans did MongoDB pick during runtime


Naming convention of query files:
* A universally unique identifier (UUID) is assigned to each query file. 
	* Format: `query_<UUID>.txt`
	* An example would be: `query_6d478179f7dd41099067c9bb7d09abd7.txt`
* The UUID is used to associate queries with corresponding results. 

Naming convention of grids:
*  time grid: `time_grid_<UUID>.txt`, where UUID refering to the query file which is used to generate this grid  
*  plan grid: `plan_grid_<UUID>.txt`, where UUID refering to the query file which is used to generate this grid  



Force MongoDB to Execute All Query Plan Candidates
-------
To execute all queries, run:

    $ python3 experiment/experiment_core.py COLLECTIONNAME -r

The script will persist results into `query_dir` specified in the config file. Results including:
* plan_grid: a n * n grid records winning plans
* time_grid: a n * n grid records time for executing different query plans

If `repetition` > 1, then multiple plan_grid and time_grid can be found in `query_dir`.


During the process, 


Result Visualization:
--------
To visualize result, and see summaries of the results, run

    $ python3 processing/analyze_result.py COLLECTIONNAME INDEXTYPE
    
All results will be output to `result_dir`


Log File
-------
Execptions and experiment will be saved in `log_file_path`



