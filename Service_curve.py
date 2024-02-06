import matplotlib.pyplot as plt
import numpy as np

def plot_arrival_curve(service_curve, plot_name='Arrival Curve Examples'):
    x_values, y_values = zip(*service_curve)
    
    # Plot it
    plt.plot(x_values, y_values, marker='o', label=f'Arrival Curve', markerfacecolor='k')#, where='pre')
    
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



def get_service_curve(data, verbose=False):
        service_curve = list()
        
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
            
            
            service_curve.append((td, min(delta)))
            print('Service Curve: ', service_curve)
            print() 
        return service_curve
    
CNP = [0,1,1,2,2,3]
result = get_service_curve(CNP)
print(result)
plot_arrival_curve(result)