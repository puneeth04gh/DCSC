# Lab 2 - Convert WordCount to UrlCount

## Resources used:
```
https://www.vogella.com/tutorials/JavaRegularExpressions/article.html
https://www.w3schools.com/java/java_regex.asp
https://data-flair.training/blogs/hadoop-combiner-tutorial/
https://www.hadoopinrealworld.com/can-reducer-always-be-reused-for-combiner/
```
## Software used
* CSEL
* Hadoop
* Git


## Steps to execute in dataproc
* Cloned the git repository in the master instance
* Run the command 'make filesystem' to create the directories
* Run the command 'make prepare' to dowload the input files
* Run the command 'time make run' to run the jar file and to time the execution
* Run the command 'hdfs dfs -ls /user/user/output' to list the out files
* Run the command 'hdfs dfs -cat /user/user/output/part-r-00000' to display the output

## Changes performed for mapper and reducer for UrlCount
For the mapper, I used the regex pattern and matcher to match the href="link" entreis from the input and then used the substring to obtain only the links and pass it as tokens for further steps.
In the reducer we iterate all the links with its count and take only the count which is greater than 5.

## Observation
After executing the UrlCount program in the dataproc, below is the following obervations recorded.

This is the execution screenshot of 2 nodes without the combiner
<img width="1111" alt="2 nodes wo combiner" src="https://user-images.githubusercontent.com/111805831/189173123-d764fcb1-acad-445d-8bf3-33b9dbd2ba72.png">


This is the execution screenshot of 4 nodes without the combiner
<img width="1109" alt="4 nodes wo combiner" src="https://user-images.githubusercontent.com/111805831/189173134-23665f72-e47b-4b93-8508-1b47c8f624a4.png">


We observe that without the combiner, the execution time using 4 nodes is almost same or slightly more than the 2 nodes. This might be due to the network latency for the 4 node structure. Also, the factors affecting the 4 nodes might be due to the input file not being big enough, memory, cpu utilization, network bandwidth or hardware as well.

Below is the observation made after using combiner. Here we see 4 nodes perfroming slightly better than the 2 nodes. In this instance the combiner is just taking the inputs from the mapper and iterating them and sending to the reducer.
  
This is the execution screenshot of 2 nodes with the combiner
<img width="1112" alt="2 nodes with combiner" src="https://user-images.githubusercontent.com/111805831/189172591-0301d5dd-8528-4871-85ac-c2200a2d547f.png">

This is the execution screenshot of 4 nodes with the combiner
<img width="1122" alt="4 nodes with combiner" src="https://user-images.githubusercontent.com/111805831/189173131-0ec23541-17aa-42eb-b91d-ea89cd7e2c8d.png">


Suppose, if we have the combiner same as the reducer for the UrlCount i.e having > 5 condition for url count, then it will result in a different output than what is expected. This is because for each and every mapper, when we have the combiner implemented, it will have its own combiner for the mapper. Hence the keys might have differnt combiners, for example [key1: 1, 1, 1] might be in one combiner and the same key [key1: 1, 1, 1] is on the other combiner, but when we implement > 5 count to be passed onto reducer, then this execution will result in wrong output and miss out on the key1 even though the combined count is > 5. The screenshot below shows the output when combiner is used.

<img width="676" alt="With combiner" src="https://user-images.githubusercontent.com/111805831/189191535-9793c6f9-99c5-493c-998f-1f69f69c90af.png">
