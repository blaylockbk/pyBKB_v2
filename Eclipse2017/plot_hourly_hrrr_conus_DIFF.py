# Brian Blaylock
# August 16, 2017               I'm going to BFLAT to replace a sensor tomorrow

"""
Plot hourly eclipse path with 
MesoWest, HRRR, and HRRRx Short Wave Radiation Flux
"""
import matplotlib as mpl
#mpl.use('Agg')#required for the CRON job. Says "do not open plot in a window"??
import numpy as np
from datetime import datetime, timedelta, date
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2/')
from BB_MesoWest.MesoWest_radius import get_mesowest_radius
from BB_basemap.draw_maps import draw_CONUS_cyl_map, draw_CONUS_HRRR_map
from BB_downloads.HRRR_S3 import get_hrrr_variable
from BB_wx_calcs.wind import wind_uv_to_spd

import matplotlib as mpl
mpl.rcParams['figure.subplot.wspace'] = 0.05
mpl.rcParams['figure.subplot.hspace'] = 0.05

# Read Eclipse path file
# Names: 'year', 'month', 'day', 'hour', 'min', 'NorthLatitude', 'NorthLongitude', 'SouthLatitude', 'SouthLongitude', 'CenterLatitude', 'CenterLongitude', 'MS_Ratio', 'Sun_Alt', 'Sun_Azm', 'Path_Width', 'Central_Duration'
E = np.genfromtxt('eclipsePath.csv', dtype=None, delimiter=',', names=True)

# Eclipse Datetimes
DATES = [datetime(E['year'][i], E['month'][i], E['day'][i], E['hour'][i], E['min'][i]) for i in range(len(E['year']))]
num = len(DATES)

# Eclipse Path
# North totality bound
Nlat = [int(i[0:2]) + float(i[3:7])/60 for i in E['NorthLatitude']]
Nlon = [-int(i[0:3]) - float(i[4:8])/60 for i in E['NorthLongitude']]
# South totality bound
Slat = [int(i[0:2]) + float(i[3:7])/60 for i in E['SouthLatitude']]
Slon = [-int(i[0:3]) - float(i[4:8])/60 for i in E['SouthLongitude']]
# Center totality bound
Clat = [int(i[0:2]) + float(i[3:7])/60 for i in E['CenterLatitude']]
Clon = [-int(i[0:3]) - float(i[4:8])/60 for i in E['CenterLongitude']]

# Draw CONUS Map
fig = plt.figure(1, figsize=[16, 4])
plt.suptitle(DATES[0])
ax1 = fig.add_subplot(131)
ax1.set_title('Operational HRRR')
m = draw_CONUS_HRRR_map()
m.drawstates()
m.drawcountries()
m.drawcoastlines()

ax2 = fig.add_subplot(132)
ax2.set_title('Experimental HRRR')
m.drawstates()
m.drawcountries()
m.drawcoastlines()

ax3 = fig.add_subplot(133)
ax3.set_title('Experimental - Operational')
m.drawstates()
m.drawcountries()
m.drawcoastlines()

Nx, Ny = m(Nlon, Nlat)
Sx, Sy = m(Slon, Slat)
Cx, Cy = m(Clon, Clat)

ax1.plot(Nx, Ny)
ax1.plot(Sx, Sy)
ax1.plot(Cx, Cy)
ax2.plot(Nx, Ny)
ax2.plot(Sx, Sy)
ax2.plot(Cx, Cy)
ax3.plot(Nx, Ny)
ax3.plot(Sx, Sy)
ax3.plot(Cx, Cy)

within = 15
is_colorbar_on = False
SAVEDIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/PhD/Eclipse20170821/'

variable = 'TMP:2 m'
variable = 'DSWRF:surface'
variable = 'WIND:10 m'
#variable = 'UVSpeed:10 m'

var_str = variable.replace(':', '_').replace(' ', '')

if variable == 'TMP:2 m':
    label = 'Temperature (C)'
    offset = 273.15
    vmin = 5; vmax = 35
    vminD = -3; vmaxD = 3
    ticks = range(vminD, vmaxD+1)
    cmap = 'Spectral_r'
elif variable == 'DSWRF:surface':
    label = r'Solar Radiation (W m$\mathregular{^{-2}}$)'
    offset = 0
    vmin = 100; vmax = 1000
    vminD = -800; vmaxD = 800
    ticks = range(vminD, vmaxD+1, 400)
    cmap = 'magma'
elif variable == 'WIND:10 m' or variable == 'UVSpeed:10 m':
    label = r'Wind Speed (ms$\mathregular{^{-1}}$)'
    offset = 0
    vmin = 0; vmax = 15
    vminD = -4; vmaxD = 4
    ticks = range(vminD, vmaxD+1)
    cmap = 'plasma'

