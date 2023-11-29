def get_arrival_curve(self, data):
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