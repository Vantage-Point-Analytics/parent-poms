#!/usr/bin/env python

import argparse
import logging
import os
import sys
import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.INFO)

def parse_arguments(arguments):
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str)
    return parser.parse_args(arguments)

def get_modules(tree, file_name):
    root = tree.getroot()
    modules_element = root.find("{%s}modules" %  MVN_NS)

    if modules_element is not None:
        base_dir = os.path.dirname(os.path.realpath(file_name))
        return [os.path.join(base_dir, x.text, "pom.xml") for x in modules_element.getchildren()]
    else:
        return []

def increment_version(old_version):
    new_version = old_version.split(".")
    new_version[-1] = str(int(new_version[-1]) + 1)

    return ".".join(new_version)

def update_version(tree):
    root = tree.getroot()
    current_version = root.find("{%s}version" % MVN_NS)

    if current_version is not None:
        # Increment the version
        current_version.text = increment_version(current_version.text)

        # Update the saved file
        tree.write(arguments.file)

        return True
    else:
        return False

# Maven namespace
MVN_NS = 'http://maven.apache.org/POM/4.0.0'

if __name__ == "__main__":
    arguments = parse_arguments(sys.argv[1:])

    ET.register_namespace("", MVN_NS)
    parent = ET.parse(arguments.file)

    logging.info("Updating versions for {}".format(arguments.file))
    if not update_version(parent):
        logging.error("Could not update parent pom version! Exiting")
        sys.exit(1)

    child_pom_files = get_modules(parent, arguments.file)
    logging.info("Found submodules {}".format(child_pom_files))
    for child_file in child_pom_files:
        child = ET.parse(child_file)
        logging.info("Updating version for {}".format(child_file))
        if not update_version(child):
            logging.warn("Child pom {} had no version to update".format(child_file))
