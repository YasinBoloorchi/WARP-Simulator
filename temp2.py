def get_arrival_curve(data):
    arrival_curve = list()
    
    # for each time duration (td: time duration)
    for td in range(1, len(data)):
        delta = list()
        print('     Time Duration: ',td)
        # we calculate maximum delta for each data[i: i+td+1]
        for i in range(len(data)-td):
            segment = data[i: i+td+1]
            print(f'data[{i}: {i+td+1}]', segment, '     max - min => ', max(segment) - min(segment))
            delta.append(max(segment) - min(segment))
        
        print('         Max is: ', max(delta))
        arrival_curve.append((td, max(delta)))
    
    
    return arrival_curve
       
# data = [1] 
data = [1, 1, 2, 2, 2]
# data = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 6]
# data = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 8]
print("data: ", data)
print("len of data: ", len(data))
ac = get_arrival_curve(data)
print("Len of ac: ", len(ac))
print(ac)