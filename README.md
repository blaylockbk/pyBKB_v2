# pyBKB_v2
Python scripts created and used by [Brian K. Blaylock](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/home.html)


Version 2: This code is being updated and cleaned up regularly, as opposed to 
the first version.

|Directory | Purpose |
|--------|------------------------|
|BB_ASN  | For getting data from MesoWest Above Surface Network|
|BB_HRRR | For raw handling HRRR data |
|BB_MesoWest | For grabbing data from the MesoWest API|
|BB_WRF | For handling WRF output data|
|BB_basemap | Draws various basemaps I use often|
|BB_cmap | Various color maps|
|BB_data | For handling various data types|
|BB_downloads | Scripts to download various data sets or images|
|BB_mplstyle | Matplotlib styling for publication|
|BB_rose | Creating wind and pollution roses |
|BB_skewt| Plotting SkewT|
|BB_special | Special and misc. functions |
|BB_wx_calcs | Various weather related calculations|
|MetPy_BB | An older version of MetPy with a fix for reading TDWR data|
|TDWR| Code for downloading and plotting TDWR data


# Code Snippets, and "Convention"
## Color maps
My personal color map convention and preferences.
Read this article before using python colormaps: http://matplotlib.org/users/colormaps.html
|Variable          | Code                   | Suggested Range|
|------------------|------------------------|---|
|Air Temperature   | `cmap='Spectral_r'`    |
|Dew Point         | `cmap='BrBG'`          |   |
|Relative Humidity | `cmap='BrBG'`          | [0, 100] %|
|Sea Level Pressure|`cmap='viridis'`        |[976, 1040] hPa|
|Wind Gust         |`from BB_cmap.my_cmap import cmap_gust` 
|                  |`cmap=cmap_gust()`|[0, 35] m/s|
|Terrain           |`from BB_cmap.terrain_colormap import terrain_cmap_256()`
|                  |`cmap=terrain_cmap_256()`||
|Reflectivity      |`from MetPy_BB.plots import ctables`
|                  |`ctable = 'NWSReflectivity'`
|                  |`norm, cmap = ctables.registry.get_with_steps(ctable, -0, 5)`
|                  |`m.pcolormesh(x, y, ref, norm=norm, cmap=cmap)`||

## HRRR Variable names
Commonly used HRRR variable names needed for indexing 
|Variable             | HRRR code |
|---------------------|-----------|
|2 m Temperature      | `TMP:2 m` |
|2 m RH               | `RH:2 m`  |
|10 m Wind Speed (max)| `WIND:10 m`|
|10 m Wind Gust       | `GUST:surface`|
|Sea Level Pressure   | `MSLMA:mean sea level`|
|Topography           | `HGT:surface`|
