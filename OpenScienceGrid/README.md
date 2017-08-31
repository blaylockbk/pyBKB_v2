<img src='./OSG_logo.jpg' height='200px' alt="Open Science Grid">

# Lessons Learned Using the Open Science Grid
*Brian Blaylock  
Department of Atmospheric Science  
University of Utah  
Summer/Fall 2017*

## Introduction
The [Open Science Grid](https://www.opensciencegrid.org/) (OSG) is a [High Throughput Computing](https://en.wikipedia.org/wiki/High-throughput_computing) (HTC) system. This should not be confused with High Performance Computing (HPC) systems.

I am using the system to compute statistics of HRRR data over the last 2.5 years stored in the CHPC Pando archive system. The archive is currently 35TB, and growing every day.

The OSG is most useful if your job can be written in an embarrasingly parallel way.

## OSG Limits
|Maximum Storage|Maximum Files|
|---------------|-------------| 
|   102,400 MB  |   500,000   |

When I run my statistics, I reach 600% of my allotted storage, but only 5% of my allotted number of files. As soon as I can get the files transfered to my local computing center (Utah Center for High Performance Computing), then I remove the files from the OSG.

## Specificaitons to my job
I calculate statistics from the HRRR model for the last 3 years of data that we store in an [object-storage archive](http://hrrr.chpc.utah.edu). The HRRR model covers the contiguous United States with 3 km grid spacing with a size of 1059x1799 pixels, resulting in 1.9 million grid points. There are 136 different meteorological variables with an analysis hour and 18 forecast hours. That is a lot of data that needs to be sifted through. I am focusing on the analysis hours at the moment.

The deal with using the OSG is that your jobs need to be embarrassingly parallel. Thus, I have had framed the research questions I want answered in an embarrassingly parallel framework. I am calculating 30-day statstics for all those grid points for every hour of the year, including leap year. This requires 8,784 unique jobs (365 days * 24 hours a day). This can be done in an embarassingly parallel way, where the same script can run those 8,784 jobs on different processors. With this method, I am downloading the same files multiple times, which causes some inefficiencies, but with the OSG there is not way to share data between the jobs. 

The calculated statistics include the 30-day running mean and percentiles [0, 1, 2, 3, 4, 5, 10, 25, 33, 50, 66, 75, 90, 95, 96, 97, 98, 99, 100].

The Latitude and Longitude for the grid is stored in a separate HDF5 file. There is no need to have every node return these values when they are known.

### Example
Statistics for July 1st at 00z are calculated using the 00z data for the 15 days before and after July 1st, using all the available years (2015-2017). The data values are downloaded from the HRRR archive, and stored. This requires the OSG nodes to have at least 6 MB of memory. This download process is used using all the available processors on the OSG node which reduced the download time. Numpy funcitons are then used to calculate the mean and the percentiles. Those statistics are returned in an HDF5 file along with the number of cores on the node, the time it took to calculate the statistics, and the number of data values used to calculte the statistic. If only 2 years of data are used, then there are about 60 samples. If 3 years of data are avaiale, then there are about 90 samples. I am sifting through TONS of data. Each variable for each hour is about 1MB in GRIB2 format, that is downloaded from the Pando archive.

In the future, when there are 2 or 3 years of additional HRRR data, this method of calculating statistics will require a computer with a minimum of 8 or 16GB of available memory. Computing the max, min, and mean of the data set is not memory intensive, but computing percentiles is memory intensive, because all the values need to be stored and then sorted before finding each percentile.


## File Transfer between OSG and CHPC
Data Transfer of large files is somewhat cumbersome. I use the scp command to move files form OSG to the CHPC, my home institution's computing facility. One of the downsides of producing such large files on the OSG is that the transfer rate of those files to CHPC is very slow and it takes a long time to move the bulk of files.

With each variable statistics I run on the OSG, I produce 8,784 files (one file for each hour of the year including leap year) that ammount to about 700 GB. Transfering those files one at a time can take over a day over scp. However, I am now utilizing multiprocessing to transfer those files in about 3 hours using 32 cores. I think the limiting factor of the transfer time is a function of the write speed of the disk and the bandwidth of the network.

Even with the added transfer time, transfering files from the OSG is much faster than running the statistics on my home instituion. For example, the same job at CHPC, on the wx4 node with 8 cores, took 7.5 days to complete.

## OSG Tips
The OSG appears to run faster in the early morning. Maybe less people are on it.

### Remote login
I set up SSH keys on meso4, but had trouble setting up SSH keys on Putty, so I gave up.

### Retry Failed Jobs
Sometimes, for unexplained reasons, a job doesn't finish on the OSG. I used to simply deal with this problem by re-running those scripts locally (there usually weren't more than 20 jobs that had failed). It is possible for OSG to re-run a job if it fails. Add these lines in the condor submit file: 

    ## Retry the job if it fails  
    ## Send the job to Held state on failure.  
    on_exit_hold = (ExitBySignal == True) || (ExitCode != 0) 
    
    # Periodically retry the jobs every 10 minutes,
    ## up to a maximum of 5 retries.
    periodic_release =  (NumJobStarts < 5) && ((CurrentTime - EnteredCurrentStatus) > 600)

### Singularity Image
The people at OSG created a singularity image for me to do my work in. This allows me to have pygrib installed in my python build, as well as a few other libraries. I could technically manage the sinularity image myself, but I haven't learned how to do that yet. The image as it is now does all I need it to do at the moment.

If using a singularity image, In the condor submit file, you need to specify that your job is sent to an OSG node that has singularity and you need to send the image.  
    
    +SingularityImage = "/cvmfs/singularity.opensciencegrid.org/opensciencegrid/osgvo-blaylockbk:latest/"

### A note about saving HDF5 files:
It is best to save each array on "top level" of the HDF5 file. My first iteration of creating these files I stored all my percentile calculations as a 3D array, requiring to get a slab of data to index the individual levels, i.e. file['percentile values'][0][10, 10] to get a point of data. It is much better and more efficient to grab data stored in 2D arrays, on the "top level" like my mean array is stored, i.e. file['mean'][10, 10]. With multiprocessing, I created a time series of the mean data at a point in 30 seconds, but it took 33 minutes to create a time series at a point for the percentile data!!! I'm pretty sure this is due to the added dimension of the percentile variable.

## Workflow
Since I still get errors when running on OSG, I have to do a little babysitting:
- Create condor_submit script on OSG
    - a python script helps me with this
- Submit the job on the OSG: 
    - condor_submit job.submit
- Copy the files to local CHPC storage using scp
    - Again, another python script loops through all available files
- Look for and rerun bad files
    - Some of the files returned from OSG are incomplete, so I check the file sizes of all the files and when I see one that is smaller than the rest I rerun the job locally.
- Remove files from OSG
    - These jobs produce a lot of data, over 500% of my allocation on the OSG, so I quickly remove those files.

## Data Created

|File Name  | Total Size           |Images | Transfer OSG --> CHPC | Run time on OSG |
|-----------|----------------------|-------|-----------------------|-----------------|
|TMP:2 m    | 685 GB (~82 MB/file) |8.87 GB| 6.5 hours (8 cores)   |                 |
|DPT:2 m    | 691 GB (~84 MB/file) |GB     | 2 hours (32 cores)    | 3 hours         |
|WIND:10 m  | 704 GB (~87 MB/file) |8.98 GB| 2.5 hours (32 cores)  |                 |
|REFC:entire| 335 GB (~43 MB/file  |GB     | hours (cores)         |                 |
|LatLon     | 184 MB |

## Running jobs on OSG
I have seen about over 455 jobs running simultaneously on the OSG
The total time to calculate hourly statistics on OSG takes about 3 hours. This same work would otherwise take over 7 days if I ran this on one node at CHPC.

### Example
To give you an idea of the speed of computing on OSG, I have a job that would take about 2 hours to run on the meso4 server, which has 32 processors, and created 288 ~65MB files. In comparison, I submitted the same job to the OSG, which ran in about 15 minutes. The difference is that I ran the 288 jobs on meso4 in serial, whereas I ran the 288 jobs simultaneously on the OSG, each with between 8-48 processors,as soon as the computing resources become available. If you don't account for the time in the queue waiting for resources to become available, it takes less than one minute (typically between 10-60 seconds with an average time of 30 seconds) to complete the computations on the 8,000+ cores. The trade off is in the transfer time...transferring the files from the compute node (farmed out somewhere in the United States) to my OSG home directory, and then from the OSG home directory to meso4 via scp. The transfer of files from OSG to meso4 can take up to 24 minutes if done in serial (about 4-5 seconds per file, and need to transfer 288 files).

## Useful CONDOR commands
- Submit a job: `condor_submit name_of_job_file.submit`
- View your jobs in the queue: `condor_q`
- View your Jobs (auto update): `watch condor_q` ctr-z to exit
- View individual jobs: `condor_q blaylockbk -nobatch`
- View a usuer's jobs: `condor_q blaylockbk`
- Remove a job: `condor_rm 1234567890`

The queue looks different whether you are in the normal command prompt, or if you have loaded a singularity image. I find that the queue within the singularity image is filled with someone else submitting jobs. Jobs I've submitted get through the queue really quick in the normal command prompt (when I'm not in the singularity image).

## History of Statistics Work
My first attempt calculated the hourly statistics for each month, a job that could be done in 288 parts (12 months * 24 hours). This method gave me about 60-90 samples for each hour (60 samples if two years are available, or 90 samples if three years are available). This produced much less data, but a timeseries of the data was not continous. Each month was a unquie statistic. It is much better to calculate the 30-day running statistics where each hour is a unique statistic.

I didn't calculate as many statistics as I had before, only computing the mean, max, min and [1, 5, 10, 90, 95, 99] percentiles. 

I origianally stored the statistics data in NetCDF files, but these filese were so bloated it would have been too much data to store in memory. I used compression level=1 which reduced a 180 MB file to a 65 MB file. I later changed to HDF5 which has reduced the file sizes substantially. This was a smart move especially after I doubled the number of calculated statistics. The file size as HDF5 with the 20 statistics was about the same size as the NetCDF file with the 9 statistics.

# Post Processing
## Plot Maps
A map of the statistical data

## Time Series
It is much more efficient to store each statistical value as a key in the HDF5 file. My original method was to store the calculated percentiles as a 3D array, but that wasn't efficient to pluck values from. Using the 32 cores on meso4, I could create a time series from a point in 30 seconds with my new HDF5 storage order, whereas before with the 3D array it took 33 minutes to generate the same timeseries!

### List generation using multiprocessing
I can generate a time series from a point in about 2-3 seconds using 32 cores

    import h5py
    import multiprocessing
    variable = 'TMP_2_m'
    DIR = '/uufs/chpc.utah.edu/common/home/horel-group2/blaylock/HRRR_OSG/daily30_20150418-20170801/%s/' % (variable)
    months = range(1,13)
    days = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    hours = range(24)

    def get_point_MP(inputs):
        FILE, STAT, ROW, COL = inputs
        with h5py.File(FILE, 'r') as f:
            return f[STAT][ROW][COL]

    ROW = 10
    COL = 10
    STAT = 'mean'
    args = [[DIR+'OSG_HRRR_%s_m%02d_d%02d_h%02d_f00.h5' % \
            (variable, month, day, hour), STAT, ROW, COL] \
            for month in months for day in range(1,days[month-1]+1) for hour in hours]
    num_proc = multiprocessing.cpu_count()
    p = multiprocessing.Pool(num_proc)
    HTS = p.map(get_point_MP, args) 
    p.close()
    # HTS is the 'HRRR-statistic time series'

### List Comprehension
The time series can be generated on a single processer. The speed of these list comprehensions varies. Sometimes it takes 10 minutes, other times it take as little as one minute. I'm not sure the reasoning.
    
    import h5py
    variable = 'TMP_2_m'
    DIR = '/uufs/chpc.utah.edu/common/home/horel-group2/blaylock/HRRR_OSG/daily30_20150418-20170801/%s/' % (variable)
    months = range(1,13)
    days = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    hours = range(24)

    def get_point(FILE, STAT, ROW, COL):
        with h5py.File(FILE, 'r') as f:
            return f[STAT][ROW][COL]

    # Pluck the value at point (10, 10)
    ROW = 10
    COL = 10
    STAT = 'mean'
    HTS = [get_point(DIR+'OSG_HRRR_%s_m%02d_d%02d_h%02d_f00.h5' % \
           (variable, month, day, hour), STAT, ROW, COL) \
           for month in months for day in range(1,days[month-1]+1) for hour in hours]
    # HTS is the 'HRRR-statistic Time Series'

-----------
-----------
# Old discussion of first attempt statistics

(Old example images of hourly by month)

Note: the graphs shouldn't be interpreted as a continuum. Each month is independent from one another. This explains the steep steps in a value from month to month. These steps from month to month are caused because the maximums are the month maximum. For example, the maximum on the 23rd hour in May and the 0th hour in June are very different. This is because the maximum in May may be on on May 30th, while the maximum in June may be on June 30th. Thus, the line representing the maximum of each hour in each month cannot be considered a continuous.

Because I only have 2.5 years of data, a loop showing a map of the maximum or minimum values appears to show features of two underlying weather features move around the map. These are caused by the extreme events for the day

Python multiprocessing is easy to utilize, but doesn't really gain me any ground for what I'm doing. Primarily, multiprocessing is used to speed up the downloads, but it doesn't appear it makes much difference in the compute time. Below shows a scatter plot for 288 files of the number of cores used in the computation in relation to the number of seconds it took to complete the computations. Something to keep in mind is that some of these are calculating statistics for a high sample size, while some are calculating for a fewer sample size.

Images
num of cores/compute time

number of samples/compute time

each data point/number of samples

point time series

point time series with mesowest observations
