#!/bin/bash

module load python/2.7
module load globus-cli

# Move every .h5 file from the /local-scratch/blaylock directory to my stash directory
mv *.h5 ~/stash/fromScratch/

# https://docs.globus.org/cli/using-the-cli/
# Endpoint IDs found from 'globus endpoint search Tutorial'
# https://docs.globus.org/cli/examples/

# Endpoint IDs found from 'globus endpoint search Tutorial'
# On Globus transfer dashboard, https://www.globus.org/app/transfer,
# click on "Endpoints" and, the name, and copy the UUID.
ep1=9a8e5a67-6d04-11e5-ba46-22000b92c6ec    # OSG Stash Endpoint (Never Expires)
ep2=e26201e5-6d04-11e5-ba46-22000b92c6ec    # UofU Endpoint (Expires every 10 days)
                                            # Must login to globus to reactivate.

# recursively transfer the godata folder from one endpoint to another
globus transfer $ep1:~/stash/fromScratch $ep2:/~/../horel-group2/blaylock/ --recursive --label "CLI single folder"
