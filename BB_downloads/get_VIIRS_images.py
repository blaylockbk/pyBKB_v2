# Brian Blaylock
# January 9, 2015

"""
Download and save available VIIRS images
"""

import urllib,urllib2
from datetime import datetime, timedelta


# Since images can be created of any minute of the day, here we try to find 
# if an image is available at any minute between two dates. Yeah, I know it
# takes a long time to loop over every minute to find a date.


# There are several available products. We will save all of them.
product = ["snowcloud.jpg",
           "truecolor.jpg",
           "vis.gif",
           "fog.gif",
           "ntmicro.jpg",
           "39um.gif",
           "11um.gif",
           "dust.jpg"]

#Loop through a set of dates
start_date = datetime.now()-timedelta(days=3)
end_date = datetime.now()
print start_date
print end_date


current_time = start_date
#Loop until a specified date is reached
while current_time < end_date:
    #Do whatever you want to after getting the date
    string_time = current_time.strftime("%Y%m%d_%H%M")    
    #print "Looking for image", string_time

    URL = "http://weather.msfc.nasa.gov/sport/dynamic/viirsConusa/wnregion/"+string_time+"_sport_viirs_wnregion_"+product[0]        
        
        #Check if the Image is avaiable        
    try:
        f = urllib2.urlopen(urllib2.Request(URL))
        deadLinkFound=False
    except:
        deadLinkFound=True
    #If the Image exists:
    if deadLinkFound==False:
        for p in product:
            URL = "http://weather.msfc.nasa.gov/sport/dynamic/viirsConusa/wnregion/"+string_time+"_sport_viirs_wnregion_"+p            
            #print URL            
            file_name='VIIRS_'+p[0:-4]+'_'+string_time+'_UTC'+p[-4:]
            print "saving", file_name
            img = urllib.urlretrieve(URL,file_name)
            
#           #^ Something to add to this code, not all satellite images have data for 
#           #  over Utah. Could check how much of image is black, then, if less 
#           #  than half we will save the image.
#           #from PIL import Image
#
#            img = Image.open("B:\public_html\NASA_SPoRT_VIIRS_Images\VIIRS_dust_20150104_1834_UTC.jpg").convert('1')
#            black,white = img.getcolors()
#            
#            img.save('test.gif')
#            
#            b= float(black[0])
#            w= float(white[0])
#            print "percentage", b/(b+w)

    #check next minute on repeat
    current_time = current_time+timedelta(minutes=1)
    