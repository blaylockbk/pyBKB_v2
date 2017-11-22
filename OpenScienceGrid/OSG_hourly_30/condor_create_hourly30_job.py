# Brian Blaylock
# August 29, 2017                  Rachel is in Scotland today visitng a castle

"""
Create a script to submit many jobs to the OSG
Daily job by hour
"""

# Open the file
f = open('job_daily30.submit', 'w')

# Write some intro lines
f.write("""Universe = vanilla
Requirements = HAS_SINGULARITY == True
request_memory = 6 GB
+SingularityImage = "/cvmfs/singularity.opensciencegrid.org/opensciencegrid/osgvo-blaylockbk:latest/"
Executable = OSG_HRRR_run_this.sh
Error = log/job.err.$(Cluster)-$(Process)
Output = log/job.out.$(Cluster)-$(Process)
Log = log/job.log.$(Cluster)
ShouldTransferFiles = YES
when_to_transfer_output = ON_EXIT

### Retry the job if it fails
# Send the job to Held state on failure.
on_exit_hold = (ExitBySignal == True) || (ExitCode != 0)

# Periodically retry the jobs every 10 minutes, up to a maximum of 5 retries.
periodic_release =  (NumJobStarts < 5) && ((CurrentTime - EnteredCurrentStatus) > 600)
""")

# Write the arguments and queue
#for variable in ['TMP:2_m', 'DPT:2_m', 'Wind:10_m', 'GUST:surface', 'REFC:entire']:
var = 'TMP:2 m'
fxx = 0
months = range(1,13)
days = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
hours = range(24)

args = [[var, month, day, hour, fxx] for month in months for day in range(1,days[month-1]+1) for hour in hours]
for i in args:
    var, month, day, hour, fxx = i
    f.write("""
Arguments = %s %s %s %s %s
transfer_input_files = OSG_HRRR_composite_daily30.py, HRRR_S3.py
Queue 1
""" % (var.replace(' ', '_'), month, day, hour, fxx))

f.close()