for i in range(num):
    if DATES[i].minute != 0:
        # HRRR is only available at the top of the hour
        print 'skipping', DATES[i]
        continue
    else:
        # Plot the HRRR Data
        attime = DATES[i] 
        print DATES[i] 
        print '!', attime
        if variable == 'UVSpeed:10 m':
            uH = get_hrrr_variable(attime, variable='UGRD:10 m')
            vH = get_hrrr_variable(attime, variable='VGRD:10 m')
            uHX = get_hrrr_variable(attime, variable='UGRD:10 m', model='hrrrX', removeFile=True, value_only=True)
            vHX = get_hrrr_variable(attime, variable='VGRD:10 m', model='hrrrX', removeFile=True, value_only=True)
            H = {'lat':uH['lat'],
                 'lon':uH['lon'],
                 'value': wind_uv_to_spd(uH['value'], vH['value'])}
            HX = {'value': wind_uv_to_spd(uHX['value'], vHX['value'])}
        else:
            H = get_hrrr_variable(attime, variable=variable)
            HX = get_hrrr_variable(attime, variable=variable, model='hrrrX', removeFile=True, value_only=True)
        Hx, Hy = m(H['lon'], H['lat'])
        HRRR_plot = ax1.pcolormesh(Hx, Hy, H['value']-offset, vmin=vmin, vmax=vmax, cmap=cmap)
        HRRRx_plot = ax2.pcolormesh(Hx, Hy, HX['value']-offset, vmin=vmin, vmax=vmax, cmap=cmap)
        DIFF_plot = ax3.pcolormesh(Hx, Hy, HX['value']-H['value'], vmin=vminD, vmax=vmaxD, cmap='bwr')
        #
        #
        # Plot CONUS
        Epoint1 = ax1.scatter(Cx[i], Cy[i], c='r', s=90, zorder=500)
        Epoint2 = ax2.scatter(Cx[i], Cy[i], c='r', s=90, zorder=500)
        Epoint3 = ax3.scatter(Cx[i], Cy[i], c='r', s=90, zorder=500)
        #
        if is_colorbar_on is False:
            from mpl_toolkits.axes_grid1 import make_axes_locatable
            divider = make_axes_locatable(ax2)
            #cax = divider.append_axes('bottom', size='6%', pad=.25)
            cax = fig.add_axes([0.23, 0.08, 0.3, 0.05])
            cb = fig.colorbar(HRRR_plot, cax=cax, orientation='horizontal', extend="both")
            cb.set_label(label)
            #
            divider = make_axes_locatable(ax3)
            #cax = divider.append_axes('bottom', size='6%', pad=.25)
            cax = fig.add_axes([0.68, 0.08, 0.2, 0.05])
            cb = fig.colorbar(DIFF_plot, cax=cax, orientation='horizontal', extend="both")
            cb.set_label(r'$\Delta$ ' + label)
            cb.set_ticks(ticks)
            is_colorbar_on = True
        #
        plt.suptitle('Time (UTC): %s' % (attime))
        print '!', attime
        plt.savefig(SAVEDIR+'HRRR_'+var_str+'/HRRR_%s.png' % attime.strftime('%Y-%m-%d_%H%M'), bbox_inches='tight')
        Epoint1.remove()
        Epoint2.remove()
        Epoint3.remove()
        HRRR_plot.remove()
        HRRRx_plot.remove()
        DIFF_plot.remove()


# Create animated gifs of the files on the eclipse day
if DATES[0].day == 21:
    import os
    os.system('convert -delay 60 '+SAVEDIR+'HRRR_'+var_str+'/*2017-08-21*.png '+SAVEDIR+'HRRR_'+var_str+'/Animated.gif')


"""
H = get_hrrr_variable(attime, variable='WIND:10 m', fxx=1, removefile=False)
HX = get_hrrr_variable(attime, variable='WIND:10 m', model='hrrrX', fxx=1)
Hx, Hy = m(H['lon'], H['lat'])

plt.figure(1)
plt.title('Operational ' + str(attime) + ' WIND:10 m')
plt.pcolormesh(Hx, Hy, H['value'], vmin=0, vmax=5)
m.drawcoastlines()

plt.figure(2)
plt.title('Experimental ' + str(attime) + ' WIND:10 m')
plt.pcolormesh(Hx, Hy, HX['value'], vmin=0, vmax=5)
m.drawcoastlines()



uH = get_hrrr_variable(attime, variable='UGRD:10 m')
vH = get_hrrr_variable(attime, variable='VGRD:10 m')
uHX = get_hrrr_variable(attime, variable='UGRD:10 m', model='hrrrX', removeFile=True, value_only=True)
vHX = get_hrrr_variable(attime, variable='VGRD:10 m', model='hrrrX', removeFile=True, value_only=True)
H = {'lat':uH['lat'],
        'lon':uH['lon'],
        'value': wind_uv_to_spd(uH['value'], vH['value'])}
HX = {'value': wind_uv_to_spd(uHX['value'], vHX['value'])}
Hx, Hy = m(H['lon'], H['lat'])

plt.figure(1)
plt.title('Operational ' + str(attime) + ' Speed from U and VGRD:10 m')
plt.pcolormesh(Hx, Hy, H['value'], vmin=0, vmax=5)
m.drawcoastlines()

plt.figure(2)
plt.title('Experimental ' + str(attime) + ' Speed from U and VGRD:10 m')
plt.pcolormesh(Hx, Hy, HX['value'], vmin=0, vmax=5)
m.drawcoastlines()




grbs = pygrib.open('hrrrX.t20z.wrfsfcf00.grib2')
H = grbs[66]
lat, lon = H.latlons()
x, y = m(lon, lat)
m.drawcoastlines()
m.pcolormesh(x, y, H.values, vmin=0, vmax=15)
plt.title('hrrrX.t20z.wrfsfcf00.grib2\n' + str(H))


"""