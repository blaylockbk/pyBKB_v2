# Brian Blaylock
# August 14, 2017                   I need to buy a French Door for the house

"""
Create a script to submit many jobs to the OSG
Daily job by hour
"""

# Open the file
f = open('job_hourlybymonth.submit', 'w')

# Write some intro lines
f.write("""Universe = vanilla
Requirements = HAS_SINGULARITY == True
request_memory = 4 GB
+SingularityImage = "/cvmfs/singularity.opensciencegrid.org/opensciencegrid/osgvo-blaylockbk:latest/"
Executable = OSG_HRRR_run_this.sh
Error = log/job.err.$(Cluster)-$(Process)
Output = log/job.out.$(Cluster)-$(Process)
Log = log/job.log.$(Cluster)
ShouldTransferFiles = YES
when_to_transfer_output = ON_EXIT
""")

# Write the arguments and queue
for variable in ['TMP:2_m', 'DPT:2_m', 'Wind:10_m', 'GUST:surface', 'REFC:entire']:
    for fxx in range(0, 1):
        for month in range(1, 13):
            day in range(1,32):
                for hour in range(0, 1):
                    f.write("""
Arguments = %s %s %s %s %s
transfer_input_files = OSG_HRRR_composite_hourlybymonth.py, HRRR_S3.py
Queue 1
""" % (variable, month, day, hour, fxx))

f.close()