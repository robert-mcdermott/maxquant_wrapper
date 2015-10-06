#!/bin/bash
# Christian Panse <cp@fgcz.ethz.ch>

set -x
SCRATCH=$1
ZIP=$2
OUTPUTURL=$3
YAML=$4
EXTERNALJOBID=`~cpanse/bin/fgcz_yaml.py -c $YAML -q external_job_id` 
RESSOURCEID=`~cpanse/bin/fgcz_yaml.py -c $YAML -q resource_id`

scp $ZIP $OUTPUTURL || { echo "scp failed"; exit 1; }

# clean
rm -rfv $ZIP $SCRATCH/* || { echo "clean failed"; exit 1; }

# report BFABRIC 
/home/bfabric/.python/fgcz_bfabric_setResourceStatus_available.py $RESSOURCEID \
&& /home/bfabric/.python/fgcz_bfabric_setExternalJobStatus_done.py $EXTERNALJOBID 

set +x

exit 0
