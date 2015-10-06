#!/bin/bash

#$ -q scaffold

set -x
INPUT=$1
SCRATCH=$2

SGEAPPBIN=~cpanse/__checkouts/maxquant_wrapper/
SCAFFOLDDRIVER=$SGEAPPBIN/fgcz_maxquant2scaffold_driver.py
SCAFFOLDDBATCH4=/srv/FGCZ/SCAFFOLD/scaffold.c71/ScaffoldBatch4
SCAFFOLDKEYPATH=/srv/FGCZ/SCAFFOLD/scaffold.c71/share/registeredKey.lkeynew


echo "JOB_ID=$JOB_ID"
echo "BASH_VERSINFO=$BASH_VERSINFO"

mkdir -p $SCRATCH && cd $SCRATCH || { echo "cd $SCRATCH failed";  exit 1; }

scp $INPUT $SCRATCH \
&& 7zr e -y $SCRATCH/`basename $INPUT` \
&& $SCAFFOLDDRIVER -m $PWD/maxquant_driver.xml -s $PWD/scaffold_driver.xml -w $PWD --fasta_dir /misc/fasta/ \
&& $SCAFFOLDDBATCH4 -q -f -keypath $SCAFFOLDKEYPATH $PWD/scaffold_driver.xml \
|| { echo "scaffold failed"; exit 1; }

set +x

exit 0
