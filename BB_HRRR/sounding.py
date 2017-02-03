#
#
#  sounding.py
#
#  This script plots skew-T diagrams using bufr formatted data 
#
#  Skew-T plotting software from https://pypi.python.org/pypi/SkewT
#  
#  Jim Steenburgh 
#  modified by bkb 05/20/15
#  modified by jdh 05/23/15 to do automatically as downloading files
#  modified by bkb 05/26/15 to include ogden
#  modified by bkb 07/07/15 to plot actual slc sounding at hour 23, 00, 11,and 12
#  modified by tam 08/20/15 fix dewpoints. Take lowest three levels and replace with the fourth level
#  modified by bkb 01/29/16 only fix dewpoints if the dewpoint temp is less than the temperature
#
import matplotlib
matplotlib.use('Agg')
from matplotlib.pyplot import savefig
import os, sys, time
from datetime import datetime, timedelta
from pytz import timezone
import pytz
import calendar
from skewt import SkewT
from numpy import *
import urllib2
from bs4 import BeautifulSoup
#from bufrconfig import *
#
# 
#
def calcght(tsfc,zsfc,psfc,plev):
  lapse = .0065
  exp = 287.*lapse/9.81
  zlev = zsfc + ((tsfc+273.15)/lapse)*(1.-(plev/psfc)**exp)
  return zlev
#
# Returns RH (%) from temperature and dewpoint in C
#
def calcrh(tval,tdval):
  if tdval>=tval:
    rh=100.0
  else:
    rh = 100.0*exp(5422.0*(1.0/(tval+273.15)-1.0/(tdval+273.15)))
  if rh > 100.0:
    rh = 100.0
  if rh < 0:
    rh = 1.0
  return rh
#
# Returns potential temperature (K) from temperature (C) and pressure (mb)
#
def calctheta(tval,pres):
   theta = (tval+273.15)*(1000/pres)**.2859
   return theta
#
# Returns virtual temperature (C) from temperature (C) and mixing ratio (g/kg) 
#
def calctv(tval,wval):
   ee = .622
   tv = (tval+273.15)*(wval/1000+ee)/(ee*(1+wval/1000)) - 273.15
   return tv

################################################################################
# Functions from https://svn.ssec.wisc.edu/repos/geoffc/Python/Science/thermo.py
# Downloaded 28 Apr 2015
# Created by Geoff Cureton on 2009-04-04.
# Copyright (c) 2011 University of Wisconsin SSEC. All rights reserved.
#
from scipy import log10

def rh_to_mr( rh, p, t) :
  '''
  Returns mixing ratio, in g/kg, given relative humidity in %, 
  pressure in hPa and temperature in K.
  '''
  return rh * 0.01 * satmix(p, t)

def rh_to_mr_wat( rh, p, t) :
  '''
  Returns mixing ratio over water, in g/kg, given relative humidity in %, 
  pressure in hPa and temperature in K.
  '''
  return rh * 0.01 * satmixwat(p, t)

def rh_to_mr_ice( rh, p, t) :
  '''
  Returns mixing ratio over ice, in g/kg, given relative humidity in %, 
  pressure in hPa and temperature in K.
  '''
  return rh * 0.01 * satmixice(p, t)

def mr_to_rh( mr,  p,  t) :
  '''
  Returns relative humidity in %, given the mixing ratio in g/kg,  
  pressure in hPa and temperature in K.
  '''
  return mr * 100. / satmix(p, t)

def mr_to_rh_wat( mr,  p,  t) :
  '''
  Returns relative humidity in %, given the mixing ratio over water in g/kg,  
  pressure in hPa and temperature in K.
  '''
  return mr * 100. / satmixwat(p, t)

def mr_to_rh_ice( mr,  p,  t) :
  '''
  Returns relative humidity in %, given the mixing ratio over ice in g/kg,  
  pressure in hPa and temperature in K.
  '''
  return mr * 100. / satmixice(p, t)

def satmix( p, t) :
  '''
  Returns saturation mixing ratio in g/kg, given pressure in hPa and
  temperature in K.
  '''
  if (t > 253.) :
    return satmixwat(p, t)
  else :
    return satmixice(p, t)

