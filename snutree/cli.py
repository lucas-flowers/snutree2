import logging
import sys
from functools import wraps
import click
from . import api
from .errors import SnutreeError
from .logging import create_snutree_logger, logged

def main():
    '''
    Run the command-line version of the program.
    '''

    logger = logging.getLogger('snutree')

    try:
        cli()

    # Expected errors
    except SnutreeError as e:
        logger.error(e)
        sys.exit(1)

    # Unexpected errors
    except Exception as e:
        logger.critical('Unexpected error.', exc_info=True)
        sys.exit(1)

options = [
        ('--verbose', '-v', {
            'is_flag' : True,
            'help' : 'Print progress'
            }),
        ('--debug', '-d', {
            'is_flag' : True,
            'help' : 'Print debug information'
            }),
        ('--quiet', '-q', {
            'is_flag' : True,
            'help' : "Do not print anything, including warnings"
            }),
        ('log_path', '--log', '-l', {
            'type' : click.Path(exists=False),
            'help' : 'Log file path'
            }),
        ('output_path', '--output', '-o', {
            'type' : click.Path(),
            'help' : f'Instead of writing DOT code to stdout, send output to a file with one of the filetypes in {list(api.WRITERS.keys())!r}'
            }),
        ('config_paths', '--config', '-c', {
            'type' : click.Path(exists=True),
            'multiple' : True,
            'help' : 'Program configuration files'
            }),
        ('schema', '--schema', '-m', {
            'type' : str,
            'help' : f'Member table schema; one of {api.BUILTIN_SCHEMAS!r} or a custom Python module'
            }),
        ('input_format','--format', '-f', {
            'type' : str,
            'help' : f'Input file format for stdin; one of {api.BUILTIN_READERS!r}'
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
    create_snutree_logger(verbose, debug, quiet, log_path)
    return api.generate(*args, **kwargs)

