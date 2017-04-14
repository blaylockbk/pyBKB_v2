# Terminal Doppler Weather Radar (TDWR)

Python tools for download TDWR data and and plotting it on a map

## `download_TDWR_from_URL.py`
Terminal Doppler Weather Radar - SLC
 lat:  40.97
 lon:-111.93

downloaded from
http://thredds.ucar.edu/thredds/catalog/terminal/level3/catalog.html

As an example, this is the HTTP server URL you can download from
http://thredds.ucar.edu/thredds/fileServer/terminal/level3/TV0/SLC/20160123/Level3_SLC_TV0_20160123_2359.nids

Catalog: browse the availalbe data here
http://thredds.ucar.edu/thredds/catalog/terminal/level3/TV0/SLC/catalog.html


TV0/Base Velocity Tilt 1 (knots)
TV1/Base Velocity Tilt 2 (knots)
TV2/Base Velocity Tilt 3 (knots)
TR0/Base Reflectivity Tilt 1 (dbz)
TR1/Base Reflectivity Tilt 2 (dbz)
TR2/Base Reflectivity Tilt 3 (dbz)
NCR/Composite Reflectivity

## Plotting
Requires metpy package. I think the newest version should work, but my special download, MetPy_BB, found one directory up, has what you need.