def satmixwat( p,  t) :
  '''
  Returns saturation mixing ratio over water, in g/kg, given pressure in hPa and
  temperature in K.
  '''
  es = svpwat(t)
  return (622. * es)/p

def satmixice( p, t) :
  '''
  Returns saturation mixing ratio over ice, in g/kg, given pressure in hPa and
  temperature in K.
  '''
  es = svpice(t);
  return (622. * es) / p;


def svpwat(t) :
  '''
  Returns saturation vapor pressure over water, in hPa, given temperature in K.
  
  '''

  a0 =  0.999996876e0
  a1 = -0.9082695004e-2
  a2 =  0.7873616869e-4
  a3 = -0.6111795727e-6
  a4 =  0.4388418740e-8
  a5 = -0.2988388486e-10
  a6 =  0.2187442495e-12
  a7 = -0.1789232111e-14
  a8 =  0.1111201803e-16
  a9 = -0.3099457145e-19
  b = 0.61078e+1
  t -= 273.16
  return (b / ((a0+t*(a1+t*(a2+t*(a3+t*(a4+t*(a5+t*(a6+t*(a7+t*(a8+t*a9)))))))))**8.))

def svpice( t) :
  '''
  Returns saturation vapor pressure over ice, in hPa, given temperature in K.
  The Goff-Gratch equation (Smithsonian Met. Tables,  5th ed., pp. 350, 1984)
  '''
  a = 273.16 / t
  exponent = -9.09718 * (a - 1.) - 3.56654 * log10(a) + 0.876793 * (1. - 1./a) + log10(6.1071)

  return 10.0**exponent

daysofweek=['MON','TUE','WED','THU','FRI','SAT','SUN']  
################################################################################     
#
# Get models and Read in Bufr File
#
#
arcdir = '/uufs/chpc.utah.edu/common/home/horel-group/archive/'

model=sys.argv[1]
site=sys.argv[2]
iyear = sys.argv[3]
imonth = sys.argv[4]
iday = sys.argv[5]
ihour = sys.argv[6]
anl = sys.argv[7]
#for x in range (1,len(sys.argv)):
#  models.append(sys.argv[x])
#for model in models:
#  if model == 'gfs':
#    sites = ['kslc','alta','lo1','ksgu','kjac','kfca','kvel','krdd','klgu','kbzn']
#  else:
#    sites = ['kslc','alta','lo1','ksgu','kjac','kgpi','kvel','mhs','klgu','kbzn']
#  for site in sites:
    # read in BUFR file
print("\n\nPROCESSING DATA for model:'{0}'".format(model.upper()))
print("  Site:'{0}'".format(site))
archivedir = arcdir + iyear + imonth + iday + '/models/hrrr/'
plotdir = arcdir + iyear + imonth + iday + '/images/models/hrrr/'
bufrfile = archivedir + site + '_'+iyear + imonth + iday + ihour + '.buf'
if os.path.exists(plotdir):
	print 'plot dir'  + plotdir
else:
	os.system('mkdir ' + plotdir)

print("  Reading buffer file:{0}".format(bufrfile))
f=open(bufrfile,'r')
ls=f.readlines()
f.close()

    # Get dimensions/validtimes of BUFR data
ptimes=[]
fhr=[]
for i in range(len(ls)):
  l=ls[i]
# bkb: when adding new stations, check that the station id is included in this list
  if l[0:5]=='72572' or l[0:5]=='72575' or l[0:4]=='298 ' or l[0:5]=='45012' or l[0:5]=='45139' or l[0:5]=='71629' or l[0:5]=='71624' or l[0:5]=='72529' or l[0:5]=='72515' or l[0:5]=='72519' or l[0:4]=='821 ' or l[0:5]=='72622' or l[0:5]=='72475' or l[0:5]=='72577' or l[0:5]=='72779' or l[0:5]=='72570' or l[0:4]=='728 ' or l[0:5]=='72592' or l[0:5]=='72479' or l[0:5]=='72679' or l[0:6]=='856290':
    ptimes.append(datetime(2000+int(l.split(' ')[1][0:2]),int(l.split(' ')[1][2:4]),int(l.split(' ')[1][4:6]),int(l.split(' ')[1][7:9])))
  if l[0:4] == 'STIM':
     fhr.append(int(l.split(' ')[2]))
