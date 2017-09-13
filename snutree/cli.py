
'''
Visualizes big-little brother/sister relationships in Greek-letter
organizations. Input file data is read from stdin and/or any provided
positional <input> arguments. Each input <filetype> has a corresponding reader,
which converts the file into a table of the given <schema> and adds it to the
rest of the input data. The <schema> module then turns the the resulting table
into a tree data structure. The tree is processed and finally written to the
output <path> using the given <writer> and output <filetype>. Additional
options can be provided in configuration files.
'''

import logging
import sys
import argparse
from pathlib import Path
from . import api, version
from .errors import SnutreeError
from .logging import setup_logger, logged

class Modules:
    '''
    Collection of allowable module names. If `pattern` is provided to the
    constructor, any file path that matches the glob pattern will be considered
    allowable.
    '''

    def __init__(self, module_names, pattern=None):
        self.module_names = module_names
        self.glob = pattern

    def __contains__(self, item):
        if item in self.module_names:
            return True
        elif self.glob:
            return Path(item).match(self.glob)
        else:
            return False

    def __iter__(self):
        yield from self.module_names
        if self.glob is not None:
            yield self.glob

    def __str__(self):
        return '{{{allowed}}}'.format(allowed=','.join(self))

# Allowable values for different arguments
CHOICES_READER = Modules(api.BUILTIN_READERS, pattern=None)
CHOICES_SCHEMA = Modules(api.BUILTIN_SCHEMAS, pattern='*.py')
CHOICES_WRITER = Modules(api.BUILTIN_WRITERS, pattern='*.py')

# Command-line options for argparse
options = [

    (('input_files',), {
        'metavar' : '<input>',
        'type' : argparse.FileType('r'),
        'nargs' : '*',
        'help' : "an input file path or '-' for stdin; default is stdin",
    }),

    (('-o', '--output',), {
        'metavar' : '<path>',
        'dest' : 'output_path',
        'type' : Path,
        'help' : 'the output file; default is stdout'
    }),

    (('-f', '--from',), {
        'metavar' : '<filetype>',
        'dest' : 'input_format',
        'choices' : CHOICES_READER,
        'help' : 'expected filetype of stdin, which must be one of {readers}; default is csv'.format(readers=CHOICES_READER),
    }),

    (('-t', '--to',), {
        'metavar' : '<filetype>',
        'dest' : 'output_format',
        'help' : "filetype of the output file, which must be supported by the writer; default  is the output file's extension (if known) or 'dot'"
    }),

    (('-m', '--schema',), {
        'metavar' : '<schema>',
        'choices' : CHOICES_SCHEMA,
        'help' : "member table schema, which must be in {schemas}; default is 'basic'".format(schemas=CHOICES_SCHEMA),
    }),

    (('-w', '--writer',), {
        'metavar' : '<writer>',
        'choices' : CHOICES_WRITER,
        'help' : 'writer module, which must be in {writers}; default is a guess based on the output file format'.format(writers=CHOICES_WRITER)
    }),

    (('-c', '--config',), {
        'metavar' : '<path>',
        'dest' : 'config_paths',
        'type' : Path,
        'default' : [],
        'action' : 'append',
        'help' : 'configuration file <path(s)>; files listed earlier override later ones',
    }),

    (('-S', '--seed',), {
        'metavar' : '<int>',
        'type' : int,
        'help' : 'random number generator seed, for moving tree nodes around in a repeatable way'
    }),

    (('-l', '--log',), {
        'metavar' : '<path>',
        'dest' : 'log_path',
        'type' : Path,
        'help' : 'write logger output to the file at <path>'
    }),

    (('-q', '--quiet',), {
        'action' : 'store_true',
        'help' : 'write only errors to stderr; suppress warnings'
    }),

    (('-v', '--verbose',), {
        'action' : 'store_true',
        'help' : 'print more information to stderr'
    }),

    (('-d', '--debug',), {
        'action' : 'store_true',
        'help' : 'print debug-level information to stderr'
    }),

    (('-V', '--version',), {
        'action' : 'version',
        'version' : version,
    }),

]

def parse_args(args=None):
    '''
    Parse and return the program command-line arguments. If the `args` variable
    is provided, arguments are read from that dictionary instead of using the
    true command-line arguments.
    '''
    parser = argparse.ArgumentParser(prog='snutree', description=__doc__)
    for names, parameters in options:
        parser.add_argument(*names, **parameters)
    return parser.parse_args(args)

def main():
    '''
    Snutree program entrypoint.
    '''

    logger = logging.getLogger('snutree')
    kwargs = vars(parse_args())

    try:
        cli(**kwargs)

    # Expected errors
    except SnutreeError as e:
        logger.error(e)
        sys.exit(1)

    # Top-level catching for unexpected errors
    except Exception as e: # pylint: disable=broad-except
        logger.error('Unexpected error.', exc_info=True)
        sys.exit(1)

@logged
def cli(verbose, debug, quiet, log_path, *args, **kwargs):
    setup_logger(verbose, debug, quiet, log_path)
    return api.generate(*args, **kwargs)

