#!/usr/bin/env python

from pathlib import Path
from setuptools_scm import get_version
from snutree import api
from snutree.readers import sql
from snutree.schemas import sigmanu
from snutree.writers import dot
from snutree.cerberus import describe_schema

with Path('README_TEMPLATE.txt').open('r') as f:
    readme = f.read()

with Path('README.txt').open('w+') as f:
    f.write(readme.format(
        CONFIG_API=describe_schema(api.CONFIG_SCHEMA, level=2),
        CONFIG_READER_SQL=describe_schema(sql.CONFIG_SCHEMA, level=2),
        CONFIG_SCHEMA_SIGMANU=describe_schema(sigmanu.CONFIG_SCHEMA, level=2),
        CONFIG_WRITER_DOT=describe_schema(dot.CONFIG_SCHEMA, level=2),
        VERSION=get_version(root=Path(__file__).parent),
        ))

