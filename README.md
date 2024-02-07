Experimental evaluation of MongoDB's FPTP query planner
====

This code evaluates the effectiveness of MongoDB's query optimizer. We define query optimizer 
effectiveness as the capability of the query optimizer to consistently choose the best execution
plan among all alternatives. This tool is capable of:

* Populating a MongoDB database with customizable workload.
* Visualizing MongoDB's choices of query plan and their performance.
* Visualizing ties (i.e. query plans that has similar execution time)
* Visualizing the overhead of the FPTP query optimization.

Project Scope
----
This repository contains all code required to reproduce the results in our paper
"First Past the Post: Evaluating Query Optimization in MongoDB". That includes server configuration,
scripts to build multiple versions of MongoDB from source, experimental harnesses, applying
additional workloads to installations of MongoDB on cloud-hosted services, measuring query execution
time, visualizing ties of query plan choices, analysis overhead of the FPTP approach, storage of
code data and outcomes in appropriate stores, and producing reports and charts on the results.

[Code for all experiments and results](https://github.com/michaelcahill/mongodb-fptp-paper)

Instructions
---
1. Provision an AWS instance: m6id.large (or larger) recommended
Attach at least 200GB storage
Use the Amazon Linux 2023 AMI
Make sure you have ssh access (keypair and ssh is permitted inbound from your client)
2. Log in and run:
```sh
$ wget -c 'https://github.com/michaelcahill/mongodb-fptp-paper/archive/refs/heads/main.zip'
$ unzip main.zip && rm main.zip

$ sudo bash ./mongodb-fptp-paper-main/prep.sh
$ ./mongodb-fptp-paper-main/build-all.sh
$ ./mongodb-fptp-paper-main/run-all.sh
```
3. Data and charts will be generated in the `results-cover`, `results-both` and `results-single`
directories, corresponding to different index choices.

Running the code manually
----

We also provide information about how to run the code without the scripts described above.  Here are
links for manual steps run the experiments. Please note that some steps cannot be skipped.  It is
**strongly recommended** to execute the code step by step according to the instructions. 
Otherwise, you may encounter errors. 

1. Build MongoDB from source
[> Instructions](./docs/building-monogdb-from-source.md)
2. Deploy different versions of MongoDB on AWS instances. (Includes links to modified MongoDB source code)\
[> Instructions](./docs/deploy-mongodb-on-aws.md)
3. Prerequisites and suggested settings.\
[> Instructions](./docs/prerequisites.md)
4. Run the experiments that visualize query plans and their performance.\
[> Instructions](./docs/run-experiment.md)
5. Visualize ties (i.e. query plans that has similar execution time).\
[> Instructions](./docs/visualize-ties.md)
6. Measure overhead and evaluate results.\
[> Instructions](./docs/visalize-overhead.md)

Contributions
----
* VLDB submission
    * [Overleaf Link](https://www.overleaf.com/project/639797b18d3baa4404d1c7c3)
    * [Latex code and .pdf file](./vldb-submission-latex)

The results and findings of this project have the following contributions towards
 understanding the nature of the MongoDB query optimizer:

* We proposed an innovative way to evaluate and visualize the impact on query performance
of an optimizer’s choices.  By using this approach, we identified places where the MongoDB 
query optimizer chooses sub-optimal query plans. Our approach could form the basis of an 
automated regression testing tool to verify that the query planner in MongoDB improves
 over time. 
* We identified causes of the preference bias of FPTP, in which index scans are systematically 
chosen even when a collection scan would run faster. We evaluate a fix for this problem.
Changes to the MongoDB source code [are included](./mongoversions)
* The query plan visualization tool can visualize ties (i.e. query plans with similar execution
time)

This work was originally based on Dawei Tao's honours thesis: 
[Overleaf Link](https://www.overleaf.com/9886178511bnfhsqfvvmfv)