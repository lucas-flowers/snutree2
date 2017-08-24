import logging
import sys
from functools import wraps
from pathlib import Path
import click
from . import api, version
from .errors import SnutreeError
from .logging import setup_logger, logged

def main():
    '''
    Run the command-line version of the program.
    '''

    logger = logging.getLogger('snutree')

    try:
        # pylint: disable=no-value-for-parameter
        cli()

    # Expected errors
    except SnutreeError as e:
        logger.error(e)
        sys.exit(1)

    # Unexpected errors
    except Exception as e:
        logger.critical('Unexpected error.', exc_info=True)
        sys.exit(1)

def path_callback(context, parameter, value):
    if value is None:
        return None
    elif isinstance(value, str):
        return Path(value) if value is not None else None
    else:
        return [Path(s) if s is not None else None for s in value]

def metavars(allowed, module=False):
    allowed = [str(s) for s in allowed]
    if module:
        allowed.append('MODULE')
    return '[' + '|'.join(allowed) + ']'

options = [
        ('--verbose', '-v', {
            'is_flag' : True,
            'help' : 'Print information to stderr.'
            }),
        ('--debug', '-d', {
            'is_flag' : True,
            'help' : 'Print debug information to stderr.'
            }),
        ('--quiet', '-q', {
            'is_flag' : True,
            'help' : 'Only print errors to stderr; no warnings.'
            }),
        ('log_path', '--log', '-l', {
            'type' : click.Path(exists=False),
            'callback' : path_callback,
            'help' : 'Log file path.'
            }),
        ('output_path', '--output', '-o', {
            'type' : click.Path(),
            'callback' : path_callback,
            'help' : 'Instead of writing DOT code to stdout, send output to the file given.'
            }),
        ('config_paths', '--config', '-c', {
            'type' : click.Path(exists=True),
            'callback' : path_callback,
            'multiple' : True,
            'help' : 'Program configuration files'
            }),
        ('input_format','--from', '-f', {
            'type' : str,
            'help' : "File format for input coming through stdin. Assumed to be 'csv' if not given.",
            'metavar' : metavars(api.BUILTIN_READERS, module=False)
            }),
        ('--schema', '-m', {
            'type' : str,
            'help' : "Member table schema. May be the path to a custom Python module. Defaults to 'basic'.",
            'metavar' : metavars(api.BUILTIN_SCHEMAS, module=True)
            }),
        ('--writer', '-w', {
            'type' : str,
            'help' : 'Writing module. May be the path to a custom Python module. If no module is given, one is guessed based on the output filetype.',
            'metavar' : metavars(api.BUILTIN_WRITERS, module=True)
            }),
        ('output_format', '--to', '-t', {
            'type' : str,
            'help' : "File format for output. Must be supported by the writer. Defaults to the output's file extension if it is known or 'dot' if it is unknown.",
            'metavar' : 'EXT',
            }),
        ('--seed', '-S', {
            'type' : int,
            'help' : 'Seed for the random number generator. Used to move tree nodes around in a repeatable way.'
            }),
        ]

class collect_options:
    '''
    Combines the list of options into a chain of options for the click package.
    '''

    def __init__(self, options_list):
        self.options = options_list

    def __call__(self, function):

        accumulator = function
        for option in options:
            param_decls, attrs = option[:-1], option[-1]
            accumulator = wraps(accumulator)(click.option(*param_decls, **attrs)(accumulator))

        return accumulator

@click.command()
@click.argument('input_files', nargs=-1, type=click.File('r'))
@click.version_option(version=version)
@collect_options(options)
@logged
def cli(verbose, debug, quiet, log_path, *args, **kwargs):
    setup_logger(verbose, debug, quiet, log_path)
    return api.generate(*args, **kwargs)

