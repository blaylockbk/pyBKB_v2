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
month = '02'
day = '06'
station = 'URHCL'


from pydap.client import open_url
dataset = open_url("http://asn.mesowest.net/data/opendap/PUBLIC/"+year+"/"+month+"/"+day+"/"+station+"_"+year+month+day+".h5")

print('\n')
BackScatter = dataset['data']['BS'][:]
print BackScatter.shape
#pprint.pprint( BackScatter )

import numpy as np
import matplotlib.pyplot as plt



# Find threshold Function
#   This will find the layer based on the threshold paramater
def find_threshold_index(threshold,profile):        
    current_index_height = 0                # start at 50 m    
    for i in profile:
        print i
        if i < threshold:
            break
        else:
            current_index_height += 1
    return current_index_height


# Simple Threshold Method
################################
bot_ind=0
top_ind=100

for i in range(100,200):

	profile = BackScatter[i][bot_ind:top_ind]
	threshold = -7.3

	PBL_height = find_threshold_index(threshold, profile)*10
	if PBL_height > 50:
		print PBL_height
		
		plt.figure(i)
		plt.hold(True)
		back1 = plt.plot(profile,np.arange(len(profile))*10)
		thresh = plt.axvline(threshold, c='g',ls='--')
		height = plt.axhline(PBL_height, c='r', linestyle='--')

		plt.xlim([-8.5,-6.5])
		plt.ylim([bot_ind*10, top_ind*10])


		plt.legend((thresh,height),('Threshold value: '+str(threshold), 'Estimated Height: '+str(PBL_height)),loc='lower left')
		plt.title('Mixed Layer Height Estimation: Threshold Method')
		plt.xlabel('Backscatter (m^-1 * sr^-1)')
		plt.ylabel('Height (m)')

plt.show()