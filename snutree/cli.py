
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
from argparse import ArgumentParser
from collections import OrderedDict
from pathlib import Path
from . import api, version
from .errors import SnutreeError
from .utilities.logging import setup_logger, logged

def main():
    '''
    Snutree CLI entry point. Run snutree as a CLI program using the
    command-line arguments provided to the running script. Catch and log all
    errors that occur.
    '''

    try:
        invoke()

    # Expected errors
    except SnutreeError as e:
        logging.getLogger('snutree').error(e)
        sys.exit(1)

    # Top-level catching for unexpected errors
    except Exception as e: # pylint: disable=broad-except
        logging.getLogger('snutree').error('Unexpected error.', exc_info=True)
        sys.exit(1)

@logged
def invoke(argv=None):
    '''
    Run snutree using the provided list of command-line arguments. By default,
    the running script's actual command-line arguments are used.
    '''
    log_keys = {'verbose', 'debug', 'quiet', 'log_path'}
    args = vars(parse_args(argv))
    args_log = {k : v for k, v in args.items() if k in log_keys}
    args_api = {k : v for k, v in args.items() if k not in log_keys}
    setup_logger(**args_log)
    api.generate(**args_api)

def parse_args(argv=None):
    '''
    Parse and return the program command-line arguments. If the `argv` variable
    is provided, arguments are read from that list instead of using the true
    command-line arguments.
    '''
    parser = ArgumentParser(prog='snutree', description=__doc__)
    for args, kwargs in options.values():
        parser.add_argument(*args, **kwargs)
    parsed = parser.parse_args(argv)
    return parsed

class AllowedModules:
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

    def __add__(self, other):
        '''
        Concatenation happens only with the module names, not the pattern.
        '''
        return self.module_names + other

    __radd__ = __add__

    def __iter__(self):
        yield from self.module_names
        if self.glob is not None:
            yield self.glob

    def __str__(self):
        return '{{{allowed}}}'.format(allowed=','.join(self))

# Allowable values for different arguments
CHOICES_READER = AllowedModules(api.BUILTIN_READERS, pattern=None)
CHOICES_SCHEMA = AllowedModules(api.BUILTIN_SCHEMAS, pattern='*.py')
CHOICES_WRITER = AllowedModules(api.BUILTIN_WRITERS, pattern='*.py')

# In Python 3.6, options can just be set as a dict and the order will be as
# expected. (We need a dict now to interact with Gooey.)
options = OrderedDict([

    ('input', (['input_files'], {
        'metavar' : '<input>',
        'type' : argparse.FileType('r', encoding='utf-8'),
        'nargs' : '*',
        'help' : "an input file path or '-' for stdin; default is stdin",
    })),

    ('output', (['-o', '--output'], {
        'metavar' : '<path>',
        'dest' : 'output_path',
        'type' : Path,
        'help' : 'the output file; default is stdout'
    })),

    ('from', (['-f', '--from'], {
        'metavar' : '<filetype>',
        'dest' : 'input_format',
        'choices' : CHOICES_READER,
        'help' : 'expected filetype of stdin, which must be one of {readers}; default is csv'.format(readers=CHOICES_READER),
    })),

    ('to', (['-t', '--to'], {
        'metavar' : '<filetype>',
        'dest' : 'output_format',
        'help' : "filetype of the output file, which must be supported by the writer; default  is the output file's extension (if known) or 'dot'"
    })),

    ('schema', (['-m', '--schema'], {
        'metavar' : '<schema>',
        'choices' : CHOICES_SCHEMA,
        'help' : "member table schema, which must be in {schemas}; default is 'basic'".format(schemas=CHOICES_SCHEMA),
    })),

    ('writer', (['-w', '--writer'], {
        'metavar' : '<writer>',
        'choices' : CHOICES_WRITER,
        'help' : 'writer module, which must be in {writers}; default is a guess based on the output file format'.format(writers=CHOICES_WRITER)
    })),

    ('config', (['-c', '--config'], {
        'metavar' : '<path>',
        'dest' : 'config_files',
        'type' : argparse.FileType('r', encoding='utf-8'),
        'default' : [],
        'action' : 'append',
        'help' : 'configuration file <path(s)>; files listed earlier override later ones',
    })),

    ('seed', (['-S', '--seed'], {
        'metavar' : '<int>',
        'type' : int,
        'help' : 'random number generator seed, for moving tree nodes around in a repeatable way'
    })),

    ('log', (['-l', '--log'], {
        'metavar' : '<path>',
        'dest' : 'log_path',
        'type' : Path,
        'help' : 'write logger output to the file at <path>'
    })),

    ('quiet', (['-q', '--quiet'], {
        'action' : 'store_true',
        'help' : 'write only errors to stderr; suppress warnings'
    })),

    ('verbose', (['-v', '--verbose'], {
        'action' : 'store_true',
        'help' : 'print more information to stderr'
    })),

    ('debug', (['-d', '--debug'], {
        'action' : 'store_true',
        'help' : 'print debug-level information to stderr'
    })),

    ('version', (['-V', '--version'], {
        'action' : 'version',
        'version' : version,
    })),

])

