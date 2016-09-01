#!/usr/bin/env python

import argparse
import sys
import xml.etree.ElementTree as ET

def parse_arguments(arguments):
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str)
    return parser.parse_args(arguments)

def increment_version(old_version):
    new_version = old_version.split(".")
    new_version[-1] = str(int(new_version[-1]) + 1)

    return ".".join(new_version)

# Maven namespace
MVN_NS = 'http://maven.apache.org/POM/4.0.0'

if __name__ == "__main__":
    arguments = parse_arguments(sys.argv[1:])

    ET.register_namespace("", MVN_NS)
    tree = ET.parse(arguments.file)
    root = tree.getroot()
    current_version = root.find("{%s}version" % MVN_NS)

    import pdb; pdb.set_trace() 
    # Increment the version
    current_version.text = increment_version(current_version.text)

    # Update the saved file
    tree.write(arguments.file)
