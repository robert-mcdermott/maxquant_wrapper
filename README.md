# maxquant_wrapper
- easy high throughput processing 
- the wrapper takes care for the data staging

## input config file
## output zip file


# old bash script
```
#!/bin/bash -x
#$ -N fgcz_sge_scaffold
#$ -S /bin/bash
#$ -q maxquant

. /home/bfabric/sgeworker/bin/fgcz_sge_initng.sh
test $? -gt 0 && (echo "init failed" ; exit 1)

# by Simon Barkow & Christian Panse  <{sb,cp}@fgcz.ethz.ch>
# December 2013

# Example:
# qsub ./fgcz_sge_scaffold -i 130.60.81.23 -j /usr/local/mascot/data/20100127/F107346.dat -o 130.60.81.23 -p /tmp/$USER.$$.F107346.sf3

## There are four files involved in this app:
# 1.) fgcz_sge_MaxQuant_Scaffold_LFQ_fast: this script
# 2.) MaxQuantDriverTemplate_fast.xml: template for MaxQuant
# 3.) create_maxquant_driver_xml.rb: script to alter the MaxQuant template
# 4.) create_scaffold_input_xml.rb: create scaffold driver
# 
## The SSH Server (Powershell server) has to be running on the fgcz-v-074 and the administrator has to be logged on

# SET MANDATORY PARAMETERS
CONTACT="Simon Barkow <sb@fgcz.ethz.ch>"
LASTMODIFIED="Fri Dec  6 11:27:37 CET 2013"
LASTMODIFIED="Mon Dec 16 09:52:48 CET 2013"
LASTMODIFIED="Wed Jan  8 08:47:19 CET 2014"
LASTMODIFIED="Thu Jan  9 16:32:38 CET 2014"
LASTMODIFIED="Fri Dec 12 12:05:27 CET 2014"


SCPOPTION="-o VerifyHostKeyDNS=no -c arcfour"

OPTIND=1

SCRATCHSPACE=/scratch/fgcz_sge_scaffold_MQ/
mkdir -p $SCRATCHSPACE || die "'mkdir -p $SCRATCHSPACE' failed"

SCAFFOLDSPACE=$SCRATCHSPACE/$$.scaffold/
MAXQUANTRESULTFILE=$$.maxquant.zip
mySCAFFOLD=/usr/local/FGCZ/SCAFFOLD/ScaffoldBatch4
mySCAFFOLDDRIVER=$SCRATCHSPACE/$$.scaffold-driver.xml

#TESTING without B-Fabric 20140108:
#INPUTFILE=/scratch/fgcz_sge_scaffold_MQ/19815.scaffold/mqpar_p1000_10techReps.xml
#INPUTFILE=/home/bfabric/repo/p1000/General/Local_File_Import__no_annotation_/workunit_121438/jg_mqpar.xml
#INPUTFILE=/srv/www/htdocs/p1000/Proteomics/QEXACTIVE_2/paolo_20131204_TestBeads_Yeast_HeLa/20131204_01_Fetuin400amol_Col19um.raw,/srv/www/htdocs/p1000/Proteomics/QEXACTIVE_2/paolo_20131204_TestBeads_Yeast_HeLa/20131204_03_Fetuin400amol_Col19um.raw,/srv/www/htdocs/p1000/Proteomics/QEXACTIVE_2/paolo_20131204_TestBeads_Yeast_HeLa/20131204_16_Fetuin400amol_Col19um.raw,/srv/www/htdocs/p1000/Proteomics/QEXACTIVE_2/paolo_20131204_TestBeads_Yeast_HeLa/20131204_18_Fetuin400amol_Col19um.raw,
#SCAFFOLDSPACE=/scratch/fgcz_sge_scaffold_MQ/99999.scaffold
#MAXQUANTRESULTFILE=99999.maxquant.zip
#END TESTING

mkdir -p $SCAFFOLDSPACE || die "'mkdir -p $SCRATCHSPACE/$$.scaffold' failed"

copyRawFilesToMaxquantComputer() {
    echo "________--- Copy ----_________"
    echo "New-Item $maxQuantWindowsFolder -type directory; exit" | ssh -T 130.60.81.74
    echo "\$bf_password=Get-Content d:\YHgSqYs6exw5bmck\PZNnWNNbX63PiAbA.txt; net use t: \\\\fgcz-proteomics.uzh.ch\\$projectNumber /USER:bfabric \$bf_password; exit"  | ssh -T 130.60.81.74
    IFS=','
    for i in $INPUTFILE
    do
        fileToCopy=T:\\`echo $i | sed -e "s/\/srv\/www\/htdocs\/$projectNumber\///g" | sed -e 's/\\//\\\\/g'`
        echo "Copy-Item $fileToCopy $maxQuantWindowsFolder; exit " | ssh -T 130.60.81.74
    done 
    IFS=''
    echo "net use /delete /y t: ;exit" | ssh -T 130.60.81.74
}

generateMaxQuantXML() {
    echo "generateMaxQuantXML"
    # alter MaxQuant xml template
    ruby /home/bfabric/sgeworker/bin/create_maxquant_driver_xml.rb /home/bfabric/sgeworker/bin/MaxQuantDriverTemplate_fast.xml $maxQuantWindowsFolder $INPUTFILE > $SCAFFOLDSPACE/$$.MaxQuantDriver.xml
    # copy MaxQuant xml file over to MaxQuant computer
    scp $SCAFFOLDSPACE/$$.MaxQuantDriver.xml bfabric@130.60.81.21:/srv/www/htdocs/Data2San/fgcz_sge_scaffold_MQ/$$.MaxQuantDriver.xml
    echo "\$bb_password=Get-Content d:\YHgSqYs6exw5bmck\4ZlNJd0ecdTxOHBt.txt; net use s: \\\\fgcz-proteomics.uzh.ch\Data2San /USER:FGCZ-NET\BioBeamer \$bb_password; Copy-Item \\\\fgcz-proteomics.uzh.ch\Data2San\fgcz_sge_scaffold_MQ\\$$.MaxQuantDriver.xml $maxQuantWindowsFolder; exit; " | ssh -T 130.60.81.74
    echo "net use /delete /y s:; exit;" | ssh -T 130.60.81.74
}

runMaxQuantOverSSH() {
    XMLFILE=$1
    # First, check if the input file really is a xml File
    if [ ! [ "$XMLFILE" == *.xml ]]; then 
        die "XMLFILE is no xml file"
    fi
    MAXQUANTLINUXFOLDERNAME=`basename $XMLFILE`
    echo "________--- run Maxquant over SSH ----_________"
    echo "CMD /C \"C:\Program Files\mxQnt_versions\MaxQuant_1.4.1.2\MaxQuant\bin\MaxQuantCmd.exe\" -mqpar=$maxQuantWindowsFolder\\$MAXQUANTLINUXFOLDERNAME -ncores=8; exit" | ssh -T 130.60.81.74
    checkFile=$maxQuantWindowsFolder\\combined\\txt\\allPeptides.txt
    echo "While (\$TRUE) {\"...\"; Start-Sleep -s 20; if (-not (Test-Path $maxQuantWindowsFolder\\combined)) {\"The combined folder does not exist! Exitting MaxQuant\";exit;}; if (Test-Path $checkFile) {\$filesize1 = (Get-Item $checkFile).length;Start-Sleep -s 120;\$filesize2 = (Get-Item $checkFile).length; if (\$filesize1 -eq \$filesize2) {\"allPeptides.txt is unchanged, so I exit powershell to carry on with copying files. \"; exit}}}" | ssh -T 130.60.81.74
    echo "New-Item c:\tmp\tmpMQ\\$MAXQUANTLINUXFOLDERNAME -type directory; exit"  | ssh -T 130.60.81.74
    echo "Copy-Item $maxQuantWindowsFolder\combined\txt\*.txt c:\tmp\tmpMQ\\$MAXQUANTLINUXFOLDERNAME\; Copy-Item $maxQuantWindowsFolder\combined\*.txt c:\tmp\tmpMQ\\$MAXQUANTLINUXFOLDERNAME\; Copy-Item $maxQuantWindowsFolder\combined\andromeda\*.apl c:\tmp\tmpMQ\\$MAXQUANTLINUXFOLDERNAME\; Copy-Item $maxQuantWindowsFolder\combined\*.apl c:\tmp\tmpMQ\\$MAXQUANTLINUXFOLDERNAME\;exit" | ssh -T 130.60.81.74
    sleep 10 
    echo "CMD /C \"C:\Program Files\7-zip\7z.exe\" a c:\tmp\tmpMQ\\$MAXQUANTLINUXFOLDERNAME.zip c:\tmp\tmpMQ\\$MAXQUANTLINUXFOLDERNAME\*; exit" | ssh -T 130.60.81.74
    sleep 10 
    echo "\$bb_password=Get-Content d:\YHgSqYs6exw5bmck\4ZlNJd0ecdTxOHBt.txt; net use s: \\\\fgcz-proteomics.uzh.ch\Data2San /USER:FGCZ-NET\BioBeamer \$bb_password; Copy-Item c:\tmp\tmpMQ\\$MAXQUANTLINUXFOLDERNAME.zip \\\\fgcz-proteomics.uzh.ch\Data2San\fgcz_sge_scaffold_MQ\\$MAXQUANTRESULTFILE; net use /delete /y s:; exit; " | ssh -T 130.60.81.74

##  For using scp (for example https://www.nsoftware.com), uncomment the following line and change the every path to the maxquant results folder on the linux node in this script
##    echo "Import-Module C:\Users\simon\Documents\WindowsPowerShell\Modules\NetCmdlets; Send-SCP -Server 192.168.81.49  -User bfabric  -SSHAccept e7:4f:59:ed:bf:de:00:97:ff:5e:b3:c0:68:b1:48:58 -LocalFile c:\tmp\tmpMQ\\$MAXQUANTLINUXFOLDERNAME.zip -Password \$bf_password -RemoteFile $MAXQUANTZIP; exit " | ssh -T 130.60.81.74
    
    unzip /srv/www/htdocs/Data2San/fgcz_sge_scaffold_MQ/$MAXQUANTRESULTFILE -d $SCAFFOLDSPACE/maxquant
    chmod -R go+r $SCAFFOLDSPACE
}

QCReport() {
    echo "QCReport"
    test -d $SCAFFOLDSPACE/maxquant || { echo "Maxquant folder does not exists." ; exit 1; }
    cd /home/bfabric/sgeworker/bin/R-Sweave_QCofMQresults/
    rm -v /home/bfabric/sgeworker/bin/R-Sweave_QCofMQresults/maxquant
    ln -s $SCAFFOLDSPACE/maxquant /home/bfabric/sgeworker/bin/R-Sweave_QCofMQresults/maxquant 
    test -f maxquant/evidence.txt || { echo "evidence.txt is missing does not exists." ; exit 1; }
    test -f maxquant/msms.txt || { echo "one ore more txt file is missing does not exists." ; exit 1; }
    test -f maxquant/parameters.txt || { echo "one ore more txt file is missing does not exists." ; exit 1; }
    test -f maxquant/proteinGroups.txt || { echo "proteinGroups.txt is missing does not exists." ; exit 1; }
    test -f maxquant/summary.txt || { echo "one ore more txt file is missing does not exists." ; exit 1; }
    
    cp maxquant/proteinGroups.txt maxquant/proteinGroups.txt.bak
    cp maxquant/evidence.txt maxquant/evidence.txt.bak
    
    # Select which QCSweaveFile to take based on RT-Kit and iRT_Protein
    if grep --quiet RT-Kit maxquant/proteinGroups.txt; then 
        echo "RT-Kit found in proteinGroups.txt"
	    cp LFQ_QC_RT-Kit.Rnw QCSweaveFile.Rnw
	elif grep --quiet iRT_Protein maxquant/proteinGroups.txt; then
        echo "iRT_Protein found in proteinGroups.txt"
	    cp LFQ_QC_iRT_Protein.Rnw QCSweaveFile.Rnw
	else  
	    echo "neither iRT_Protein nor RT-Kit found in proteinGroups.txt"
        cp LFQ_QC_no_iRT_Protein.Rnw QCSweaveFile.Rnw
	fi
    
    # clean up proteinGroups.txt and evidence.txt for Sweave by removing the Fasta description
    python3 MaxQuant_LFQ_parser.py -i maxquant/evidence.txt -o maxquant/evidence.txt -u removeColumn
    test $? -gt 0 && die "cleaning up evidence.txt failed"
	python3 MaxQuant_LFQ_parser.py -i maxquant/proteinGroups.txt -o maxquant/proteinGroups.txt -u removeColumn
    test $? -gt 0 && die "cleaning up proteinGroups.txt failed"
	

    # R CMD Sweave /home/bfabric/sgeworker/bin/R-Sweave_QCofMQresults/QCSweaveFile.Rnw && xelatex QCSweaveFile && xelatex QCSweaveFile
R --no-save --no-restore  <<EOF
Stangle('/home/bfabric/sgeworker/bin/R-Sweave_QCofMQresults/QCSweaveFile.Rnw')
Sweave('/home/bfabric/sgeworker/bin/R-Sweave_QCofMQresults/QCSweaveFile.Rnw')
quit('yes')
EOF

    test $? -eq 0 \
&& xelatex QCSweaveFile.tex \
&& xelatex QCSweaveFile.tex 


    mv -v /home/bfabric/sgeworker/bin/R-Sweave_QCofMQresults/QCSweaveFile.pdf $SCAFFOLDSPACE/maxquant.pdf
    mv maxquant/proteinGroups.txt.bak maxquant/proteinGroups.txt
    mv maxquant/evidence.txt.bak maxquant/evidence.txt 
    rm -v /home/bfabric/sgeworker/bin/R-Sweave_QCofMQresults/maxquant
    rm -v /home/bfabric/sgeworker/bin/R-Sweave_QCofMQresults/*.pdf
}

myScaffoldDriverGenerator() {
    XMLFILE=$1
    
    # First, check if the input file really is a xml File
    if [ ! [ "$XMLFILE" == *.xml ]]; then 
        die "$XMLFILE is no xml file"
    fi
    
	# grep FASTA file from input xml  <string>R:\MaxQuantDBs\fgcz_contaminants_20130115.fasta</string>
	fastaDBName=`grep -o '.*\\.*\.fasta' $XMLFILE | head -n1 | awk -F'\\' '{print $NF}'`
	test $? -gt 0 && die "getting 'fastaDBPath' failed"
	
	fastaDBPath=`find /imports/share/fgcz/db/ | grep "$fastaDBName" | grep ".fasta$" | tail -n1`
	test ! ${#fastaDBPath} -gt 0 && die "Cannot access '$fastaDBName'. Fasta DB is probably not in /imports/share/fgcz/db/"
		
	experimentName=$MAXQUANTLINUXFOLDERNAME
	test $? -gt 0 && die "getting 'experimentName' failed"
	
	echo "<Scaffold>" \
	> $mySCAFFOLDDRIVER

    echo "<Experiment name='$experimentName'  analyzeWithTandem='false' connectToNCBI='false' condenseDataWhileLoading='true' annotateWithGOA='true' unimodFile='/misc/FGCZ/SCAFFOLD/parameters/unimod.xml'" >> $mySCAFFOLDDRIVER 

	echo "highMassAccuracyScoring='true' >" \
	>> $mySCAFFOLDDRIVER 
	
	echo "<FastaDatabase id=\"$fastaDBName\" path=\"$fastaDBPath\" databaseAccessionRegEx=\">([^ ]*)\" databaseDescriptionRegEx=\">[^ ]* (.*)\" decoyProteinRegEx=\"REV_|rr\|\" />" \
	>> $mySCAFFOLDDRIVER
	
    # get searchTitle name for naming of the sample
    searchTitle="${MAXQUANTLINUXFOLDERNAME%.*}"

    # create scaffold input xml file with as many BioSamples as there are raw files in the MaxQuant Folder (as specified in the MaxQuant xml)
    ruby /home/bfabric/sgeworker/bin/create_scaffold_input_xml.rb $XMLFILE $SCAFFOLDSPACE/maxquant >> $mySCAFFOLDDRIVER
   
	echo "<DisplayThresholds name='95%' 
		id='thresh' 
		proteinProbability='0.95' 
		minimumPeptideCount='2' 
		peptideProbability='0.95'/>" \
	>> $mySCAFFOLDDRIVER

	echo "<Export type='sfd' 
		thresholds='thresh' 
		path='$SCAFFOLDSPACE/'/>" \
	>> $mySCAFFOLDDRIVER

	echo "<Export type='experiment-report' 
		thresholds='thresh' 
		experimentDisplayType='Quantitative Value'
		quantitativeDisplayType='Top 3 Precursor Intensity'
		path='$SCAFFOLDSPACE/'/>" \
	>> $mySCAFFOLDDRIVER

	echo "</Experiment>" \
	>> $mySCAFFOLDDRIVER

	echo "</Scaffold>" \
	>> $mySCAFFOLDDRIVER
}


#__________MAIN___________


# 0.) make sure that the drive letters S: and T: are not occupied
echo "net use /delete /y t: ;net use /delete /y s:; exit" |  ssh -T 130.60.81.74

# Check whether INPUT is XML or a collection of RAW files
if echo $INPUTFILE | grep -q '\.xml$' ; then 
    echo "INPUT is a xml file"
    maxQuantWindowsFolder=`grep -o '[A-Za-z]:\\\\FGCZ\\\\p[0-9].*\\\\.*\\\\.*raw' $INPUTFILE | head -n1 | awk -F'\\' '{$NF=""; print $0}' | sed -e 's/ /\\\\/g'`
    #copy xml file from INPUT to SCAFFOLDSPACE
    cp $INPUTFILE $SCAFFOLDSPACE/$$.MaxQuantDriver.xml
else
    echo "INPUT is no xml file"
    projectNumber=`echo $INPUTFILE | grep -o 'p[0-9]\{1,5\}' | head -n1`
    maxQuantWindowsFolder=D:\\MaxQuant_BFabric\\$projectNumber

    # 1.) copy raw Files and xml file to MaxQuant computer if INPUT is a collection of raw files
    copyRawFilesToMaxquantComputer
    test $? -gt 0 && die "'copyRawFilesToMaxquantComputer' failed"

    # 2.) generate MaxQuant xml Files
    generateMaxQuantXML
    test $? -gt 0 && die "'generateMaxQuantXML' failed"  
fi 

# 3.) run MaxQuant over SSH on the 74:
runMaxQuantOverSSH $SCAFFOLDSPACE/$$.MaxQuantDriver.xml
test $? -gt 0 && die "'runMaxQuantOverSSH' failed"

# 4.) Create QC report pdf with R and Sweave Latex
QCReport
test $? -gt 0 && die "'QCReport' failed"

# 5.) generate scaffold driver xml file and run Scaffold:
myScaffoldDriverGenerator $SCAFFOLDSPACE/$$.MaxQuantDriver.xml
test $? -gt 0 && die "'myScaffoldDriverGenerator' failed"
test -s $mySCAFFOLDDRIVER || die "no SCAFFOLDDRIVER file found."
nice -15 $mySCAFFOLD $mySCAFFOLDDRIVER || die "SCAFFOLD failed."
test $? -gt 0 && die "'ScaffoldBatch' failed"

# BEGIN WRITING THE OUTPUT BACK
zip -j $SCAFFOLDSPACE/output.zip $SCAFFOLDSPACE/*.sf3 $SCAFFOLDSPACE/maxquant.pdf $SCAFFOLDSPACE/*.xls $SCAFFOLDSPACE/maxquant/*.txt
test $? -gt 0 && die "zipping output failed"

TEMPDIR=$SCAFFOLDSPACE/

#if you want to output only the maxQuant file, use this (maybe remove the unzip command):
#zip -j $SCAFFOLDSPACE/output.zip $SCAFFOLDSPACE/maxquant

output2wu output.zip

# END WRITING THE OUTPUT BACK

# BEGIN CLEAN THE SYSTEM
rm -fv $SCRATCHSPACE/$$.*.xml $SCAFFOLDSPACE/maxquant/*  
rmdir $SCAFFOLDSPACE/maxquant
rm -fv $SCAFFOLDSPACE/*
rmdir $SCAFFOLDSPACE
test $? -gt 0 && die "cleaning failed"

# Clean MaxQuant zip and xml files from the Data2San drive.
echo "\$bb_password=Get-Content d:\YHgSqYs6exw5bmck\4ZlNJd0ecdTxOHBt.txt; net use s: \\\\fgcz-proteomics.uzh.ch\Data2San /USER:FGCZ-NET\BioBeamer \$bb_password; Remove-Item -force \\\\fgcz-proteomics.uzh.ch\Data2San\fgcz_sge_scaffold_MQ\\$MAXQUANTRESULTFILE; Remove-Item -force \\\\fgcz-proteomics.uzh.ch\Data2San\fgcz_sge_scaffold_MQ\\$$.MaxQuantDriver.xml; exit " | ssh -T 130.60.81.74
test $? -gt 0 && die "cleaning on Data2San failed"

#clean up R:\ Ramdisk and c:\tmp\tmpMQ
echo "Remove-Item -Recurse -Force $maxQuantWindowsFolder;exit" | ssh -T 130.60.81.74
echo "Remove-Item -Recurse -Force C:\tmp\tmpMQ\; New-Item C:\tmp\tmpMQ -type directory;exit" | ssh -T 130.60.81.74

exit 0

```
