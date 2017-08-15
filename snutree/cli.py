import logging
import sys
from functools import wraps
import click
from . import api
from .errors import SnutreeError
from .logging import logged

def main():
    '''
    Run the command-line version of the program.
    '''

    try:
        cli()

    ## Debugging
    # except:
    #     import pdb; pdb.post_mortem()

    # Expected errors
    except SnutreeError as e:
        logging.error(e)
        sys.exit(1)

    # Unexpected errors
    except Exception as e:
        logging.error('Unexpected error.', exc_info=True)
        sys.exit(1)

options = [
        ('output_path', '--output', '-o', {
            'type' : click.Path(),
            'help' : f'Instead of writing DOT code to stdout, send output to a file with one of the filetypes in {list(api.WRITERS.keys())!r}'
            }),
        ('log_path', '--log', '-l', {
            'type' : click.Path(exists=False),
            'help' : 'Log file path'
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
            'help' : f'Input file format for stdin; one of {api.BUILTIN_READERS!r} or a custom Python module'
            }),
        ('--seed', '-S', {
            'type' : int,
            'help' : 'Seed for the random number generator, used to move tree nodes around in a repeatable way'
            }),
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
        ]

class collect_options:

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
def cli(*args, **kwargs):
    return api.generate(*args, **kwargs)

