# Brian Blaylock
# Mean Smoother

import numpy as np

def mean_smooth(data, ns, p):
    """
    data is a 1D array
    n is the length of the data array
    ns is the number of elements in smoother. Must be odd.
    p is the number of passes of the smoother
    Better to smooth with small ns and more p's than large ns and 1-2 p's
    
    Returns the smoothed array
    First and last elements are set to the original values on each pass
    """
    tmp = data
    n = len(tmp)
    
    for j in np.arange(1,p+1):
        half = (ns-1)/2
        # Initialize the smooth array
        smooth = np.zeros(n)
        # Set first and last elements not included in smoother 
        # to same as data
        smooth[0:half]=tmp[0:half]
        smooth[-half:]=tmp[-half:]
        for i in np.arange(half,n-half):
            values=tmp[i-half:i+half+1]
            smooth[i]=np.mean(values)
        tmp = smooth        
        
    return smooth
    
def median_smooth(data, ns, p):
    """
    data is a 1D array
    n is the length of the data array
    ns is the number of elements in smoother. Must be odd.
    p is the number of passes of the smoother
    Better to smooth with small ns and more p's than large ns and 1-2 p's
    
    Returns the smoothed array
    First and last elements are set to the original values on each pass
    """
    tmp = data
    n = len(tmp)
    
    for j in np.arange(1,p+1):
        half = (ns-1)/2
        # Initialize the smooth array
        smooth = np.zeros(n)
        # Set first and last elements not included in smoother 
        # to same as data
        smooth[0:half]=tmp[0:half]
        smooth[-half:]=tmp[-half:]
        for i in np.arange(half,n-half):
            values=tmp[i-half:i+half+1]
            smooth[i]=np.median(values)
        tmp = smooth        
        
    return smooth
        
        
if __name__ == "__main__":
    
    import matplotlib.pyplot as plt
    
    data = np.random.randint(0,5,12)
    
    plt.plot(data,lw=3,label="Data")
    
    smoothed = median_smooth(data,5,1)
    plt.plot(smoothed,label='pass 1')
    
    smoothed = median_smooth(smoothed,5,1)
    plt.plot(smoothed,label='pass 2')
    
    smoothed = median_smooth(smoothed,5,1)
    plt.plot(smoothed,label='pass 3')
    plt.legend()