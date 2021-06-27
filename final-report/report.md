Final Report
=====

Project Scope
----
Carry out empirical work that extends the research work of my honours thesis: 
[Overleaf Link](https://www.overleaf.com/9886178511bnfhsqfvvmfv)

Tasks include coding experimental harnesses, applying additional workloads 
to installations of MongoDB on cloud-hosted services, measuring query execution
time, visualizing ties of query plan choices, analysis overhead of the FPTP approach,
storage of code data and outcomes in appropriate stores, and producing reports
and charts on the results.

Contributions
----

The results and findings of this project have the following contributions towards
 understanding the nature of the MongoDB query optimizer:

* I made a VLDB submission
    * [Overleaf Link](https://www.overleaf.com/4849921368dtjgrhckpjcy)
* In the above submission, I propose an innovative way to evaluate and visualize the impact on query performance
of an optimizer’s choices.  By using this approach, I identify places where the MongoDB 
query optimizer chooses sub-optimal query plans. My approach could form the basis of an 
automated regression testing tool to verify that the query planner in MongoDB improves
 over time. 
    * [Code for all experiments and results](https://github.com/DaweiTao/mongodb-query-optimizer-evaluation-tool)
    * [How to run the code](TODO)
* I identify causes of the preference bias of FPTP, in which index scans are systematically 
chosen even when a collection scan would run faster. I fix the problem. Different versions 
of the MongoDB source code are available for download and inspection.
    * [Get the source code](TODO)
    * [Deploy different versions of MongoDB on AWS instances](TODO)
* The query plan visualization tool can visualize ties (i.e. query plans with similar execution time)

Query Plan Evaluation Tool
====

GitHub Link
----
[Code for all experiments and results](https://github.com/DaweiTao/mongodb-query-optimizer-evaluation-tool)


Description
----
This tool aims at evaluating the effectiveness of Mongodb query optimizer. We define query optimizer 
effectiveness as the capability of the query optimizer to consistently choose the best execution plan 
among all alternatives. This tool is capable of...

* Populate a MongoDB database with customizable workload.
* Visualize MongoDB's choices of query plan and their performance.
* Visualize ties (i.e. query plans that has similar execution time)
* Visualize the overhead ofå the FPTP query optimization.

How To Run The Code
----
Please follow the steps below to run the code. Please note that some steps cannot be skipped.
It is strongly recommended to execute the code step by step according to the instructions. 
Otherwise, you may encounter errors. 

1. Deploy different versions of MongoDB on AWS instances.
[instructions](final-report/)


Building MongoDB From Source 
====
To build MongoDB, you will need:
* A modern C++ compiler capable of compiling C++17. One of the following is required:
    * GCC 8.2 or newer
    * Clang 7.0 (or Apple XCode 10.2 Clang) or newer
    * Visual Studio 2019 version 16.4 or newer (See Windows section below for details)
* On Linux and macOS, the libcurl library and header is required. MacOS includes libcurl.
    * Fedora/RHEL - `dnf install libcurl-devel`
    * Ubuntu/Debian - `libcurl-dev` is provided by three packages. Install one of them:
      * `libcurl4-openssl-dev`
      * `libcurl4-nss-dev`
      * `libcurl4-gnutls-dev`
* Python 3.7.x and Pip modules:
  * See the section "Python Prerequisites" below.
* About 13 GB of free disk space for the core binaries (`mongod`,`mongos`, and `mongo`) and about 600 GB for the install-all target.

Where to Get Source Code
----
We use three different versions of MongoDB for the experiment, including v4.4.0 release and two other modifed versions:

* V0: the original MongoDB v4.4.0 release
    * `$ wget https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-amazon2-4.4.0.tgz`
* V1: we add collection scan to query plan candidates (based on MongoDB v4.4.0 source code)
    * https://github.com/DaweiTao/mongo/releases/tag/v4.4.0-collscan-added
* V2: we adjust the productvity of all fetch operations (based on MongoDB v4.4.0 source code)
    * https://github.com/DaweiTao/mongo/releases/tag/v4.4.0-fptp-mod


Python Prerequisites
----

In order to build MongoDB, Python 3.7+ is required, and several Python
modules must be installed. Note that on macOS the system python is
still python2. You will need to use homebrew or macports or similar to
obtain python3.

To install the required Python modules, run:

    $ python3 -m pip install -r etc/pip/compile-requirements.txt

Installing the requirements inside a python3 based virtualenv
dedicated to building MongoDB is recommended.

Note: In order to compile C-based Python modules, you'll also need the
Python and OpenSSL C headers. Run:

* Fedora/RHEL - `dnf install python3-devel openssl-devel`
* Ubuntu/Debian - `apt-get install python3.7-dev libssl-dev`


Scons Prerequisites
----
To install lzma dlevel （Devel libraries & headers for liblzma) on Linux, run:

    $ yum install -y xz-devel


Install mongod
----
Upgrade g++ version:
* https://medium.com/@bipul.k.kuri/install-latest-gcc-on-centos-linux-release-7-6-a704a11d943d
* https://ftp.gnu.org/gnu/gcc/gcc-8.2.0/gcc-8.2.0.tar.gz

Install install libcurl, run:
```
$ yum install -y curl-devel
$ yum install -y openssl-devel
```
Install lzma dlevel (Devel libraries & headers for liblzma), run:

    $ yum install -y xz-devel

Build from source code, run:

    $ python3 buildscripts/scons.py -j4 --disable-warnings-as-errors install-mongod

**Note**: The following targets can be named on the scons command line to build
only certain components:

* `install-mongod`
* `install-mongos`
* `install-mongo` or `install-shell`
* `install-servers` (includes `mongod` and `mongos`)
* `install-core` (includes `mongod`, `mongos`, `mongo`)
* `install-all`

   
How to Run the Experiment
====

Python Prerequisites
----
In order to run the experiment, Python 3.7+ is required, and several Python
modules must be installed. Note that on macOS the system python is
still python2. You will need to use homebrew or macports or similar to
obtain python3.

To install the required Python modules, run:

    $ pip install -r requirements.txt
    

Specify Configurations
----
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
----
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
-----
To execute all queries, run:

    $ python3 experiment/experiment_core.py COLLECTIONNAME -r

The script will persist results into `query_dir` specified in the config file. Results including:
* plan_grid: a n * n grid records winning plans
* time_grid: a n * n grid records time for executing different query plans

If `repetition` > 1, then multiple plan_grid and time_grid can be found in `query_dir`.


During the process, 


Result Visualization:
------
To visualize result, and see summaries of the results, run

    $ python3 processing/analyze_result.py COLLECTIONNAME INDEXTYPE
    
All results will be output to `result_dir`


Log File
-----
Execptions and experiment will be saved in `log_file_path`


Install MongoDB on the linux2 server via Tarball
----
Dependencies

    $ sudo yum install libcurl openssl

Download V0: MongoDB 4.4.0

    $ wget https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-amazon2-4.0.12.tgz

Unzip

    $ tar -zxvf <filename>
    $ rm  <tarball-name>
    $ mv <mongo-name> mongodb
    
Create database

    $ mkdir -p /data/db

Modify the config file of MongoDB

    $ vim /etc/mongod.conf
    
Here is an example of config file

```
net:
    port: 27017
    bindIp: 0.0.0.0   #default value is 127.0.0.1
storage:
    dbPath: /data/db
```

