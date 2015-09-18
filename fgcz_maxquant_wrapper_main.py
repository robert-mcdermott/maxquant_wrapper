#!/usr/bin/python


import sys
import os

import yaml

from optparse import OptionParser
import fgcz_maxquant_wrapper


if __name__ == "__main__":
    """
    """


    parser = OptionParser(usage="usage: %prog -y <yaml formated config file>",
                          version="%prog 1.0")

    parser.add_option("-y", "--yaml",
                      type='string',
                      action="store",
                      dest="yaml_filename",
                      default=None,
                      help="config file.yaml")


    (options, args) = parser.parse_args()

    if not os.path.isfile(options.yaml_filename):
        print "ERROR: no such file '{0}'".format(options.yaml_filename)
        sys.exit(1)
    try:
        with open(options.yaml_filename, 'r') as f:
            content = f.read()
        job_config = yaml.load(content)

    except:
        print "ERROR: exit 1"
        raise

    sys.exit(1)

    #mqw = FgczMaxquantWrapper()
    #mqw.add_configuration(job_config)
    #mqw.run()

