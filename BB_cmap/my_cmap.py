# My Colormaps (for when I don't like any of the others)

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
'''
# Each color has a list of (x,y0,y1) tuples, where
# x defines the "index" in the colormap (range 0..1), y0 is the
# color value (0..1) left of x, and y1 the color value right of x.

# Example:
cdict = {'red': ((0.0, 0.0, 0.0),
                 (0.5, 1.0, 0.7),
                 (1.0, 1.0, 1.0)),
         'green': ((0.0, 0.0, 0.0),
                   (0.5, 1.0, 0.0),
                   (1.0, 1.0, 1.0)),
         'blue': ((0.0, 0.0, 0.0),
                  (0.5, 1.0, 0.0),
                  (1.0, 0.5, 1.0))}

my_cmap = matplotlib.colors.LinearSegmentedColormap('my_colormap', cdict, 256)

plt.pcolormesh(np.random.random([5,5]), cmap=my_cmap)
plt.colorbar()

'''
# Wind Gusts (similar to College of Dupage HRRR map)
def cmap_gust():
    num_sections = 4
    sections = np.linspace(0, 1, num_sections)
    cdict = {'red': ((sections[0], 1.0, 1.0),
                    (sections[1], 75/256., 75/256.),
                    (sections[2], 134/256., 134/256.),
                    (sections[3], 184/256., 184/256.)),
            'green': ((sections[0], 1.0, 1.0),
                    (sections[1], 132/256., 132/256.),
                    (sections[2], 1/256., 1/256.),
                    (sections[3], 134/256., 134/256.)),
            'blue': ((sections[0], 1.0, 1.0),
                    (sections[1], 181/256., 181/256.),
                    (sections[2], 124/256., 124/256.),
                    (sections[3], 11/256., 11/256.))}
    cmap_gusts = matplotlib.colors.LinearSegmentedColormap('gust_colormap_COD', cdict, 256)
    return cmap_gusts
    
'''
plt.pcolormesh(np.random.random([5,5]), cmap=cmap_gust())
plt.colorbar()
'''