ptimes=array(ptimes)
starttime=ptimes[0]
endtime=ptimes[-1]
maxfhr=int(24.0*(endtime-starttime).days+(endtime-starttime).seconds/3600)
step=int(maxfhr/float(len(ptimes)-1))
numhours=len(ptimes)
getind=[]
for l in ls:
  if l[0:4]=='STID':
    getind.append(ls.index(l))
numlevs=(min(array(getind)[1:-1]-array(getind)[0:-2])-12)/2
print("  FOUND DATA (time) from {0} to {1}".format( starttime,endtime))
print("  Data captured every {0} hours through hour {1}".format(step,maxfhr))
print("  Time step size:{0}".format(step))
print("  #Vertical levels:{0}".format(numlevs))
print("  #Hours:{0}".format(numhours))

# initialize 2-D arrays of BUFR data (val versus time,level)
p=zeros((numhours,numlevs))
z=zeros((numhours,numlevs))
t=zeros((numhours,numlevs))
tw=zeros((numhours,numlevs))
td=zeros((numhours,numlevs))
#rh=zeros((numhours,numlevs))
dir=zeros((numhours,numlevs))
spd=zeros((numhours,numlevs))
#    theta=zeros((numhours,numlevs))
#    thetae=zeros((numhours,numlevs))
#    thetav=zeros((numhours,numlevs))
#    mixrat=zeros((numhours,numlevs))

# fill 2-D BUFR arrays
for i in range(numhours):
  ind1=arange(getind[0]+i*(numlevs*2+12)+11,getind[0]+i*(numlevs*2+12)+11+numlevs*2,2)
  for j in range(len(ind1)):
    p[i,j]=float((ls[ind1[j]].rstrip()).split(' ')[0])
    t[i,j]=float((ls[ind1[j]].rstrip()).split(' ')[1])
    tw[i,j]=float((ls[ind1[j]].rstrip()).split(' ')[2])
    td[i,j]=float((ls[ind1[j]].rstrip()).split(' ')[3])
#
#   Hack here forces td to be <= t.  Needed due to problems with GFS BUFR data
# bkb: so, does this hack need to be here for HRRR BUFR data?????
    if td[i,j] > t[i,j]:
      print 'Reseting',model,'td at',site
      print 'Run initialized at',starttime,'forecast hour= ',fhr[i]
      print 'p=',p[i,j],'t=',t[i,j],'td=',td[i,j]
      td[i,j] = t[i,j]
#        thetae[i,j]=float((ls[ind1[j]].rstrip()).split(' ')[4])
#        rh[i,j]=calcrh(t[i,j],td[i,j])
    dir[i,j]=float((ls[ind1[j]].rstrip()).split(' ')[5])
    spd[i,j]=float((ls[ind1[j]].rstrip()).split(' ')[6])
    if 'nam' in model:
      z[i,j]=float((ls[ind1[j]+1].rstrip()).split(' ')[1])
# bkb: added correct hrrr height value
    elif 'hrrr' in model:
      z[i,j]=float((ls[ind1[j]+1].rstrip()).split(' ')[1])
    else:
      z[i,j]=float((ls[ind1[j]+1].rstrip()).split(' ')[0])
#        theta[i,j]=calctheta(t[i,j],p[i,j])
#        mixrat[i,j]=rh_to_mr(rh[i,j],p[i,j],t[i,j]+273.15)
#        thetav[i,j]=calctheta(calctv(t[i,j],mixrat[i,j]),p[i,j])

# QC measures for BUFR data
tw[i,:]=where(logical_and(greater(tw[i,:],50),greater(z[i,:],1000)),-80.0,tw[i,:])

for i in range (numhours):
  junk = str(ptimes[i])
  idayofweek = calendar.weekday(int(junk[0:4]),int(junk[5:7]),int(junk[8:10]))
  dayofweek = daysofweek[idayofweek]
  print 'plotting forecast sounding valid',junk[11:13],'Z',dayofweek,junk[8:10],calendar.month_abbr[int(junk[5:7])],junk[0:4]
