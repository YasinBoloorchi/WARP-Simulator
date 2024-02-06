import matplotlib.pyplot as plt
import numpy as np

def plot_arrival_curve(arrival_curve, plot_name='Arrival Curve Examples'):
    x_values, y_values = zip(*arrival_curve)
    
    # Plot it
    plt.step(x_values, y_values, marker='o', label=f'Arrival Curve', markerfacecolor='k', where='pre')
    
    # Customization
    plt.xticks(np.arange(min(x_values), max(x_values)+1, 1))
    plt.yticks(np.arange(0, max(y_values)+1, 1))
    # plt.title(plot_name)
    plt.xlabel("Time Duration") #Δ
    plt.ylabel('Number of packets')
    plt.grid()
    plt.legend()
    plt.show()
    # plt.savefig("./Output/Plots/"+plot_name+'_arrival_curve'+'.pdf', format="pdf")
    # plt.savefig("./Output/Plots/"+plot_name+'_arrival_curve', dpi=300)
    # plt.clf()



def get_arrival_curve(data, verbose=False):
        arrival_curve = list()
        
        # for each time duration (td: time duration)
        for td in range(0, len(data)):
            delta = list()
            print('Time duration: ', td)
            # we calculate maximum delta for each data[i: i+td+1]
            for i in range(len(data)-td):
                segment = data[i: i+td+1]
                print(f'Segment [{i} : {i+td+1}] ==> ', segment)
                delta.append(max(segment) - min(segment))
                print('delta: ', delta)
            
            
            arrival_curve.append((td, max(delta)))
            print('Service Curve: ', arrival_curve)
            print() 
        return arrival_curve
    
# CNP = [0,0,1,1,1,2,2,2,2,2,3,3,3,3,3,4]

# case 1
CNP = [0,0,1,1,2,2,3]

# case 2
# CNP = [0,1,1,2,2,3,3]

# case 3?
# CNP = [1,1,2,2,3,3,4,4,5,5]

result = get_arrival_curve(CNP)
print(result)
plot_arrival_curve(result)