#!/bin/bash

# Christian Panse <cp@fgcz.ethz.ch>
# 201510

# This script takes as input an config file. 
# NOTE: Ensure that the config file is on the same host where this script is executed.

#$ -q PRX@fgcz-c-071

set -x	
STAMP=`/bin/date +%Y%m%d%H%M`.$$.$JOB_ID
YAMLREADER=/home/cpanse/bin/fgcz_yaml.py
YAML=$1
DUMPURL="bfabric@130.60.81.21:/scratch/"
WORKUNITID=`$YAMLREADER -c $YAML -q wu`
OUTPUTURL=`$YAMLREADER -c $YAML -q output`
SGEAPPBIN=~cpanse/__checkouts/maxquant_wrapper/

SCRATCH=/scratch/$JOB_ID/
mkdir -p $SCRATCH || { echo "mkdir '$SCRATCH' failed"; exit 1; }


[ -f $YAML ] || { echo "$YAML file is not available"; exit 1; }
cp $YANL $SCRATCH

echo "JOB_ID=$JOB_ID"
echo "BASH_VERSINFO=$BASH_VERSINFO"
echo "STAMP=$STAMP"
echo "YAML=$YAML"
echo "WORKUNITID=$WORKUNITID"
echo "OUTPUTURL=$OUTPUTURL"


qsub -N mq_$STAMP -q maxquant $SGEAPPBIN/fgcz_sge_maxquant.bash $YAML $DUMPURL/mq_$STAMP.dump

qsub -N s_$STAMP -hold_jid mq_$STAMP -q scaffold $SGEAPPBIN/fgcz_sge_scaffold.bash $DUMPURL/mq_$STAMP.dump /scratch/$JOB_ID

qsub -N qc_$STAMP -hold_jid s_$STAMP -q all.q@fgcz-c-071 $SGEAPPBIN/fgcz_sge_qc.bash /scratch/$JOB_ID /scratch/$JOB_ID.zip

qsub -N stage_clean_$STAMP -hold_jid qc_$STAMP -q all.q@fgcz-c-071 $SGEAPPBIN/fgcz_sge_stage_output.bash /scratch/$JOB_ID /scratch/$JOB_ID.zip $OUTPUTURL $YAML
set +x

sleep 10

exit 0
