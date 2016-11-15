# Brian Blaylock
# Version 2 update
# 14 November 2016

"""
Collection of funcitons for manipulating gridded data.
"""

import numpy as np


def pluck_point(stn_lat, stn_lon, grid_lat, grid_lon):
    """
    From the grid, get the data for the point nearest the MesoWest station
    Figure out the nearest lat/lon in the HRRR domain for the station location
    Input:
        stn_lat, stn_lon - The latitude and longitude of the station
        grid_lat, grid_lon - The 2D arrays for both latitude and longitude
    Output:
        The index of the flattened array
    """

    abslat = np.abs(grid_lat-stn_lat)
    abslon = np.abs(grid_lon-stn_lon)

    # Element-wise maxima. (Plot this with pcolormesh to see what I've done.)
    c = np.maximum(abslon, abslat)

    # The index of the minimum maxima (which is the nearest lat/lon)
    latlon_idx = np.argmin(c)

    return latlon_idx


def cut_data(bl_lat, tr_lat, bl_lon, tr_lon, lat, lon, buff=0):
    """
    If you want to cut down a data for domain for faster plotting, this
    will give you the max and min latitude and longitude position indexes
    for an array.

    Input: the bottom left corner and top right corner lat/lon coordinates
        bl_lat - bottom left latitude
        tr_lat - top right latitude
        bl_lon - bottom left longitude
        tr_lon - top right longitude
        buff   - a buffer in case the domain is skewed resulting in blank spots
                 on the map plot.
    Return: the max and min of each the arrays x and y coordinates
    """

    lat_limit = np.logical_and(lat > bl_lat, lat < tr_lat)
    lon_limit = np.logical_and(lon > bl_lon, lon < tr_lon)

    total_limit = np.logical_and(lat_limit, lon_limit)

    xmin = np.min(np.where(total_limit)[0]) - buff
    xmax = np.max(np.where(total_limit)[0]) + buff
    ymin = np.min(np.where(total_limit)[1]) - buff
    ymax = np.max(np.where(total_limit)[1]) + buff

    return xmin, xmax, ymin, ymax


"""
# April 7, 2016
# Two functions to conver V and U staggered grids to mass points.
# For example:
# Usefull to convert U winds, XLAT_U, and XLONG_U, to a mass point
# using basic averaging between the left and right side of the grid point.
"""

def Vstagger_to_mass(V):
    """
    V are the data on the top and bottom of a grid box
    A simple conversion of the V stagger grid to the mass points.
    Calculates the average of the top and bottom value of a grid box. Looping
    over all rows reduces the staggered grid to the same dimensions as the
    mass point.
    Useful for converting V, XLAT_V, and XLONG_V to masspoints
    Differnce between XLAT_V and XLAT is usually small, on order of 10e-5

    (row_j1+row_j2)/2 = masspoint_inrow

    Input:
        Vgrid with size (##+1, ##)
    Output:
        V on mass points with size (##,##)
    """
    # Create the first column manually to initialize the array with correct
    # dimensions. Average of first and second column.
    V_masspoint = (V[0, :] + V[1, :]) / 2.
    # We want one less row than we have
    V_num_rows = int(V.shape[0]) - 1

    # Loop through the rest of the rows. We want the same number of rows as we
    # have columns. Take the first and second row, average them, and store in
    # first row in V_masspoint.
    for row in range(1, V_num_rows):
        row_avg = (V[row, :]+V[row+1, :]) / 2.
        # Stack those onto the previous for the final array
        V_masspoint = np.row_stack([V_masspoint, row_avg])

    return V_masspoint


def Ustagger_to_mass(U):
    """
    U are the data on the left and right of a grid box.
    A simple conversion of the U stagger grid to the mass points.
    Calculates the average of the left and right value of a grid box. Looping
    over all columns it reduces the staggered grid to the same dimensions as
    the mass point.
    Useful for converting U, XLAT_U, and XLONG_U to masspoints
    Differnce between XLAT_U and XLAT is usually small, on order of 10e-5

    (column_j1+column_j2)/2 = masspoint_incolumn

    Input:
        Ugrid with size (##, ##+1)
    Output:
        U on mass points with size (##,##)

    """

    # Create the first column manually to initialize the array with correct
    # dimensions. Average the first and second row.
    U_masspoint = (U[:, 0]+U[:, 1])/2.
    # We want one less column than we have
    U_num_cols = int(U.shape[1])-1

    # Loop through the rest of the columns
    # We want the same number of columns as we have rows.
    # Take the first and second column, average them, and store in first column in U_masspoint
    for col in range(1, U_num_cols):
        col_avg = (U[:, col] + U[:, col+1]) / 2.
        # Stack those onto the previous for the final array
        U_masspoint = np.column_stack([U_masspoint, col_avg])

    return U_masspoint


# --- Examples ----------------------------------------------------------------
if __name__=="__main__":
    V = np.array([[1, 2, 3],
                  [4, 5, 6],
                  [7, 8, 9],
                  [1, 2, 3]])
    print V
    a = Vstagger_to_mass(V)
    print a

    print ""

    U = np.array([[1, 2, 3, 4],
                  [4, 5, 6, 7],
                  [7, 8, 9, 10]])
    print U
    b = Ustagger_to_mass(U)
    print b
