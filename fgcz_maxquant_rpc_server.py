    #!/usr/bin/python


import sys
import os
import unittest

import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

from optparse import OptionParser

import time

import subprocess


class FgczMaxquantWrapper:
    """

    """
    config = None
    scratchroot = os.path.normcase(r"d:/scratch")

    def __init__(self):
        if not os.path.isdir(self.scratchroot):
            try:
                os.mkdir(self.scratchroot)
            except:
                print "scratch '{0}' does not exists.".format(self.scratchroot)
                sys.exit(1)
        pass

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

    def print_config(self):
        print self.config

    def add_configuration(self, config):
        self.config = config

    def create_scratch(self):
        # create scratch space
        self.scratch = os.path.normcase(
            "{0}/{1}".format(self.scratchroot, self.config['job_configuration']['workunit_id']))
        if not os.path.isdir(self.scratch):
            try:
                os.mkdir(self.scratch)
            except:
                print "scratch '{0}' does not exists.".format(self.scratch)
                sys.exit(1)

        # copy input to scratch
        try:
            for i in self.config['application']['input'].keys():
                for j in self.config['application']['input'][i]:
                    print j
        except:
            sys.exit(1)

        return True

    def generate_xml(self):
        pass

    def run(self):
        """
        #$maxQuantWindowsFolder\\$MAXQUANTLINUXFOLDERNAME -ncores=8;"
        """

        cmd = 'C:\\Program Files\\mxQnt_versions\\MaxQuant_1.4.1.2\\MaxQuant\\bin\\MaxQuantCmd.exe -mqpar={0} -ncores={1}'.format(
            None, 8)

        print self.run_commandline(cmd)

    def generate_qc_report(self):
        pass

class TestTargetMapping(unittest.TestCase):
    """
    run
        python -m unittest -v fgcz_maxquant_wrapper
    """
    def setUp(self):
        pass

    def test_scp2smb_url_mapping(self):
        #desired_result = os.path.normpath('p1000/Proteomics/TRIPLETOF_1/selevsek_20150119')
        #self.assertTrue(desired_result == map_data_analyst_tripletof_1('p1000\Data\selevsek_20150119'))
        #self.assertTrue(map_data_analyst_tripletof_1('p1000\data\selevsek_20150119') is None)
        pass
        return True

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

    test_config = {'application': {'input': {'QEXACTIVE_2': ['bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs//p1946/Proteomics/QEXACTIVE_2/paolo_20150811_course/20150811_01_Fetuin40fmol.raw', 'bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs//p1946/Proteomics/QEXACTIVE_2/paolo_20150811_course/20150811_02_YPG1.raw', 'bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs//p1946/Proteomics/QEXACTIVE_2/paolo_20150811_course/20150811_03_YPG2_GG.raw', 'bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs//p1946/Proteomics/QEXACTIVE_2/paolo_20150811_course/20150811_04_YPG2_SL.raw', 'bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs//p1946/Proteomics/QEXACTIVE_2/paolo_20150811_course/20150811_05_YPD3.raw', 'bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs//p1946/Proteomics/QEXACTIVE_2/paolo_20150811_course/20150811_06_Fetuin40fmol.raw', 'bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs//p1946/Proteomics/QEXACTIVE_2/paolo_20150811_course/20150811_07_YPD1.raw', 'bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs//p1946/Proteomics/QEXACTIVE_2/paolo_20150811_course/20150811_08_YPD2_SL.raw', 'bfabric@fgczdata.fgcz-net.unizh.ch://srv/www/htdocs//p1946/Proteomics/QEXACTIVE_2/paolo_20150811_course/20150811_09_YPG3.raw']}, 'protocol': 'scp', 'parameters': {}, 'output': ['bfabric@fgczdata.fgcz-net.unizh.ch:/srv/www/htdocs//p1946/bfabric/Proteomics/MaxQuant_Scaffold_LFQ_tryptic_swissprot/2015/2015-09/2015-09-07//workunit_135076//203583.zip']}, 'job_configuration': {'executable': '/home/bfabric/sgeworker/bin/fgcz_sge_MaxQuant_Scaffold_LFQ_fast', 'external_job_id': 46103, 'input': {'QEXACTIVE_2': [{'sample_id': 26524, 'resource_id': 202116, 'extract_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-extract.html?extractId=32622', 'extract_id': 32622, 'resource_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-resource.html?resourceId=202116', 'sample_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-sample.html?sampleId=26524'}, {'sample_id': 26195, 'resource_id': 202115, 'extract_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-extract.html?extractId=32648', 'extract_id': 32648, 'resource_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-resource.html?resourceId=202115', 'sample_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-sample.html?sampleId=26195'}, {'sample_id': 26195, 'resource_id': 202114, 'extract_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-extract.html?extractId=32648', 'extract_id': 32648, 'resource_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-resource.html?resourceId=202114', 'sample_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-sample.html?sampleId=26195'}, {'sample_id': 26195, 'resource_id': 202113, 'extract_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-extract.html?extractId=32648', 'extract_id': 32648, 'resource_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-resource.html?resourceId=202113', 'sample_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-sample.html?sampleId=26195'}, {'sample_id': 26196, 'resource_id': 202112, 'extract_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-extract.html?extractId=32649', 'extract_id': 32649, 'resource_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-resource.html?resourceId=202112', 'sample_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-sample.html?sampleId=26196'}, {'sample_id': 26524, 'resource_id': 202111, 'extract_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-extract.html?extractId=32622', 'extract_id': 32622, 'resource_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-resource.html?resourceId=202111', 'sample_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-sample.html?sampleId=26524'}, {'sample_id': 26196, 'resource_id': 202110, 'extract_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-extract.html?extractId=32649', 'extract_id': 32649, 'resource_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-resource.html?resourceId=202110', 'sample_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-sample.html?sampleId=26196'}, {'sample_id': 26196, 'resource_id': 202109, 'extract_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-extract.html?extractId=32649', 'extract_id': 32649, 'resource_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-resource.html?resourceId=202109', 'sample_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-sample.html?sampleId=26196'}, {'sample_id': 26195, 'resource_id': 202108, 'extract_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-extract.html?extractId=32648', 'extract_id': 32648, 'resource_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-resource.html?resourceId=202108', 'sample_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-sample.html?sampleId=26195'}]}, 'stdout': {'url': '/home/bfabric/sgeworker/logs/workunitid-135076_resourceid-203583.out', 'protocol': 'file', 'resource_id': 203585}, 'output': {'protocol': 'scp', 'ssh_args': '-o StrictHostKeyChecking=no -c arcfour -2 -l bfabric -x', 'resource_id': 203583}, 'stderr': {'url': '/home/bfabric/sgeworker/logs/workunitid-135076_resourceid-203583.err', 'protocol': 'file', 'resource_id': 203584}, 'workunit_url': 'http://fgcz-bfabric.uzh.ch/bfabric/userlab/show-workunit.html?workunitId=135076', 'workunit_id': 135076}}