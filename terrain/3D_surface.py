# Brian Blaylock
# July 11, 2017                    Umm, I think I'm getting married in October

"""
Hovemoller for two weeks prior to a fire, with bias and RMS errors calculated
for each forecast hour against the analysis hour.
"""
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D

#mpl.use('Agg')#required for the CRON job. Says "do not open plot in a window"??
import numpy as np
from datetime import datetime, timedelta
import matplotlib as mpl
import matplotlib.pyplot as plt

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
from BB_downloads.HRRR_S3 import get_hrrr_variable, hrrr_subset

## Reset the defaults (see more here: http://matplotlib.org/users/customizing.html)
mpl.rcParams['figure.figsize'] = [15, 12]        #[15, 6]
mpl.rcParams['figure.titlesize'] = 15
mpl.rcParams['figure.titleweight'] = 'bold'
mpl.rcParams['xtick.labelsize'] = 10
mpl.rcParams['ytick.labelsize'] = 10
mpl.rcParams['axes.labelsize'] = 10
mpl.rcParams['axes.titlesize'] = 12
mpl.rcParams['lines.linewidth'] = 1.8
mpl.rcParams['grid.linewidth'] = .25
mpl.rcParams['figure.subplot.wspace'] = 0.05
mpl.rcParams['figure.subplot.hspace'] = 0.18     #0.01
mpl.rcParams['legend.fontsize'] = 8
mpl.rcParams['legend.framealpha'] = .75
mpl.rcParams['legend.loc'] = 'best'
mpl.rcParams['savefig.bbox'] = 'tight'
mpl.rcParams['savefig.dpi'] = 100
mpl.rcParams['savefig.transparent'] = False

print "\n--------------------------------------------------------"
print "  Working on the HRRR 3D surface (%s)" % sys.argv[0]
print "--------------------------------------------------------\n"

#==============================================================================


# Directory to save figures (subdirectory will be created for each stnID)
SAVE_dir = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/PhD/HRRR/'

#==============================================================================

# Get Terrain Data from HRRR
DATE = datetime(2017, 6, 25)
variable = 'HGT:surface'
topo = get_hrrr_variable(DATE, variable)

topo = hrrr_subset(topo, half_box=40)

# Make 3D projection plot
fig = plt.figure()
ax = fig.gca(projection='3d')

# Plot the surface.
surf = ax.plot_surface(topo['lon'][50:100,50:100], topo['lat'][50:100,50:100], topo['value'][50:100,50:100],
                       cmap='terrain',
                       linewidth=0, antialiased=False)

# Add a color bar which maps values to colors.
fig.colorbar(surf, shrink=0.5, aspect=5)

plt.show()
