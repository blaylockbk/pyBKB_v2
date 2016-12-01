# Brian Blaylock
# Version 2 update

"""
Draw Basemaps
"""
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap


def draw_world_map(res='i'):
    """
    Draw a custom basemap

    Can define the resolution of the map with res argument:
        'c' - crude
        'l' - low
        'i' - intermediate
        'h' - high
        'f' - full
    """
    ## Draw Background basemap
    bot_left_lat = -90
    bot_left_lon = 0
    top_right_lat = 90
    top_right_lon = 360

    ## Map in cylindrical projection (data points may apear skewed)
    m = Basemap(resolution=res, projection='cyl', \
        llcrnrlon=bot_left_lon, llcrnrlat=bot_left_lat, \
        urcrnrlon=top_right_lon, urcrnrlat=top_right_lat)
    return m


def draw_utah_map(res='i'):
    """
    Draw a custom basemap
    """
    ## Draw Background basemap
    bot_left_lat  =36.5
    bot_left_lon  =-114.5
    top_right_lat =42.5
    top_right_lon = -108.5

    ## Map in cylindrical projection (data points may apear skewed)
    m = Basemap(resolution=res, projection='cyl', \
        llcrnrlon=bot_left_lon, llcrnrlat=bot_left_lat, \
        urcrnrlon=top_right_lon, urcrnrlat=top_right_lat)
    return m


def draw_GSL_map(res='i'):
    """
    Draw a custom basemap for Great Salt Lake
    """
    ## Draw Background basemap
    bot_left_lat  = 40.5
    bot_left_lon  = -113.25
    top_right_lat = 41.9
    top_right_lon = -111.75

    ## Map in cylindrical projection (data points may apear skewed)
    m = Basemap(resolution=res, projection='cyl', \
        llcrnrlon=bot_left_lon, llcrnrlat=bot_left_lat, \
        urcrnrlon=top_right_lon, urcrnrlat=top_right_lat)
    return m

def draw_GSL2_map(res='i'):
    """
    Draw a custom basemap for Great Salt Lake
    Domain extends out to BFLAT station 
    """
    ## Draw Background basemap
    bot_left_lat  = 40.5
    bot_left_lon  = -114.1
    top_right_lat = 41.9
    top_right_lon = -111.75

    ## Map in cylindrical projection (data points may apear skewed)
    m = Basemap(resolution=res, projection='cyl', \
        llcrnrlon=bot_left_lon, llcrnrlat=bot_left_lat, \
        urcrnrlon=top_right_lon, urcrnrlat=top_right_lat)
    return m


def draw_UtahLake_map(res='i'):
    """
    Draw a custom basemap for Utah Lake
    """
    ## Draw Background basemap
    bot_left_lat  = 40.
    bot_left_lon  = -111.95
    top_right_lat = 40.38
    top_right_lon = -111.65

    ## Map in cylindrical projection (data points may apear skewed)
    m = Basemap(resolution=res, projection='cyl', \
        llcrnrlon=bot_left_lon, llcrnrlat=bot_left_lat, \
        urcrnrlon=top_right_lon, urcrnrlat=top_right_lat)
    return m



if __name__ == "__main__":

    m = draw_utah_map()

    # Examples of drawing other things on a map

    # Drawing ArcGIS Basemap
    # Examples of what each map looks like can be found here:
    # http://kbkb-wx-python.blogspot.com/2016/04/python-basemap-background-image-from.html
    maps = ['ESRI_Imagery_World_2D',    # 0
            'ESRI_StreetMap_World_2D',  # 1
            'NatGeo_World_Map',         # 2
            'NGS_Topo_US_2D',           # 3
            'Ocean_Basemap',            # 4
            'USA_Topo_Maps',            # 5
            'World_Imagery',            # 6
            'World_Physical_Map',       # 7
            'World_Shaded_Relief',      # 8
            'World_Street_Map',         # 9
            'World_Terrain_Base',       # 10
            'World_Topo_Map'            # 11
           ]
    m.arcgisimage(service=maps[8], xpixels=1000, verbose=False)


    # Draw various map boundaries
    m.drawcoastlines()
    m.drawcounties()
    m.drawstates()

    plt.show(block=False)
    