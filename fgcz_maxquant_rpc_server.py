#!/usr/bin/python


import sys
import os

import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer


class FgczMaxquantWrapper:
    def __init__(self):
        pass

    def load_config(self, config):
        print config
        #self.config = config

    def print_config(self):
        print self.config

    def add(self, a, b):
        print b
        return 1


if __name__ == "__main__":
    mqw = FgczMaxquantWrapper()

    server = SimpleXMLRPCServer(("130.60.81.113", 8082))
    server.register_instance(mqw)
    server.serve_forever()
