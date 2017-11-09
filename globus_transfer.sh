#!/bin/bash

# https://docs.globus.org/cli/using-the-cli/
# https://docs.globus.org/cli/examples/

# Endpoint IDs found from 'globus endpoint search Tutorial'
# On Globus transfer dashboard, https://www.globus.org/app/transfer,
# click on "Endpoints" and, the name, and copy the UUID.
ep1=9a8e5a67-6d04-11e5-ba46-22000b92c6ec    # OSG Stash Endpoint (Never Expires)
ep2=e26201e5-6d04-11e5-ba46-22000b92c6ec    # UofU Endpoint (Expires every 10 days)
                                            # Must login to globus to reactivate.

# transfer from one endpoint to another
globus transfer $ep1:/share/godata/file1.txt $ep2:~/file1.txt --label "CLI single file"

# recursively transfer the godata folder from one endpoint to another
$ globus transfer $ep1:/share/godata $ep2:~/godata \
    --recursive --label "CLI single folder"

