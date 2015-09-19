#!/usr/bin/python


import sys
import os
import yaml
import xmlrpclib
from optparse import OptionParser



if __name__ == "__main__":

    parser = OptionParser(usage="usage: %prog -h <hostname>",
                          version="%prog 1.0")


    parser.add_option("-c", "--config",
                      type='string',
                      action="store",
                      dest="config_filename",
                      default=None,
                      help="provide a yaml formated config file")

    parser.add_option("-n", "--hostname",
                      type='string',
                      action="store",
                      dest="hostname",
                      default="localhost",
                      help="provide a hostname")

    parser.add_option("-p", "--port",
                      type='int',
                      action="store",
                      dest="port",
                      default="8084",
                      help="provide a port number")

    parser.add_option("-o", "--outputurl",
                      type='string',
                      action="store",
                      dest="outputurl",
                      default="bfabric@fgcz-s-021.uzh.ch:/scratch/dump.zip",
                      help="provide a output url")



    (options, args) = parser.parse_args()

    if options.config_filename is None:
        print "ERROR: provide a config filename."
        sys.exit(1)

    try:
        with open(options.config_filename, 'r') as f:
            content = f.read()
            
        job_config = yaml.load(content)

    except:
        print "ERROR: parsing file '{0}' failed.".format(options.config_filename)
        raise


    try:
        maxquant_wrapper = xmlrpclib.ServerProxy("http://{0}:{1}/".format(options.hostname, options.port))
    except:
        print "ERROR: failed starting rpc proxy client"
        raise

    maxquant_wrapper.add_config(job_config)
    maxquant_wrapper.add_outputurl(options.outputurl)

    maxquant_wrapper.print_config()

    print maxquant_wrapper.run()

    #print job_config
    #cmd = r"C:\Program Files\mxQnt_versions\MaxQuant_1.4.1.2\MaxQuant\bin\MaxQuantCmd.exe -mqpar={0} -ncores={1}".format(r"s:\cp_temp\maxQuantDriver.xml", 8)
    #r = proxy.run_commandline(cmd, False)
    #print r
