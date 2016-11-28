# Brian Blaylock
# Spring 2015 for Environmental Statistics class.


"""
Bootstrap test for significance
"""


import numpy as np
import matplotlib.pyplot as plt

x = np.random.randint(1,10,10)
y = np.random.randint(1,10,10)

expected_b1 = np.polyfit(x,y,1)[0]

# Number of bootstrap samples
num_b = 5000

# we will fill this vector with the regression coefficient as we find them
b1_vector = np.zeros(num_b)
r = np.corrcoef(x,y)
r_squared = r[0,1]**2

#bootstraping
for i in np.arange(num_b):
    index = np.random.randint(0,len(x),len(x))

    #pull out the (x,y) pair for each index    
    sample_x = x[index]
    sample_y = y[index]

    #calculate the b1 value and store it in the b_vector
    b_values = np.polyfit(sample_x,sample_y,1)

    #b1 is the first element result of polyfit
    b1=b_values[0]
    b1_vector[i]=b1


# Plot results of bootstrapping    
plt.figure(6)
plt.hist(b1_vector,50)
plt.axvline(x=expected_b1,color='r')
plt.title('Bootstrapped x and y')                                
plt.xlabel('b1 coefficient')
plt.ylabel('count')
confidence_level = len(np.argwhere(b1_vector>0))/float(len(b1_vector))
confidence_level_neg = len(np.argwhere(b1_vector<0))/float(len(b1_vector))

print "confidece b>0:", confidence_level
print "confidece b<0:", confidence_level_neg
print "r-squared:", r_squared
print "expected slope (b): ", expected_b1
print " "

# Plot scatter plot of data and trendline
plt.figure(7)
plt.scatter(x,y)
plt.title('scatter')
plt.xlabel('x')
plt.ylabel('y')

# Trendline
m,b = np.polyfit(x,y,1)
plt.plot(x,m*x+b,color='r')
