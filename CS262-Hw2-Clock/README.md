# CS262-Hw2-Clock
CS262 programming assignment 2.   
This assignment creates three virtual machines with different processing speed that can send message to each other. Our goal is to record and analyze how the logical clock will evolve for different combination of clock speeds.

### How to run the code:
You can run simply run the `test.py` to get the test results. Outputs are generated in the log files `1.log`, `2.log`, `3.log`. Each contain the log of activities for its corresponding virtual machine. There are 2 parameters that you can play with:   
`(ticks1, ticks2, ticks3)` - These parameters denote how many number of clock ticks per (real world) second for corresponding machines. This means that only that many instructions can be performed by the machine during that time.  
`send_prob` - This is a parameter taking range from 0 to 1 denote the probability of the instructions being external (i.e. sending message to other machines instead of internal event.)

Additionally, you can change the value of `plot_fig`, which is set as `False` by default, to generate figures for further analysis of the results.

### Implementation details:
We use the module `multiprocessing.Queue` to construct all three virtual machines. The mechanism is pretty simple, each machine has a inqueue (which can be think of as its own message inbox) and two outqueues (which are the inqueues of the other two machines). Sending a message corresponds to put the message to the selected outqueues, and receiving a message corresponds to take one message out from the queue. For full implementation see `logicmachine.py`.

## Notebook
In this notebook we are going to discuss how the logical clock for each machine will be affected by the parameters `(ticks1, ticks2, ticks3)` and `send_prob`.

#### How the logical clock change with `send_prob`?
Let's first look at the case where `(ticks1, ticks2, ticks3) = (2,4,6)`. The following figure shows how the time stamps of each machine changes with global time, `send_prob` is setted to be 3%, 30%, 60%, 90% from left to right:

![](images/tick-2-4-6.png)  

By looking at the first two figures on the left, we may conclude that the machine with the fastest speed will dominate the numbering of the time stamp becuase the three lines almost aligned with each other. This makes sense because when receiving a message the time stamp is calculated `max(time_stamp_of_the_message, local_time_stamp) +1`, which implies that the time stamp at every machine will increase with the time stamp of the fastest one.

Additionally, notice that there's a 'staircase-like' shape in the curve of Machine 1 and 2 when `send_prob = 3%`, while the curve is smoother for `send_prob = 30%`. This can be explained by the fact that the more external interaction, the more frequent the time stamps of slower machines will jump in order to catch up with the time stamp of faster machine.  

However, if we look at the two figures on the right, the time stamp for Machine 1 no longer align with the other two. This is because with the increasing of external event, the speed of getting an external message exceeds the capacity of Machine 1 to handle them. Thus un-processed messages will queue up, which means that message being processed at current time is sent at an earlier time, this 'slows down' the time stamp of Machine 1.

Based on these observations we conclude that there's a 'phase transition' in the behavior of the time stamps as `send_prob` grows larger. The critical point is the point where messages start to queue up in the inbox of the slower machines. If `send_prob` is smaller than this value, then the evolving of time stamps are going to roughly follow the time stamp of the fastest machine. If `send_prob` is larger than this value, messages are going to queue up and we might observe behavior as shown in the two figures on the right.

#### How the logical clock change with  `(ticks1, ticks2, ticks3)`?
In this section, we will vary the parameter `(ticks1, ticks2, ticks3)`, for each set of parameter, we generate a figure similar to previous section to study how the variation of speed is going to affect the time stamp. We tested three sets of parameter: `(ticks1, ticks2, ticks3) = (4,5,6), (2,4,6), (1,6,12)`. The numerical results are shown in following figures:
`(ticks1, ticks2, ticks3) = (4,5,6)` (Small Variation)
![](images/tick-4-5-6.PNG)  
`(ticks1, ticks2, ticks3) = (2,4,6)` (Moderate Variation)
![](images/tick-2-4-6.png)
`(ticks1, ticks2, ticks3) = (1,6,12)` (Large Variation)
![](images/tick-1-6-12.PNG)  
