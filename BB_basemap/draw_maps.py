# Brian Blaylock
# Version 2 update

"""
Draw Basemaps
"""

def draw_world_map():
    """
    Draw a custom basemap
    """
    ## Draw Background basemap
    bot_left_lat = -90
    bot_left_lon = 0
    top_right_lat = 90
    top_right_lon = 360

    ## Map in cylindrical projection (data points may apear skewed)
    m = Basemap(resolution='l', projection='cyl', \
        llcrnrlon=bot_left_lon, llcrnrlat=bot_left_lat, \
        urcrnrlon=top_right_lon, urcrnrlat=top_right_lat)
    return m


def draw_utah_map():
    """
    Draw a custom basemap
    """
    ## Draw Background basemap
    bot_left_lat  =36.5
    bot_left_lon  =-114.5
    top_right_lat =42.5
    top_right_lon = -108.5

    ## Map in cylindrical projection (data points may apear skewed)
    m = Basemap(resolution='l', projection='cyl', \
        llcrnrlon=bot_left_lon, llcrnrlat=bot_left_lat, \
        urcrnrlon=top_right_lon, urcrnrlat=top_right_lat)
    return m