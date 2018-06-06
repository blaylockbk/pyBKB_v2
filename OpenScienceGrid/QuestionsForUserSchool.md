<img src='./OSG_logo.jpg' width='200px' align=right>

Brian Blaylock  
Madison, Wisconsin  
July 9-13, 2018
# Open Science Grid User School 2018
  
## Potential Project Ideas

What questions can be answered using the Open Science Grid and 2 years of HRRR model forecasts and GOES-16 ABI and GLM data.

1. **HRRR Analysis (f00) Empirical Cumulative Distribution**  
Compute empirical cumulative distribution from aggregated model analyses for every hour of the year using a 30-day window. With this new data set, we can identify typical and atypical atmospheric conditions, relative to the HRRR model, for present and past HRRR forecasts.
(Paper submitted to JTECH)

2. **HRRR Native Grid sounding extractor**  
We would like to create soundings for HRRR forecasts at select points near wildfires (or all model grid points) using the HRRR native grid output files. To do this, we would need to:
    1. Identify locations of current wildfires
    2. Download the HRRR native grid forecasts for all levels (each worker works on a separate forecast hour)
    3. Pluck the Temperature, Specific Humidity, and U/V wind components for the points of interest (or all grid points).
    4. Save the data in an HDF5 file.

3. **HRRR Wind Roses at every point**  
This can be done quickly with a DAGMan to reduce the count 

## Questions
- How _real time_ can we run stuff on OSG?
- What is best method for returning output data to home institution?


