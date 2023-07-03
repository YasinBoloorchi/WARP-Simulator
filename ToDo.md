Below is a sequence of steps that propose increasingly more difficult programs for you to analyze. You need to use your tool to build trees to answer the following questions for each program.

==== Step 1 ===

The code includes a "while" and a "push" instruction. The while instruction and all the other instructions defined later take 0 clock cycles to execute, while the push instruction takes 1 clock cycle. Push always succeeds (though you should be able to generate the above trees even though this is not the case).

**while(True):**
     **push()**

For this code:

    how many packets will be transmitted in the time interval from [0 to 100]?

<u>Answer:</u>

As all the transmissions will always be successful then in the time interval from [0 to 100] hundred packet will be transmitted.   

![Step one - While loop.gv](/home/hakim/OneDrive/1 - UIowa/Semester 2/3 - Independent Study/Sessions/23 - June 29/Step one - While loop.gv.png)

==== Step 2 ===
Let's make things a bit more complicated. Let's explicitly add a clock variable, an integer whose initial value is 0.  Now consider the following code:

**while (True):**
    **if clock % 100 == 0:**
          **push()**

For this code, answer the following questions:

    how many packets will be transmitted in the time interval from [0 to 100]?
    how many packets will be transmitted in the time interval from [1 to 101]?
    how many packets will be transmitted in the time interval from [2 to 102]?
    how many packets will be transmitted in the time interval from [3 to 103]?
    how many packets will be transmitted in the time interval from [t to  t+100], where t is the start of the interval (t>0)?



<u>Answer:</u>

As in each 100 time clock a packet will be transmitted and all the packets are successful we can say that in every time interval of [t to t+100] where t is the start of the interval only one packet will transmit.



(For ease of eye instead of 100 clock we used 1/10 of scale to show the diagram )

![whil_with_condition_11_clock.gv](/home/hakim/OneDrive/1 - UIowa/Semester 2/3 - Independent Study/WARP Simulator/Output/whil_with_condition_11_clock.gv.png)



Simulation after 200 clock:

![whil_with_condition_201_clock.gv](/home/hakim/OneDrive/1 - UIowa/Semester 2/3 - Independent Study/Sessions/23 - June 29/whil_with_condition_201_clock.gv.png)





==== Step 3 ===
Now, let's assume that there is a transmission queue q that stores packets to be transmitted. The standard API with push, pop, and empty is defined for the queue. Assume constants S=100 and R=100 that control the frequency of packets generated and transmitted.



**let int S = 100**
**let int R = 100**
**queue q**
**while(True):**
    **if clock % R == 0:**
        **q.push(new packet)**

​    **if clock % S == 0:**
​       **if !q.empty():**
​            **p = q.pop()**
​            **push(p)**

For this code, with R = 100 and S = 100, answer these questions:

    how many packets will be transmitted in the time interval from [0 to 1000]?
    
    Ans: 10
    
    how many packets will be added to the queue in the time interval from [0 to 1000]?
    
    Ans: 10
    
    how many packets will be transmitted in the time interval from [t to  t+1000], where t is the start of the interval (t>0)?
    
    Ans: 10
    
    how many packets will be added to the queue in the interval from [t to  t+1000], where t is the start of the interval (t>0)?
    
    ANS: 10
    
    Is there a time interval of length t such that the number of added packets to the queue exceeds the number of packets transmitted?
    
    ANS: No. Because, both S and R number are equal and each time that a packet push into the queue it will be poped immediately after and be pushed to it's destination.

Answer the same questions for R=100 S=50 and R=50 S=100.
As a stretch goal --- what happens if we make push probabilistic with p=0.9?

I hope this helps. Let me know if you have questions,
