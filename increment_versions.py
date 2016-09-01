#!/usr/bin/env python

import argparse
import logging
import os
import sys
import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.INFO)

# Maven namespace
MVN_NS = 'http://maven.apache.org/POM/4.0.0'

def parse_arguments(arguments):
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str)
    return parser.parse_args(arguments)

def find_mvn_property(current_element, prop):
    return current_element.find("{%s}%s" % (MVN_NS, prop))

def get_modules(tree, file_name):
    root = tree.getroot()
    modules_element = find_mvn_property(root, "modules")

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
    current_version = find_mvn_property(root, "version")

    if current_version is not None:
        # Increment the version
        current_version.text = increment_version(current_version.text)

        return True
    else:
        return False

def update_parent_version(tree):
    root = tree.getroot()
    parent = find_mvn_property(root, "parent")
    version = find_mvn_property(parent, "version")

    version.text = increment_version(version.text)


if __name__ == "__main__":
    arguments = parse_arguments(sys.argv[1:])

    ET.register_namespace("", MVN_NS)
    parent = ET.parse(arguments.file)

    logging.info("Updating versions for {}".format(arguments.file))
    if not update_version(parent):
        logging.error("Could not update parent pom version! Exiting")
        sys.exit(1)

    # Update the saved file
    parent.write(arguments.file)

    child_pom_files = get_modules(parent, arguments.file)
    logging.info("Found submodules {}".format(child_pom_files))
    for child_file in child_pom_files:
        child = ET.parse(child_file)
        logging.info("Updating version for {}".format(child_file))
        update_version(child)
        update_parent_version(child)
        child.write(child_file)
