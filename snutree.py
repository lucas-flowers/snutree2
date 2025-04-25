#!/usr/bin/env python

import sys
from argparse import ArgumentParser

import yaml

from snutree.read import csv
from snutree.core import member, tree
from snutree.write import dot
from snutree.utilities import deep_update

config = None

def setup_args(argv):

    parser = ArgumentParser()

    parser.add_argument(
        '--config-file', '-c',
    )

    return parser.parse_args(argv)


def setup_config(args):
    paths = [args.config_file] # TODO Multiple config files
    dicts = []
    for path in paths:
        with open(path, 'r') as f:
            dicts.append(yaml.safe_load(f))
    return deep_update(*dicts)

def main():

    global config
    args = setup_args(sys.argv[1:])
    config = setup_config(args)
    rows = []
    # TODO Allow the columns to be missing in brothers_not_knights
    for filename in ('sigmanu.csv', 'brothers_not_knights.csv'):
        with open(filename, 'r') as f:
            rows += list(csv.read(f))

    members = member.read(rows, config=config['member'])
    family_tree = tree.create(members, config=config['tree'])
    print(dot.write_str(family_tree, config=config['dot']))


if __name__ == '__main__':
    main()

