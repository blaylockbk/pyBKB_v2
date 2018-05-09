# Brian Blaylock
# May 2, 2018

import numpy as np
import matplotlib.colors as colors

"""
Standardized colormaps from National Weather Service

source: OneDrive/02_Horel_Group/NWS Standard Color Curve Summary.pdf
"""

def cm_precip():
    """
    Inches:
        vmax=30, vmin=0
    millimeters:
        vmax=762, vmin=0
    """
    # normalized value, in inches
    a = np.array([0,.01,.1,.25,.5,1,1.5,2,3,4,6,8,10,15,20,30])/30.
    COLORS = [(a[0], np.array([255,255,255])/255.),
              (a[1], np.array([199,233,192])/255.),
              (a[2], np.array([161,217,155])/255.),
              (a[3], np.array([116,196,118])/255.),
              (a[4], np.array([49,163,83])/255.),
              (a[5], np.array([0,109,44])/255.),
              (a[6], np.array([255,250,138])/255.),
              (a[7], np.array([255,204,79])/255.),
              (a[8], np.array([254,141,60])/255.),
              (a[9], np.array([252,78,42])/255.),
              (a[10], np.array([214,26,28])/255.),
              (a[11], np.array([173,0,38])/255.),
              (a[12], np.array([112,0,38])/255.),
              (a[13], np.array([59,0,48])/255.),
              (a[14], np.array([76,0,115])/255.),
              (a[15], np.array([255,219,255])/255.)]

    cmap = colors.LinearSegmentedColormap.from_list("Precip", COLORS)

    return cmap

def cm_temp():
    """
    F:
        vmax=120, vmin=-60
    C:
        vmax=45, vmin=-50
    """
    a = range(-60,121,5)
    norm = [(float(i)-min(a))/(max(a)-min(a)) for i in a]

    C = np.array([[145,0,63],
                  [206,18,86],
                  [231,41,138],
                  [223,101,176],
                  [255,115,223],
                  [255,190,232],
                  [255,255,255],
                  [218,218,235],
                  [188,189,220],
                  [158,154,200],
                  [117,107,177],
                  [84,39,143],
                  [13,0,125],
                  [13,61,156],
                  [0,102,194],
                  [41,158,255], 
                  [74,199,255], 
                  [115,215,255], 
                  [173,255,255],
                  [48,207,194], 
                  [0,153,150], 
                  [18,87,87],
                  [6,109,44],
                  [49,163,84],
                  [116,196,118],
                  [161,217,155],
                  [211,255,190],  
                  [255,255,179], 
                  [255,237,160], 
                  [254,209,118], 
                  [254,174,42], 
                  [253,141,60], 
                  [252,78,42], 
                  [227,26,28], 
                  [177,0,38], 
                  [128,0,38], 
                  [89,0,66], 
                  [40,0,40]])/255.
        
    COLORS = []
    for i, n in enumerate(norm):
        COLORS.append((n, C[i]))

    cmap = colors.LinearSegmentedColormap.from_list("temperature", COLORS)

    return cmap

def cm_wind():
    """
    MPH: vmin=0, vmax=140
    m/s: vmin=0, vmax=60
    """
    a = [0,5,10,15,20,25,30,35,40,45,50,60,70,80,100,120,140]
    norm = [(float(i)-min(a))/(max(a)-min(a)) for i in a]
    C = np.array([[16,63,120],
                  [34,94,168],
                  [29,145,192],
                  [65,182,196],
                  [127,205,187],
                  [180,215,158],
                  [223,255,158],
                  [255,255,166],
                  [255,232,115],
                  [255,196,0],
                  [255,170,0],
                  [255,89,0],
                  [255,0,0],
                  [168,0,0],
                  [110,0,0],
                  [255,190,232],
                  [255,115,223]])
    COLORS = []
    for i, n in enumerate(norm):
        COLORS.append((n, np.array(C[i])/255.))

    cmap = colors.LinearSegmentedColormap.from_list("wind", COLORS)

    return cmap










    