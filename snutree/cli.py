import logging
import sys
from functools import wraps
from pathlib import Path
import click
from . import api
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

options = [
        ('--verbose', '-v', {
            'is_flag' : True,
            'help' : 'Print extra information on progress to stderr'
            }),
        ('--debug', '-d', {
            'is_flag' : True,
            'help' : 'Print debug information to stderr'
            }),
        ('--quiet', '-q', {
            'is_flag' : True,
            'help' : 'Only print errors to stderr, no warnings'
            }),
        ('log_path', '--log', '-l', {
            'type' : click.Path(exists=False),
            'callback' : path_callback,
            'help' : 'Log file path'
            }),
        ('output_path', '--output', '-o', {
            'type' : click.Path(),
            'callback' : path_callback,
            'help' : f'Instead of writing DOT code to stdout, send output to a file with one of the filetypes in TODO'
            }),
        ('config_paths', '--config', '-c', {
            'type' : click.Path(exists=True),
            'callback' : path_callback,
            'multiple' : True,
            'help' : 'Program configuration files'
            }),
        ('input_format','--format', '-f', {
            'type' : str,
            'help' : f'Input file format for stdin; one of {api.BUILTIN_READERS!r}'
            }),
        ('--schema', '-m', {
            'type' : str,
            'help' : f'Member table schema; one of {api.BUILTIN_SCHEMAS!r} or a custom Python module'
            }),
        ('--writer', '-w', {
            'type' : str,
            'help' : f'Writing module; one of {api.BUILTIN_WRITERS!r} or a custom Python module'
            }),
        ('--seed', '-S', {
            'type' : int,
            'help' : 'Seed for the random number generator, used to move tree nodes around in a repeatable way'
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
@collect_options(options)
@logged
def cli(verbose, debug, quiet, log_path, *args, **kwargs):
    setup_logger(verbose, debug, quiet, log_path)
    return api.generate(*args, **kwargs)

