Final Report
====


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
    * [Latex code and .pdf file](./vldb-submission-latex)
* In the above submission, I propose an innovative way to evaluate and visualize the impact on query performance
of an optimizer’s choices.  By using this approach, I identify places where the MongoDB 
query optimizer chooses sub-optimal query plans. My approach could form the basis of an 
automated regression testing tool to verify that the query planner in MongoDB improves
 over time. 
* I identify causes of the preference bias of FPTP, in which index scans are systematically 
chosen even when a collection scan would run faster. I fix the problem. Different versions 
of the MongoDB source code are available for download and inspection.
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
* Visualize the overhead of the FPTP query optimization.


How To Run The Code
----
Please follow the steps below to run the code. Please note that some steps cannot be skipped.
It is **strongly recommended** to execute the code step by step according to the instructions. 
Otherwise, you may encounter errors. 

1. Deploy different versions of MongoDB on AWS instances. (Includes links to modified MongoDB source code)\
[> Instructions](./final-report/deploy-mongodb-on-aws.md)
2. Prerequisites and suggested settings.\
[> Instructions](./final-report/prerequisites.md)
2. Run the experiment which visualize query plans and their performance.\
[> Instructions](./final-report/run-experiment.md)
3. Visualize ties (i.e. query plans that has similar execution time).\
[> Instructions](./final-report/visualize-ties.md)
4. Measure overhead and evaluate results.\
[> Instructions](./final-report/visalize-overhead.md)