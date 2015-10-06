#!/bin/bash

#$ -q maxquant

YAML=$1
DUMP=$2

#scp $YAML $DUMP
/usr/bin/python ~cpanse//__git_clones/maxquant_wrapper/fgcz_maxquant_rpc_client.py -c $YAML -o $DUMP
exit 0
