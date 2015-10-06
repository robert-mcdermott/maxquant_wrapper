#!/bin/bash

#$ -q scaffold

INPUT=$1
SCRATCH=$2

SCAFFOLDDRIVER=~cpanse/__git_clones/maxquant_wrapper/fgcz_maxquant2scaffold_driver.py
SCAFFOLDDBATCH4=/srv/FGCZ/SCAFFOLD/scaffold.c71/ScaffoldBatch4
SCAFFOLDKEYPATH=/srv/FGCZ/SCAFFOLD/scaffold.c71/share/registeredKey.lkeynew


echo "JOB_ID=$JOB_ID"
echo "BASH_VERSINFO=$BASH_VERSINFO"

#SCRATCH=/scratch/$JOB_ID 
mkdir -p $SCRATCH && cd $SCRATCH || exit 1

scp $INPUT $SCRATCH \
&& 7zr e -y $SCRATCH/`basename $INPUT` \
&& $SCAFFOLDDRIVER -m $PWD/maxquant_driver.xml -s $PWD/scaffold_driver.xml -w $PWD --fasta_dir /misc/fasta/ \
&& $SCAFFOLDDBATCH4 -q -f -keypath $SCAFFOLDKEYPATH $PWD/scaffold_driver.xml 

exit 0


# maxquant2scaffold
# run scaffold
