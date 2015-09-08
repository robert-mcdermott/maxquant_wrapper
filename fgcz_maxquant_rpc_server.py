#!/usr/bin/python


import sys
import os

import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

from optparse import OptionParser


import time

import subprocess

class FgczMaxquantWrapper:
    """

    """
    config = None

    def __init__(self):
        pass

    def run_commandline(self, cmd):

        (pid, return_code) = (None, None)

        tStart = time.time()
        try:
            p = subprocess.Popen(cmd, shell=True)

            pid = p.pid
            return_code = p.wait()

            (out, err) = p.communicate()
            p.terminate()

        except OSError as e:
            msg = "exception|pid={0}|OSError=".format(pid, e)
            print msg

        msg_info = "completed|pid={0}|time={1}|return_code={2}|cmd='{3}'".format(pid, time.time() - tStart, return_code, cmd)
        print msg_info

        print out
        return (return_code)

    def print_config(self):
        print self.config

    def add_configuration(self, config):
        self.config = config
        return True


    def generate_xml(self):
        pass

    def run(self):
        """
        #$maxQuantWindowsFolder\\$MAXQUANTLINUXFOLDERNAME -ncores=8;"
        """

        cmd = "C:\\Program Files\\mxQnt_versions\\MaxQuant_1.4.1.2\\MaxQuant\\bin\\MaxQuantCmd.exe -mqpar={0} -ncores={1}".format(None, 8)


        print self.run_commandline(cmd)

    def generate_qc_report(self):
        pass



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

    server = SimpleXMLRPCServer((options.hostname, 8082))

    server.register_instance(mqw)

    server.serve_forever()