#
# Stuff here to add mandatory levels
#
  manlevels=[1000.0, 925.0, 850.0, 700.0, 500.0]
  manheight=[calcght(t[i,0],z[i,0],p[i,0],1000.),calcght(t[i,0],z[i,0],p[i,0],925.),calcght(t[i,0],z[i,0],p[i,0],850.),calcght(t[i,0],z[i,0],p[i,0],700.),calcght(t[i,0],z[i,0],p[i,0],500.)]
  maxpres=max(p[i,:])
  if maxpres < 500:
    naddlevs = 5
  elif maxpres < 700:
    naddlevs = 4
  elif maxpres < 850:
    naddlevs = 3
  elif maxpres < 925:
    naddlevs = 2
  elif maxpres < 1000: 
    naddlevs = 1
  else:
    naddlevs = 0
  paddlevs = manlevels[0:naddlevs]
  zaddlevs = manheight[0:naddlevs]
  otheraddlevs = []
  for k in range(naddlevs):
    otheraddlevs.append(-999.)
  print 'max pres',maxpres,'paddlevs',paddlevs,'naddlevs',naddlevs,'p',p[i,:]
#  pnew = concatenate((paddlevs,p[i,:]),axis=1)
#  znew = concatenate((zaddlevs,z[i,:]),axis=1)
#  tnew = concatenate((otheraddlevs,t[i,:]),axis=1)
#  tdnew = concatenate((otheraddlevs,td[i,:]),axis=1)
#  dirnew = concatenate((otheraddlevs,dir[i,:]),axis=1)
#  spdnew = concatenate((otheraddlevs,spd[i,:]),axis=1)
#  mydata=dict(zip(('hght','pres','temp','dwpt','drct','sknt'),(znew,pnew,tnew,tdnew,dirnew,spdnew)))   
  mydata=dict(zip(('hght','pres','temp','dwpt','drct','sknt'),(z,p,t,td,dir,spd)))   


  if site=='kslc':
# !!! Taylor McCorkle: Correct for moist biased dewpoint values in lowest levels of sounding: 08/20/15
    print "**correcting kslc moist bias"
    mydata_fix = {}
    mydata_fix = mydata
    mydata_fix['dwpt'][:,0] = mydata_fix['dwpt'][:,3] # replace lowest level
    mydata_fix['dwpt'][:,1] = mydata_fix['dwpt'][:,3] # replace 2nd lowest
    mydata_fix['dwpt'][:,2] = mydata_fix['dwpt'][:,3] # replace 3rd lowesti
 # bkb: if dewpoint is greater than temperature, then set them equal to each other
    if mydata_fix['dwpt'][i][0]>mydata_fix['temp'][i][0]:
      mydata_fix['dwpt'][i][0]=mydata_fix['temp'][i][0]    
    if mydata_fix['dwpt'][i][1]>mydata_fix['temp'][i][1]:
      mydata_fix['dwpt'][i][1]=mydata_fix['temp'][i][1]
    if mydata_fix['dwpt'][i][2]>mydata_fix['temp'][i][2]:
      mydata_fix['dwpt'][i][2]=mydata_fix['temp'][i][2]


  else:
    print "don't correct moist bias at provo or ogden"
    mydata_fix = mydata

## !!! Brian Blaylock: The problem here is that it's trying to plot all 
##                     the data in the dictionary on the same plot. 
  #S=SkewT.Sounding(soundingdata=mydata)
## !!! Instead, Need to create a new dictionary for each hour.
## Note: use the fixed data
  hourdata = {'drct':mydata_fix['drct'][i],'dwpt':mydata_fix['dwpt'][i],'hght':mydata_fix['hght'][i],'pres':mydata_fix['pres'][i],'sknt':mydata_fix['sknt'][i],'temp':mydata_fix['temp'][i]}
  S=SkewT.Sounding(soundingdata=hourdata)

