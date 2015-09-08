# !/usr/bin/python


import sys
import os
import shutil
import unittest

import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

from optparse import OptionParser

import time

import subprocess

import re

class FgczMaxquantWrapper:
    """

    """
    config = None
    scratchroot = os.path.normcase(r"d:/scratch")
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

    def run_commandline(self, cmd, shell_flag=True):
        (pid, return_code) = (None, None)

        tStart = time.time()

        try:
            p = subprocess.Popen(cmd, shell=shell_flag)

            pid = p.pid
            return_code = p.wait()

            (out, err) = p.communicate()
            p.terminate()

        except OSError as e:
            msg = "exception|pid={0}|OSError=".format(pid, e)
            print msg

        msg_info = "completed|pid={0}|time={1}|return_code={2}|cmd='{3}'" \
            .format(pid, time.time() - tStart, return_code, cmd)
        print msg_info

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
            print result_url
            return (result_url)
        else:
            return None

    def print_config(self):
        print self.config

    def add_configuration(self, config):
        self.config = config

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
                print "scratch '{0}' does not exists.".format(self.scratch)
                raise

        return True

    @property
    def copy_input_to_scratch(self):
        """
        make input resources available on scratch
        """

        # copy input to scratch
        _input = self.config['application']['input']

        try:
            for i in _input.keys():
                _fsrc_fdst = map(lambda x: (self.map_url_scp2smb(x), os.path.normcase("{0}/{1}".format(self.scratch, os.path.basename(x))) ),
                           _input[i])


                for (_fsrc, _fdst) in _fsrc_fdst:
                    if os.path.isfile(_fdst):
                        # TODO(cp): file cmp
                        print "YEAH\n'{0}' is already there.\ncontinue ...".format(_fdst)
                    else:
                        try:
                            shutil.copyfile(_fsrc, _fdst)
                        except:
                            print "ERROR: fail copy failed."
                            raise

        except:
            raise

        return True

    def generate_xml(self):
        pass


    def run(self):
        """
        #$maxQuantWindowsFolder\\$MAXQUANTLINUXFOLDERNAME -ncores=8;"
                #cmd = 'C:\\Program Files\\mxQnt_versions\\MaxQuant_1.4.1.2\\MaxQuant\\bin\\MaxQuantCmd.exe -mqpar={0} -ncores={1}'.format(
        #    None, 8)
        #print self.run_commandline(cmd)

        """

        self.create_scratch()
        self.copy_input_to_scrach()

    def generate_qc_report(self):
        pass


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


if __name__ == "__main__":
    parser = OptionParser(usage="usage: %prog -h <hostname>",
                          version="%prog 1.0")

    parser.add_option("-n", "--hostname",
                      type='string',
                      action="store",
                      dest="hostname",
                      default="localhost",
                      help="provide a hostname")

    (options, args) = parser.parse_args()

    mqw = FgczMaxquantWrapper()

    server = SimpleXMLRPCServer((options.hostname, 8084))

    server.register_instance(mqw)

    server.serve_forever()

