"""
Brian Blaylock
Summer Research 2014
Using ceilometer aerosol backscatter thresholds to determind
the boundary layer heights.

This code is a simple example of using the threshold method
for estimating the boundary layer heights. Here we plot the
backscatter for a single observation. A threshold backscatter 
value is subjectivity chosen as the height of the PBL. 
"""

# Brian Blaylock
# Summer Research 2014
# Plot backscatter profile and threshold method

year = '2014'
month = '01'
day = '27'
station = 'URHCL'

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import medfilt
from pydap.client import open_url
dataset = open_url("http://asn.mesowest.net/data/opendap/PUBLIC/"+year+"/"+month+"/"+day+"/"+station+"_"+year+month+day+".h5")

print('\n')
BackScatter = dataset['data']['BS'][:]
height = dataset['HEIGHT'][:]
print BackScatter.shape
#pprint.pprint( BackScatter )





# Find Gradient Function
#   This will find the layer based on the largest gradient
def gradient_method(input_backscatter):
## Takes an array of backscatter data and returns an array of the
## mixed layer heights using the gradient method.
	
	ML_grad = []
	each_ob = input_backscatter
	slope = [0]
	i = 0
	while i < len(each_ob)-1:
		
		if each_ob[i]<-8.5:
		## If the backscatter is small, it has attenuated
		## and we shouldn't think it's a minimum in the gradient.
		## Instead, we'll input a nan to the slope list and move on.
			slope.append(np.nan)
			i +=1
		else:
			db_dz = (each_ob[i+1]-each_ob[i])/((i+1)-i)
			slope.append(db_dz)
			i += 1
	# find min index
	min_slope = np.nanmin(slope[6:]) #since there is noise below 50 meters, we only want to look at point above 60 meters
	min_index = np.where(slope==min_slope)
	ML_grad.append(height[min_index[0][0]])
	print height[min_index[0][0]]
	return ML_grad,slope


# Simple Threshold Method
################################
bot_ind=0
top_ind=50


for i in range(0,20,5):
	profile = BackScatter[i][bot_ind:top_ind]

	#smooth profile to eliminate noise
	profile=medfilt(profile,21)

	max_slope, slope = gradient_method(profile)

	back, = plt.plot(profile,np.arange(len(profile))*10,'r')
	grad, = plt.plot(slope,np.arange(len(slope))*10,'b')
	height_plot = plt.axhline(max_slope, c='r', linestyle='--')

	plt.xlim([-10,2])
	plt.ylim([bot_ind*10, top_ind*10])


	plt.legend((back,grad,height_plot),('Backscatter Profile','Gradient Profile','Estimated Height: '+str(max_slope[0])),loc='upper center')
	plt.title('Mixed Layer Height Estimation: Gradient Method')
	plt.xlabel('Backscatter (m^-1 * sr^-1)')
	plt.ylabel('Height (m)')

	plt.show()