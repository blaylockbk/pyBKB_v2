#!/bin/bash

. /cvmfs/oasis.opensciencegrid.org/osg/modules/lmod/current/init/bash

# Redirect stdout ( > ) into a named pipe ( >() ) running "tee"
exec > >(tee -i postscript_logfile.txt)

# Without this, only stdout would be captured - i.e. your
# log file would not contain any error messages.
# SEE (and upvote) the answer by Adam Spiers, which keeps STDERR
# as a separate stream - I did not want to steal from him by simply
# adding his answer to mine.
exec 2>&1

module load python/2.7
module load globus-cli

# Move every .h5 file from the /local-scratch/blaylock directory to my stash directory
mv *.h5 ~/stash/fromScratch/DPT_2_m/

# https://docs.globus.org/cli/using-the-cli/
# Endpoint IDs found from 'globus endpoint search Tutorial'
# https://docs.globus.org/cli/examples/

# Endpoint IDs found from 'globus endpoint search Tutorial'
# On Globus transfer dashboard, https://www.globus.org/app/transfer,
# click on "Endpoints" and, the name, and copy the UUID.
ep1=9a8e5a67-6d04-11e5-ba46-22000b92c6ec    # OSG Stash Endpoint (Never Expires)
ep2=219793b8-c8b7-11e7-9586-22000a8cbd7d    # UofU Endpoint (Expires every 3 months)
                                            # Must login to globus to reactivate.

# Recursively transfer the fromScratch folder from stash endpoint to CHCP endpoint
globus transfer $ep1:~/stash/fromScratch/DPT_2_m/ $ep2:~/../horel-group2/blaylock/HRRR_OSG/hourly30/DPT_2_m/ --recursive --label "DAGMan from OSG, DPT:2 m, CLI single folder"