#
#     Info for header and filename
#
  if fhr[i] <= 9:
    cfhr = '00' + str(fhr[i])
  elif fhr[i] <= 99:
    cfhr = '0' + str(fhr[i])
  else:
    cfhr = str(fhr[i])
  ccccddyy='%.i'%starttime.year+'%02d'%starttime.month+'%02d'%starttime.day
  hh = '%02d'%starttime.hour
  if 'nam4' in model:
    subdir = 'namhires'
    modid = 'NAM'
  elif 'nam12' in model:
    subdir = 'nam218'
    modid = 'NAM'
  elif 'gfs' in model:
    subdir = 'gfs004'
    modid = 'GFS'
  else:
    subdir = 'hrrr'
    modid = 'HRRR'
  #graphicsfile = plotdir+'/'+ccccddyy+'/images/models/'+subdir+'/'+modid+'SKEWT_'+site.upper()+ccccddyy+hh+'F'+cfhr
  graphicsfile = plotdir+modid+'SKEWT_'+site.upper()+ccccddyy+hh+'F'+cfhr
  titlestring = ccccddyy+hh+'F'+cfhr+modid+' '+site.upper()+' Valid '+ junk[11:13] + 'Z' + dayofweek + junk[8:10] + calendar.month_abbr[int(junk[5:7])] + junk[0:4]

  S.plot_skewt(title=titlestring,color='r',lw=2)



#\ bkb: Added the lifted parcel: ml=mixed layer, mu=most unstable, sb=surface based 

  pc=S.get_parcel('mu')
  S.lift_parcel(*pc)


#/  

#\ bkb: add real balloon data if it is 12z, 00z, 11z, or 23z
  if (junk[11:13]=='12') or (junk[11:13]=='00') or (junk[11:13]=='23') or (junk[11:13]=='11'):
    print ""
    print "**** PLOTTING REAL SOUNDING ****"
    print ""
    stn = '72572' #this is the ID for the slc balloon
    year = junk[0:4]
    month= junk[5:7]
    day  = junk[8:10]
    hour = junk[11:13]

    # Need to process a little differently for 23 and 11 o'clock
    datetime_fmt = datetime(int(year),int(month),int(day),int(hour))
    if (junk[11:13]=='23') or (junk[11:13]=='11'):
      back_an_hour = datetime_fmt-timedelta(hours=-1)
      year = str(back_an_hour.year)
      month= str(back_an_hour.month).zfill(2)
      day =  str(back_an_hour.day).zfill(2)
      hour = str(back_an_hour.hour).zfill(2)

    # Download, process and add to plot the Wyoming Data
    # 1)
    # Wyoming URL to download Sounding from
    url = 'http://weather.uwyo.edu/cgi-bin/sounding?region=naconf&TYPE=TEXT%3ALIST&YEAR='+year+'&MONTH='+month+'&FROM='+day+hour+'&TO='+day+hour+'&STNM='+stn
    content = urllib2.urlopen(url).read()
    
    # 2)
    # Remove the html tags
    soup = BeautifulSoup(content, "html.parser")
    data_text = soup.get_text()
    
    # 3)
    # Split the content by new line.
    splitted = data_text.split("\n",data_text.count("\n"))

    #4)
    # Write this splitted text to a .txt document
    Sounding_dir = arcdir+year+month+day+'/models/hrrr/'
    Sounding_filename = 'SLC_balloon_'+str(stn)+'.'+str(year)+str(month)+str(day)+str(hour)+'.txt'
    f = open(Sounding_dir+Sounding_filename,'w')
    for line in splitted[4:]:
        f.write(line+'\n')
    f.close()   

    #5) 
    # Add to plot
    T = SkewT.Sounding(filename=Sounding_dir+Sounding_filename)
    S.soundingdata=T.soundingdata
    S.add_profile(color='b',lw=.5,bloc=1) 
#/


  savefig(graphicsfile+'.png')
  print graphicsfile+'.png'
  os.system('convert '+graphicsfile+'.png '+graphicsfile+'.gif')
  print 'fiinished creating: ',graphicsfile+'.gif'
  os.system('rm '+graphicsfile+'.png')
#terminate if want only analysis
  if anl == 'anl':
	break
