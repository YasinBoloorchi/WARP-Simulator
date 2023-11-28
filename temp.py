l = [1,2,3,4,5]

for i in range(1, len(l)+1):
    print("i: ", i)
    print('Duration: ', i+1)
    for j in range(len(l)-i):
        print("     j: ",j, ':',j+i+1)
        print('     l: ', l[j: j+i+1])
        
        
    """
    i = 1
        l[0:1]
        l[1:2]
        l[2:3]
        l[3:4]
        l[4:5]
    
    i = 2
        l[0:2]
        l[1:3]
        l[2:4]
        l[3:5]
    
    i = 3
        l[0:3]
        l[1:4]
        l[2:5]
        
    i = 4
        l[0:4]
        l[1:5]
        
    i = 5
        l[0:5]
    """