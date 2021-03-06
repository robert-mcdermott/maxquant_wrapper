#!/bin/bash

# Christian Panse <cp@fgcz.ethz.ch>
# 20151006

#$ -q all.q@fgcz-c-071

set -x
SCRATCH=$1
ZIP=$2

WRAPPERDIR=~cpanse/__checkouts/maxquant_wrapper/
SWEAVEDIR=$WRAPPERDIR/vignettes/
test -d $SWEAVEDIR || { echo "could not find vignettes in '$SWEAVEDIR'."; exit 1; }


echo "SCRATCH=$SCRATCH"
echo "ZIP=$ZIP"
test -d $SCRATCH && cd $SCRATCH || { echo "cd $SCRATCH  failed"; exit 1; }

pwd

test -f evidence.txt || { echo "evidence.txt is missing does not exists." ; exit 1; }
test -f msms.txt || { echo "one ore more txt file is missing does not exists." ; exit 1; }
test -f parameters.txt || { echo "one ore more txt file is missing does not exists." ; exit 1; }
test -f proteinGroups.txt || { echo "proteinGroups.txt is missing does not exists." ; exit 1; }
test -f summary.txt || { echo "one ore more txt file is missing does not exists." ; exit 1; }

cp -v proteinGroups.txt proteinGroups.txt.bak
cp -v evidence.txt evidence.txt.bak

# copying the graphics reqired by the by the Rnw files
cp $SWEAVEDIR/MQ_resultOverview.Rnw MaxQuant_report.Rnw
cp -v $SWEAVEDIR/graphics/*.pdf .
cp -v $SWEAVEDIR/QprotMatrixFunctions_rn_V2.R .

# clean up proteinGroups.txt and evidence.txt for Sweave by removing the Fasta description
/usr/bin/python3 $WRAPPERDIR/fgcz_maxquant_lfq_parser.py -i evidence.txt -o evidence.txt -u removeColumn 
/usr/bin/python3 $WRAPPERDIR/fgcz_maxquant_lfq_parser.py -i proteinGroups.txt -o proteinGroups.txt -u removeColumn
/usr/bin/python3 $WRAPPERDIR/fgcz_maxquant_lfq_parser.py -i proteinGroups.txt -o proteinGroups_FGCZ2grp_Intensity.txt -u filterIntensity

test $? -gt 0 && { echo "cleaning up evidence.txt failed"; exit 1; }

/usr/bin/python3 $WRAPPERDIR/fgcz_maxquant_lfq_parser.py -i proteinGroups.txt -o proteinGroups.txt -u removeColumn
test $? -gt 0 && { echo "cleaning up proteinGroups.txt failed"; exit 1; }

test -L maxquant || ln -s . maxquant || { echo "ln -s . maxquant failed"; exit 1; }
R --no-save --no-restore  <<EOF
Stangle('MaxQuant_report.Rnw')
Sweave('MaxQuant_report.Rnw')
quit('yes')
EOF

set +x

test $? -eq 0 \
&& xelatex MaxQuant_report.tex \
&& xelatex MaxQuant_report.tex 

test $? -eq 0 \
&& /usr/bin/zip -j $ZIP  *.txt MaxQuant_report.pdf *.sf3 *.xml *.yaml

exit 0
