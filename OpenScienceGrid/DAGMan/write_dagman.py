# Brian Blaylock
# August 29, 2017                  Rachel is in Scotland today visitng a castle

"""
Create a DAGMan to submit many jobs to the OSG
Daily job by hour

DAGMan File structure:
    JOB <job_id> <submit_file>
    VARS <job_id> <space_separated_list_of_variables>
    RETRY <job_id> 10
"""


var = 'DPT:2 m'
fxx = 0
months = range(1, 13)
days = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
hours = range(24)

args = [[var, month, day, hour, fxx]
        for month in months
        for day in range(1, days[month - 1] + 1)
        for hour in hours]

osg_script = "../daily_30/OSG_HRRR_composite_daily30.py"
hrrr_script = "../daily_30/HRRR_S3.py"

with open("splice_dag.dag", "w") as f:
    for i, (var, month, day, hour, fxx) in enumerate(args):
        var_id = var.replace(':', '_').replace(' ', '_')
        f.write("JOB %s.%s %s\n" % (var_id, i, "dagman.submit"))
        f.write(("VARS %s.%s osg_python_script=\"%s\" "
                 "hrrr_s3_script=\"%s\" var=\"%s\" "
                 "month=\"%s\" day=\"%s\" hour=\"%s\" "
                 "fxx=\"%s\"\n") % (var_id, i, osg_script, hrrr_script,
                                    var.replace(' ', '_'), month,
                                    day, hour, fxx))
        f.write("RETRY %s.%s 10\n" % (var_id, i))
