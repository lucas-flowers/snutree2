#!/usr/bin/env python3

'''
Wrapper for running the fmaily tree program through a simple GUI.
'''

from snutree.gui import main

# These help pyinstaller find the builtin module plugins (see the other TODO in
# the spec file). TODO: Find a better way to do this.
from snutree.readers import csv, dot, sql
from snutree.schemas import basic, chapter, keyed, sigmanu
from snutree.writers import dot, stats, table

if __name__ == '__main__':
    main()

