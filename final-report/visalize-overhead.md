Visualize Overhead
====
This module aims at measure the overhead of FPTP optimization.

Methodology
----
The following graph shows the workflow of FPTP optimization.

![](./images/fptp.png)

From the graph we can deduce a system of equation. 

![](http://www.sciweavers.org/upload/Tex2Img_1624811048/render.png)

Where 
* Latency<sub>coldCache</sub> - the time difference from when the 
query statement is submitted to and the result is obtained (when the query 
plan does not exist in the query plan cache).
* Latency<sub>hotCache</sub> - the time difference from when the 
query statement is submitted to and the result is obtained (when the query 
plan exists in the query plan cache).
* RTT - Round Trip Time is the time it takes for a data packet 
to be sent to a destination plus the time it takes for an acknowledgment of
 that packet to be received back at the origin.
* T<sub>overheadFPTP</sub> - the overhead of FPTP optimization.
* T<sub>queryGeneration</sub> - time to generate a query solution
* T<sub>catchMatching</sub> - the time taken of find a match of query plan cache
* T<sub>execution</sub> - the time taken of executing the query

Subtract equation B from A

![](http://www.sciweavers.org/upload/Tex2Img_1624812487/render.png)

Where
* epsilon - is a very small number
* T<sub>queryGeneration</sub> - is also very small compare to T<sub>overheadFPTP</sub>

As a result we can get 

![](http://www.sciweavers.org/upload/Tex2Img_1624812968/render.png)

That means, we can compute an approximate value of overhead of FPTP opotimization by
1. run a query with cold cache
2. run the same query with hot cache
3. measure the time difference Latency<sub>coldCache</sub> - Latency<sub>hotCache</sub>

Control the number