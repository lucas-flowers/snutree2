#!/usr/bin/env python

import sys
from pathlib import Path
from textwrap import indent
from click.testing import CliRunner
from rstcheck import check
from snutree import api
from snutree.cli import cli
from snutree.readers import csv, sql, dot
from snutree.schemas import sigmanu
from snutree.writers import dot
from snutree.cerberus import describe_schema

def main():

    with Path('README_TEMPLATE.txt').open('r') as f:
        template = f.read()

    readme = template.format(
            CLI_HELP=indent(CliRunner().invoke(cli, ['--help']).output, ' '*4),
            CONFIG_API=describe_schema(api.CONFIG_SCHEMA, level=2),
            CONFIG_READER_CSV=describe_schema(csv.CONFIG_SCHEMA, level=2),
            CONFIG_READER_SQL=describe_schema(sql.CONFIG_SCHEMA, level=2),
            CONFIG_READER_DOT=describe_schema(dot.CONFIG_SCHEMA, level=2),
            CONFIG_SCHEMA_SIGMANU=describe_schema(sigmanu.CONFIG_SCHEMA, level=2),
            CONFIG_WRITER_DOT=describe_schema(dot.CONFIG_SCHEMA, level=2),
            )

    errors = '\n'.join(f'Line {N}: {error}' for N, error in check(readme))
    if errors:
        print('Did not write README. Bad format:', file=sys.stderr)
        print(errors, file=sys.stderr)
        sys.exit(1)

    with Path('README.txt').open('w+') as f:
        f.write(readme)

if __name__ == '__main__':
    main()



