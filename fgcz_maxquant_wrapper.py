#!/usr/bin/python


import sys
import os
import shutil
import unittest

import time
import subprocess
import re

import logging
import logging.handlers
import pprint

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
    this class does
        - stage the input data
        - compose a maxquant driver xml file adapted to the FGCZ infrastructure
        - run maxquant
        - stage the output data

    staging:
        - can be done by using samba or ssh
        - the class can be executed on the python shell or via rpc

    logging:
        - is done by a general log server

    input:
        - a python data structure containing all information

    note: this class is supposed to be run on a Microsoft Windows OS

    TODO(cp,wew): the stagign and exec methods would be better separated into a infrastructure class
    """

    """
  input:
    QEXACTIVE_2:
    - bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs//p1946/Proteomics/QEXACTIVE_2/paolo_20150811_course/20150811_01_Fetuin40fmol.raw
    - bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs//p1946/Proteomics/QEXACTIVE_2/paolo_20150811_course/20150811_02_YPG1.raw
    - bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs//p1946/Proteomics/QEXACTIVE_2/paolo_20150811_course/20150811_03_YPG2_GG.raw
    - bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs//p1946/Proteomics/QEXACTIVE_2/paolo_20150811_course/20150811_04_YPG2_SL.raw
    - bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs//p1946/Proteomics/QEXACTIVE_2/paolo_20150811_course/20150811_05_YPD3.raw
    - bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs//p1946/Proteomics/QEXACTIVE_2/paolo_20150811_course/20150811_06_Fetuin40fmol.raw
    - bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs//p1946/Proteomics/QEXACTIVE_2/paolo_20150811_course/20150811_07_YPD1.raw
    - bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs//p1946/Proteomics/QEXACTIVE_2/paolo_20150811_course/20150811_08_YPD2_SL.raw
    - bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs//p1946/Proteomics/QEXACTIVE_2/paolo_20150811_course/20150811_09_YPG3.raw
  output:
  - bfabric@fgczdata.fgcz-net.unizh.ch:/srv/www/htdocs//p1946/bfabric/Proteomics/MaxQuant_Scaffold_LFQ_tryptic_swissprot/2015/2015-09/2015-09-07//workunit_135076//203583.zip
  parameters: {}
  protocol: scp
    """

    config = None
    outputurl = None
    scratchroot = os.path.normcase(r"d:\scratch_")
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
        """

        :param cmd:
        :param shell_flag:
        :return:
        """
        (pid, return_code) = (None, None)

        (out, err)=("", "")
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
            print err
            print out
            raise

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
        print "------"
        pp = pprint.PrettyPrinter(width=70)
        pp.pprint(self.config)
        return True

    def add_config(self, config):
        self.config = config
        return True

    def add_outputurl(self, url=None):
        """

        :param url:
        :return:
        """
        self.outputurl = url
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

    def scp(self, src, dst,
            scp_cmd=r"C:\Program Files\fgcz\pscp.exe",
            scp_option=r"-scp -i C:\Users\administrator.FGCZ-NET\.ssh\id_rsa.ppk"
            ):
        """
         this is the scp wrapper for data staging

        :param src:
        :param dst:
        :param scp_cmd:
        :param scp_option:
        :return:
        """

        cmd = "{0} {1} {2} {3}".format(scp_cmd, scp_option, src, dst)

        self.run_commandline(cmd, shell_flag=False)

        return (True)

    def copy_input_to_scratch(self,
                              copy_method=lambda s,t: shutil.copyfile(s, t),
                              src_url_mapping=lambda x: x,
                              dst_url_mapping=lambda x: os.path.basename(x)):
        """
         make input resources available on scratch

         NOTE: we assume if the file is already in place it is identical to the src file.


        :param copy_method:
        :param src_url_mapping:
        :param dst_url_mapping:
        :return:
        """


        _input = self.config['application']['input']

        try:
            self._fsrc_fdst = []
            for i in _input.keys():
                self._fsrc_fdst = self._fsrc_fdst + map(lambda x: (src_url_mapping(x), dst_url_mapping(x)), _input[i])


            for (_fsrc, _fdst) in self._fsrc_fdst:
                if os.path.isfile(_fdst):
                    logger.info("'{0}' is already there.".format(_fdst))
                    pass
                else:
                    try:
                        logger.info("copy '{0}' from '{1}' ...".format(_fdst, _fsrc))
                        copy_method(_fsrc, _fdst)
                    except:
                        print "ERROR: fail copy failed."
                        raise

        except:
            logger.info("copying failed")
            raise

        return True

    def compose_maxquant_driver_file(self, filename=None):
        assert isinstance(filename, basestring)
        fasta_filename = None

        try:
            fasta_filename = self.config['application']['input']['parameters']['FASTA']

        except:
            fasta_filename = r"D:\MaxQuantDBs\fgcz_swissprot_20121031.fasta"

        fasta_filename = os.path.normpath((os.path.normcase(fasta_filename))

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
    <string>{5}</string>
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
           "\n".join(map(lambda x: "\t<int>0</int>", self._fsrc_fdst)),
           fasta_filename)

        try:
            with open(filename, "w") as f:
                logger.info("writing '{0}' ...".format(filename))
                f.write(_xml)
        except:
            logger.info("writing maxquant driver file '{0}' failed.".format(filename))
            raise

        return True



    """
        the following function have to be adapted
    """
    def stage_input(self):
        """

        :return:
        """

        logger.info("stage input data")
        self.copy_input_to_scratch(copy_method=lambda x, y: self.scp(x, y),
                                   dst_url_mapping=lambda x: os.path.normpath(r"{0}\{1}".format(self.scratch,
                                                                                                os.path.basename(x))))

    def run_maxquant(self,
                     cmd=r"C:\Program Files\fgcz\mxQnt_versions\MaxQuant_1.4.1.2\MaxQuant\bin\MaxQuantCmd.exe",
                     ncores=8):


        logger.info("run maxquant")

        mqpar_filename = os.path.normcase(r"{0}\maxquant_driver.xml".format(self.scratch))

        self.compose_maxquant_driver_file(filename=mqpar_filename)


        self.run_commandline("{0} -mqpar={1} -ncores={2}".format(cmd, mqpar_filename, ncores),
                             shell_flag=False)

        return True


    def stage_output(self):
        """
            zip all usefull output filed and copy it to an file exchange server
        :return:
        """

        logger.info("stage output")
        zip_cmd = r"C:\Program Files\7-zip\7z.exe"

        zip_file = "{0}.zip".format(self.scratch)
        self.run_commandline("{0} a {1} {2}".format(zip_cmd, zip_file, self.scratch), shell_flag=False)


        if self.outputurl:
            self.scp(src=zip_file, dst=self.outputurl)

        return True

    def clean(self):
        """
            clean scratch space if no errors
        """
        logger.info("clean is not implemeted yet")
        pass

    def run(self):
        """
            this is the main method of the class
        """
        self.create_scratch()
        self.stage_input()
        self.run_maxquant()
        self.stage_output()
        self.clean()

        return "EXCHAGNGE URL"

class TestTargetMapping(unittest.TestCase):
    """
    This is a class doing testing on a real infrastructure. Ensure that the SAN is available
    (> net use s: \\fgcz-s-021.uzh.ch\data ...)

    run
        python -m unittest -v fgcz_maxquant_wrapper
    """


    test_config = {'application': {'input': {'QEXACTIVE_2': [
        'bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs//p1946/Proteomics/QEXACTIVE_2/paolo_20150811_course/20150811_01_Fetuin40fmol.raw',
        'bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs//p1946/Proteomics/QEXACTIVE_2/paolo_20150811_course/20150811_02_YPG1.raw',
        'bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs//p1946/Proteomics/QEXACTIVE_2/paolo_20150811_course/20150811_03_YPG2_GG.raw',
        'bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs//p1946/Proteomics/QEXACTIVE_2/paolo_20150811_course/20150811_04_YPG2_SL.raw',
        'bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs//p1946/Proteomics/QEXACTIVE_2/paolo_20150811_course/20150811_05_YPD3.raw',
        'bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs//p1946/Proteomics/QEXACTIVE_2/paolo_20150811_course/20150811_06_Fetuin40fmol.raw',
        'bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs//p1946/Proteomics/QEXACTIVE_2/paolo_20150811_course/20150811_07_YPD1.raw',
        'bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs//p1946/Proteomics/QEXACTIVE_2/paolo_20150811_course/20150811_08_YPD2_SL.raw',
        'bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs//p1946/Proteomics/QEXACTIVE_2/paolo_20150811_course/20150811_09_YPG3.raw']},
                                   'protocol': 'scp', 'parameters': {}, 'output': [
            'bfabric@fgczdata.fgcz-net.unizh.ch:/srv/www/htdocs//p1946/bfabric/Proteomics/MaxQuant_Scaffold_LFQ_tryptic_swissprot/2015/2015-09/2015-09-07//workunit_135076//203583.zip']},
                   'job_configuration': {
                       'executable': '/home/bfabric/sgeworker/bin/fgcz_sge_MaxQuant_Scaffold_LFQ_fast',
                       'external_job_id': 46103, 'input': {'QEXACTIVE_2': [{'sample_id': 26524, 'resource_id': 202116,
                                                                            'extract_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-extract.html?extractId=32622',
                                                                            'extract_id': 32622,
                                                                            'resource_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-resource.html?resourceId=202116',
                                                                            'sample_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-sample.html?sampleId=26524'},
                                                                           {'sample_id': 26195, 'resource_id': 202115,
                                                                            'extract_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-extract.html?extractId=32648',
                                                                            'extract_id': 32648,
                                                                            'resource_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-resource.html?resourceId=202115',
                                                                            'sample_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-sample.html?sampleId=26195'},
                                                                           {'sample_id': 26195, 'resource_id': 202114,
                                                                            'extract_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-extract.html?extractId=32648',
                                                                            'extract_id': 32648,
                                                                            'resource_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-resource.html?resourceId=202114',
                                                                            'sample_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-sample.html?sampleId=26195'},
                                                                           {'sample_id': 26195, 'resource_id': 202113,
                                                                            'extract_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-extract.html?extractId=32648',
                                                                            'extract_id': 32648,
                                                                            'resource_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-resource.html?resourceId=202113',
                                                                            'sample_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-sample.html?sampleId=26195'},
                                                                           {'sample_id': 26196, 'resource_id': 202112,
                                                                            'extract_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-extract.html?extractId=32649',
                                                                            'extract_id': 32649,
                                                                            'resource_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-resource.html?resourceId=202112',
                                                                            'sample_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-sample.html?sampleId=26196'},
                                                                           {'sample_id': 26524, 'resource_id': 202111,
                                                                            'extract_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-extract.html?extractId=32622',
                                                                            'extract_id': 32622,
                                                                            'resource_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-resource.html?resourceId=202111',
                                                                            'sample_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-sample.html?sampleId=26524'},
                                                                           {'sample_id': 26196, 'resource_id': 202110,
                                                                            'extract_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-extract.html?extractId=32649',
                                                                            'extract_id': 32649,
                                                                            'resource_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-resource.html?resourceId=202110',
                                                                            'sample_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-sample.html?sampleId=26196'},
                                                                           {'sample_id': 26196, 'resource_id': 202109,
                                                                            'extract_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-extract.html?extractId=32649',
                                                                            'extract_id': 32649,
                                                                            'resource_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-resource.html?resourceId=202109',
                                                                            'sample_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-sample.html?sampleId=26196'},
                                                                           {'sample_id': 26195, 'resource_id': 202108,
                                                                            'extract_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-extract.html?extractId=32648',
                                                                            'extract_id': 32648,
                                                                            'resource_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-resource.html?resourceId=202108',
                                                                            'sample_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-sample.html?sampleId=26195'}]},
                       'stdout': {'url': '/home/bfabric/sgeworker/logs/workunitid-135076_resourceid-203583.out',
                                  'protocol': 'file', 'resource_id': 203585}, 'output': {'protocol': 'scp',
                                                                                         'ssh_args': '-o StrictHostKeyChecking=no -c arcfour -2 -l bfabric -x',
                                                                                         'resource_id': 203583},
                       'stderr': {'url': '/home/bfabric/sgeworker/logs/workunitid-135076_resourceid-203583.err',
                                  'protocol': 'file', 'resource_id': 203584},
                       'workunit_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-workunit.html?workunitId=135076',
                       'workunit_id': 135076}}

    mqw = FgczMaxquantWrapper(config=test_config)

    def setUp(self):
        pass

    def test_map_url_scp2smb(self):
        # desired_result = os.path.normpath('p1000/Proteomics/TRIPLETOF_1/selevsek_20150119')
        # self.assertTrue(desired_result == map_data_analyst_tripletof_1('p1000\Data\selevsek_20150119'))
        # self.assertTrue(map_data_analyst_tripletof_1('p1000\data\selevsek_20150119') is None)
        _input = self.test_config['application']['input']
        for input_application in _input.keys():
            map(lambda x: self.assertTrue(os.path.isfile(self.mqw.map_url_scp2smb(x) )),
                _input[input_application])

    def test_create_scratch(self):
        self.assertTrue(self.mqw.create_scratch())

    def test_copy_input_to_scratch(self):
        self.assertTrue(self.mqw.create_scratch())
        self.assertTrue(self.mqw.copy_input_to_scratch)

