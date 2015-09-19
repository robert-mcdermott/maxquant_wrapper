#!/usr/bin/python


import sys
import os
import yaml
import xmlrpclib


if __name__ == "__main__":
    try:
        with open(sys.argv[1], 'r') as f:
            content = f.read()
            
        job_config = yaml.load(content)

    except:
        print "ERROR: exit 1"
        raise

    try:
        proxy = xmlrpclib.ServerProxy("http://130.60.81.79:8084/")
    except:
        print "could not start rpc proxy"
        raise

    proxy.add_configuration(job_config)
    proxy.run()

    #print job_config
    #cmd = r"C:\Program Files\mxQnt_versions\MaxQuant_1.4.1.2\MaxQuant\bin\MaxQuantCmd.exe -mqpar={0} -ncores={1}".format(r"s:\cp_temp\maxQuantDriver.xml", 8)
    #r = proxy.run_commandline(cmd, False)
    #print r
