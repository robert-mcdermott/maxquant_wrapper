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

