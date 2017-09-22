Brian Blaylock  
September 7, 2017
# Download GOES-16 data

You can download GOES-16 data from the Amazon Cloud. This is a public dataset, so you shouldn't need access keys to download the data.

Files from the Advanced Baseline Imager (ABI):
- ABI Level 1b Radiances
    - `ABI-L1b-RadC`: CONUS
    - `ABI-L1b-RadF`: Full Disk
    - `ABI-L1b-RadM`: MesoScale
- ABI Level 2 Cloud and Moisture Imagery
    - `ABI-L2-CMIPC`: CONUS
    - `ABI-L2-CMIPF`: Full Disk
    - `ABI-L2-CMIPM`: Mesoscale
- ABI Level 2 Cloud and Moisture Imagery: Multi-Band Format
    - `ABI-L2-MCMIPC`: CONUS
    - `ABI-L2-MCMIPF`: Full Disk
    - `ABI-L2-MCMIPM`: Mesoscale


## Bucket: `noaa-goes16`




---------------
To understand how to use the pyproj python module you need to look at the proj documentation
https://github.com/OSGeo/proj.4


# GOES-16 Geostationary Projection
In python's Basemap, this is also `projection='geos'`



GOES-16 is in _Geostationary projection_  
http://proj4.org/projections/geos.html

load the netcdf file

    from netCDF4 import Dataset
    nc = Dataset(file_path, 'r')

Details on the projection:

    nc.variables['goes_imager_projection']

Options:
- +proj = projection type
    - `geos`
- +h = height of the satellite
    - `nc.variables['goes_imager_projection'].perspective_point_height`
    - `35786023.0`
- +lon_0 = subsatellite longitude point
    - `nc.variables['goes_imager_projection'].longitude_of_projection_origin`
    - `-89.5`
- +lat_0 = subsatellite latitude point
    - `nc.variables['goes_imager_projection'].latitude_of_projection_origin`
    - `0.0`
- +sweep = sweep angle axis. GOES uses a x sweep.
    - `nc.variables['goes_imager_projection'].sweep_angle_axis`
    - `x`
- +a = semi major axis
    - `nc.variables['goes_imager_projection'].semi_major_axis`
- +b = semi minor axis
    - `nc.variables['goes_imager_projection'].semi_minor_axis`
The projection corrdinate = scan_angle (radians) * height



# Lambert Conformal Conic projection of HRRR model
In python's Basemap, this is `projection='lcc'`

Options:
- +proj = projection type
    - `lcc`
- +lon_0 = center longitude
    - `-97.5`
- +lat_0 = latitude of 1st standard parallel
    - `38.5`
- +lat_1 = latitude of 2nd standard parallel
    - `38.5`
- +lat_0 = latitude of origin
    - `38.5`

# Equidistant Cylindrical
In python's Basemap, this is `projection='cyl'`

- +proj = projection type
    - `eqc`
- +lat_ts = latitude of true scale, defaults to 0.0
- +lat_0 = center of map
    - `97.5` for the HRRR model



+no_defs = Don't use the defaults file
+datum = Datum name
+ellps = Ellipsoid name




from pyproj import Proj
p = Proj(proj='geos', h='35786023.0', lon_0='-89.5', sweep='x')

X_proj_coor = (FD.variables['x'][:]+FD.variables['x'].add_offset) * 35786023.0

Y_proj_coor = (FD.variables['y'][:]+FD.variables['y'].add_offset) * 35786023.0

x, y = p(X_proj_coor, Y_proj_coor)

X_proj_coor = FD.variables['x'][:] * 35786023.0

Y_proj_coor = FD.variables['y'][:] * 35786023.0