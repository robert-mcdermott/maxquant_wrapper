#!/usr/bin/python


import sys
import os
import shutil
import unittest

import xmlrpclib
import time
import subprocess
import re

import logging
import logging.handlers

def create_logger(name="MaxQuant"):
    """
    create a logger object
    """
    syslog_handler = logging.handlers.SysLogHandler(address=("130.60.81.148", 514))
    formatter = logging.Formatter('%(name)s %(message)s')
    syslog_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(20)
    logger.addHandler(syslog_handler)

    return logger

logger = create_logger()

class FgczMaxquantWrapper:
    """

    """
    config = None
    scratchroot = os.path.normcase(r"/cygdrive/d/scratch_")
    scratch = scratchroot

    def __init__(self, config=None):

        if not os.path.isdir(self.scratchroot):
            try:
                os.mkdir(self.scratchroot)
            except:
                print "scratch '{0}' does not exists.".format(self.scratchroot)
                raise
        if config:
            self.config=config

    def run_commandline(self, cmd, shell_flag=False):
        (pid, return_code) = (None, None)

        (out,err)=("","")
        tStart = time.time()

        logger.info(cmd)
        try:
            p = subprocess.Popen(cmd, shell=shell_flag)

            pid = p.pid
            return_code = p.wait()

            (out, err) = p.communicate()
            p.terminate()

        except OSError as e:
            msg = "exception|pid={0}|OSError={1}".format(pid, e)
            logger.info(msg)

        msg_info = "completed|pid={0}|time={1}|return_code={2}|cmd='{3}'" \
            .format(pid, time.time() - tStart, return_code, cmd)
        logger.info(msg_info)

        print out
        print err
        return (return_code)

    def map_url_scp2smb(self, url,
                            from_prefix_regex="bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs",
                            to_prefix="\\\\130.60.81.21\\data"):
        """maps an url from

        'bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs//p1946/Proteomics/QEXACTIVE_2/paolo_20150811_course/20150811_01_Fetuin40fmol.raw'

        to

        '\\130.60.81.21\data\p1946\proteomics\qexactive_2\paolo_20150811_course\20150811_01_fetuin40fmol.raw'

        if it can not be matched it returns None
        """

        regex = re.compile("({0}.+)(p[0-9]+([\\/]).*)$".format(from_prefix_regex))

        match = regex.match(url)

        if match:
            result_url = "{0}\{1}".format(to_prefix, os.path.normcase(match.group(2)))
            return (result_url)
        else:
            return None

    def print_config(self):
        print self.config

    def add_configuration(self, config):
        self.config = config
        return True

    def create_scratch(self):
        """create scratch space
        """

        # TODO(cp): what if workunit is not defined
        self.scratch = os.path.normcase(
            "{0}/{1}".format(self.scratchroot, self.config['job_configuration']['workunit_id']))

        if not os.path.isdir(self.scratch):
            try:
                os.mkdir(self.scratch)
            except:
                logger.info("scratch '{0}' does not exists.".format(self.scratch))
                raise

        return True

    
	

    def copy_input_to_scratch(self,
                              copy_method=lambda s,t: shutil.copyfile(s, t),
                              src_url_mapping=lambda x: x,
                              dst_url_mapping=lambda x: os.path.basename(x)):
        """
        make input resources available on scratch


        for smb use:
            src_url_mapping = lambda x: (self.map_url_scp2smb(x)
            dst_url_mapping = os.path.normcase("{0}/{1}".format(self.scratch, os.path.basename(x)))
        """

        # copy input to scratch
        _input = self.config['application']['input']

        try:
            self._fsrc_fdst = []
            for i in _input.keys():
                self._fsrc_fdst = self._fsrc_fdst + map(lambda x: (src_url_mapping(x), dst_url_mapping(x)), _input[i])


            for (_fsrc, _fdst) in self._fsrc_fdst:
                if os.path.isfile(_fdst):
                    # TODO(cp): file cmp
                    logger.info("'{0}' is already there.".format(_fdst))
                    pass
                else:
                    try:
			if not os.path.isfile(_fsrc):
                            logger.info("ERROR")
                        logger.info("copy '{0}' from '{1}' ...".format(_fdst, _fsrc))
                        copy_method(_fsrc, _fdst)
                    except:
                        print "ERROR: fail copy failed."
                        raise

        except:
            raise

        return True

    def compose_maxquant_driver_file(self, filename=None):
        assert isinstance(filename, basestring)
        # TODO(cp): stage FASTA
        _xml="""<?xml version='1.0' encoding='UTF-8'?>
<MaxQuantParams xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xmlns:xsd='http://www.w3.org/2001/XMLSchema' aifSilWeight='4' aifIsoWeight='2' aifTopx='20' aifCorrelation='0.47' aifCorrelationFirstPass='0.8' aifMinMass='0' aifMsmsTol='10' aifSecondPass='true' aifIterative='true' aifThresholdFdr='0.01'>
  <slicePeaks>true</slicePeaks>
  <tempFolder/>
  <fixedCombinedFolder/>
  <ionCountIntensities>false</ionCountIntensities>
  <verboseColumnHeaders>false</verboseColumnHeaders>
  <minTime>NaN</minTime>
  <maxTime>NaN</maxTime>
  <fullMinMz>-1.7976931348623157E+308</fullMinMz>
  <fullMaxMz>1.7976931348623157E+308</fullMaxMz>
  <calcPeakProperties>false</calcPeakProperties>
  <useOriginalPrecursorMz>false</useOriginalPrecursorMz>
  <minPeakLen>2</minPeakLen>
  <filePaths>
    {0}
  </filePaths>
  <experiments>
    {1}
  </experiments>
  <fractions>
    {2}
  </fractions>
  <matching>
    {3}
  </matching>
  <paramGroupIndices>
    {4}
  </paramGroupIndices>
  <parameterGroups>
    <parameterGroup>
      <maxCharge>7</maxCharge>
      <msInstrument>0</msInstrument>
      <labelMods>
        <string/>
      </labelMods>
      <lfqMinEdgesPerNode>3</lfqMinEdgesPerNode>
      <lfqAvEdgesPerNode>6</lfqAvEdgesPerNode>
      <fastLfq>true</fastLfq>
      <lfqMinRatioCount>2</lfqMinRatioCount>
      <useNormRatiosForHybridLfq>true</useNormRatiosForHybridLfq>
      <maxLabeledAa>0</maxLabeledAa>
      <maxNmods>5</maxNmods>
      <maxMissedCleavages>2</maxMissedCleavages>
      <multiplicity>1</multiplicity>
      <enzymes>
        <string>Trypsin/P</string>
      </enzymes>
      <enzymesFirstSearch/>
      <useEnzymeFirstSearch>false</useEnzymeFirstSearch>
      <useVariableModificationsFirstSearch>false</useVariableModificationsFirstSearch>
      <variableModifications>
        <string>Acetyl (Protein N-term)</string>
        <string>Oxidation (M)</string>
        <string>Deamidation (NQ)</string>
      </variableModifications>
      <isobaricLabels/>
      <variableModificationsFirstSearch/>
      <hasAdditionalVariableModifications>false</hasAdditionalVariableModifications>
      <additionalVariableModifications/>
      <additionalVariableModificationProteins/>
      <doMassFiltering>true</doMassFiltering>
      <firstSearchTol>20</firstSearchTol>
      <mainSearchTol>4.5</mainSearchTol>
      <lcmsRunType>0</lcmsRunType>
      <lfqMode>1</lfqMode>
      <enzymeMode>3</enzymeMode>
      <enzymeModeFirstSearch>0</enzymeModeFirstSearch>
    </parameterGroup>
  </parameterGroups>
  <fixedModifications>
    <string>Carbamidomethyl (C)</string>
  </fixedModifications>
  <multiModificationSearch>false</multiModificationSearch>
  <compositionPrediction>false</compositionPrediction>
  <fastaFiles>
    <string>D:\\MaxQuantDBs\\fgcz_swissprot_20121031.fasta</string>
  </fastaFiles>
  <fastaFilesFirstSearch/>
  <fixedSearchFolder/>
  <advancedRatios>false</advancedRatios>
  <rtShift>false</rtShift>
  <separateLfq>false</separateLfq>
  <lfqStabilizeLargeRatios>true</lfqStabilizeLargeRatios>
  <lfqRequireMsms>true</lfqRequireMsms>
  <decoyMode>revert</decoyMode>
  <specialAas>KR</specialAas>
  <includeContamiants>true</includeContamiants>
  <equalIl>false</equalIl>
  <topxWindow>100</topxWindow>
  <maxPeptideMass>4600</maxPeptideMass>
  <reporterPif>0.75</reporterPif>
  <reporterFraction>0</reporterFraction>
  <reporterBasePeakRatio>0</reporterBasePeakRatio>
  <minDeltaScoreUnmodifiedPeptides>0</minDeltaScoreUnmodifiedPeptides>
  <minDeltaScoreModifiedPeptides>17</minDeltaScoreModifiedPeptides>
  <minScoreUnmodifiedPeptides>0</minScoreUnmodifiedPeptides>
  <minScoreModifiedPeptides>40</minScoreModifiedPeptides>
  <filterAacounts>true</filterAacounts>
  <secondPeptide>true</secondPeptide>
  <matchBetweenRuns>true</matchBetweenRuns>
  <matchUnidentifiedFeatures>false</matchUnidentifiedFeatures>
  <matchBetweenRunsFdr>false</matchBetweenRunsFdr>
  <reQuantify>true</reQuantify>
  <dependentPeptides>false</dependentPeptides>
  <dependentPeptideFdr>0</dependentPeptideFdr>
  <dependentPeptideMassBin>0</dependentPeptideMassBin>git
  <msmsConnection>false</msmsConnection>
  <ibaq>false</ibaq>
  <useDeltaScore>false</useDeltaScore>
  <avalon>false</avalon>
  <msmsRecalibration>false</msmsRecalibration>
  <ibaqLogFit>false</ibaqLogFit>
  <razorProteinFdr>true</razorProteinFdr>
  <deNovoSequencing>false</deNovoSequencing>
  <deNovoVarMods>true</deNovoVarMods>
  <massDifferenceSearch>false</massDifferenceSearch>
  <minPepLen>7</minPepLen>
  <peptideFdr>0.01</peptideFdr>
  <proteinFdr>0.05</proteinFdr>
  <siteFdr>0.01</siteFdr>
  <minPeptideLengthForUnspecificSearch>8</minPeptideLengthForUnspecificSearch>
  <maxPeptideLengthForUnspecificSearch>25</maxPeptideLengthForUnspecificSearch>
  <useNormRatiosForOccupancy>true</useNormRatiosForOccupancy>
  <minPeptides>1</minPeptides>
  <minRazorPeptides>1</minRazorPeptides>
  <minUniquePeptides>0</minUniquePeptides>
  <useCounterparts>false</useCounterparts>
  <minRatioCount>2</minRatioCount>
  <restrictProteinQuantification>true</restrictProteinQuantification>
  <restrictMods>
    <string>Acetyl (Protein N-term)</string>
    <string>Oxidation (M)</string>
  </restrictMods>
  <matchingTimeWindow>2</matchingTimeWindow>
  <alignmentTimeWindow>20</alignmentTimeWindow>
  <numberOfCandidatesMultiplexedMsms>25</numberOfCandidatesMultiplexedMsms>
  <numberOfCandidatesMsms>15</numberOfCandidatesMsms>
  <massDifferenceMods/>
  <crossLinkerSearch>false</crossLinkerSearch>
  <crossLinker/>
  <labileCrossLinkerSearch>false</labileCrossLinkerSearch>
  <labileCrossLinker>DSSO</labileCrossLinker>
  <RescoreMsx>false</RescoreMsx>
  <msmsParamsArray>
    <msmsParams Name='FTMS' InPpm='true' Deisotope='true' Topx='12' HigherCharges='true' IncludeWater='true' IncludeAmmonia='true' DependentLosses='true'>
      <Tolerance>
        <Value>20</Value>
        <Unit>Ppm</Unit>
      </Tolerance>
      <DeNovoTolerance>
        <Value>20</Value>
        <Unit>Ppm</Unit>
      </DeNovoTolerance>
    </msmsParams>
    <msmsParams Name='ITMS' InPpm='false' Deisotope='false' Topx='8' HigherCharges='true' IncludeWater='true' IncludeAmmonia='true' DependentLosses='true'>
      <Tolerance>
        <Value>0.5</Value>
        <Unit>Dalton</Unit>
      </Tolerance>
      <DeNovoTolerance>
        <Value>0.5</Value>
        <Unit>Dalton</Unit>
      </DeNovoTolerance>
    </msmsParams>
    <msmsParams Name='TOF' InPpm='false' Deisotope='false' Topx='10' HigherCharges='true' IncludeWater='true' IncludeAmmonia='true' DependentLosses='true'>
      <Tolerance>
        <Value>0.1</Value>
        <Unit>Dalton</Unit>
      </Tolerance>
      <DeNovoTolerance>
        <Value>0.1</Value>
        <Unit>Dalton</Unit>
      </DeNovoTolerance>
    </msmsParams>
    <msmsParams Name='Unknown' InPpm='false' Deisotope='false' Topx='10' HigherCharges='true' IncludeWater='true' IncludeAmmonia='true' DependentLosses='true'>
      <Tolerance>
        <Value>0.5</Value>
        <Unit>Dalton</Unit>
      </Tolerance>
      <DeNovoTolerance>
        <Value>0.5</Value>
        <Unit>Dalton</Unit>
      </DeNovoTolerance>
    </msmsParams>
  </msmsParamsArray>
  <msmsCentroidMode>1</msmsCentroidMode>
  <quantMode>1</quantMode>
  <siteQuantMode>0</siteQuantMode>
</MaxQuantParams>
""".format("\n".join(map(lambda x: "\t<string>{0}</string>".format(x[1].encode('utf8').replace("/cygdrive/d/", "d:\\").replace("/", "\\")), self._fsrc_fdst)),
           "\n".join(map(lambda x: "\t<string>{0}</string>".format(os.path.splitext(os.path.basename(x[1]))[0].encode('utf8')), self._fsrc_fdst)),
           "\n".join(map(lambda x: "\t<short>32767</short>", self._fsrc_fdst)),
           "\n".join(map(lambda x: "\t<unsignedByte>3</unsignedByte>", self._fsrc_fdst)),
           "\n".join(map(lambda x: "\t<int>0</int>", self._fsrc_fdst)))

        try:
            with open(filename, "w") as f:
                logger.info("writing '{0}' ...".format(filename))
                f.write(_xml)
        except:
            logger.info("writing maxquant driver file failed.")
            raise

        return True


    def scp(self, src, dst,
            ssh_option="-o StrictHostKeyChecking=no -vv"):

        cmd = "/usr/bin/scp.exe {0} {1} {2}".format(ssh_option, src, dst)

        self.run_commandline(cmd, shell_flag=True)

    def run(self):
        """
        """
        self.create_scratch()

        self.copy_input_to_scratch(copy_method=lambda x,y: self.scp(x, y),
                                   dst_url_mapping=lambda x: os.path.normpath("{0}/{1}".format(self.scratch, os.path.basename(x))))

        _maxquant_driver_filename = os.path.normcase("{0}/maxquant_driver.xml".format(self.scratch))

        self.compose_maxquant_driver_file(filename=_maxquant_driver_filename)

        #cmd = r"/cygdrive/c/mxQnt_versions/MaxQuant_1.4.1.2/MaxQuant/bin/MaxQuantCmd.exe -mqpar={0} -ncores={1}".format(_maxquant_driver_filename.replace("/cygdrive/d/", "d:\\\\").replace("/", "\\\\"), 8)
        #cmd = "c:\\\\mxQnt_versions\\\\MaxQuant_1.4.1.2\\\\MaxQuant\\\\bin\\\\MaxQuantCmd.exe -mqpar={0} -ncores={1}".format(_maxquant_driver_filename.replace("/cygdrive/d/", "d:\\\\").replace("/", "\\\\"), 8)


        cmd=r"c:\mxQnt_versions\MaxQuant_1.4.1.2\MaxQuant\bin\MaxQuantCmd.exe -mqpar=d:\scratch_\135076\maxquant_driver.xml -ncores=8"
        self.run_commandline(cmd, shell_flag=False)

        return True


