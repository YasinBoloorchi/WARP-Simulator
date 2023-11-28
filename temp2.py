def get_arrival_curve(data):
    arrival_curve = list()
    
    # for each time duration (td: time duration)
    for td in range(1, len(data)+1):
        delta = list()
        
        # we calculate maximum delta for each data[i: i+td+1]
        for i in range(len(data)-td+1):
            segment = data[i: i+td+1]
            delta.append(max(segment) - min(segment))
            
        arrival_curve.append((td, max(delta)))
    
    
    return arrival_curve
        
data = [1, 1, 2, 2, 2]
data = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 6]
data = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 8]
print("len of data: ", len(data))
ac = get_arrival_curve(data)
print(ac)