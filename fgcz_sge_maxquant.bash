#!/bin/bash

# Christian Panse <cp@fgcz.ethz.ch>
# 20151006

#$ -q maxquant

set -x
YAML=$1
DUMP=$2

SGEAPPBIN=~cpanse/__checkouts/maxquant_wrapper/

/usr/bin/python $SGEAPPBIN/fgcz_maxquant_rpc_client.py -c $YAML -o $DUMP

set +x
exit 0
