#!/usr/bin/env python
import logging
import sys
import click
from . import snutree, SnutreeError
from .utilities import logged

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

@click.command()
@click.argument('files', nargs=-1, type=click.File('r'))
@click.option('output_path', '--output', '-o', type=click.Path(), default=None, help='PDF or DOT file')
@click.option('log_path', '--log', '-l', type=click.Path(exists=False), default=None, help='Log location')
@click.option('config_paths', '--config', '-c', type=click.Path(exists=True), multiple=True, help='Tree configuration file')
@click.option('member_module', '--member-format', '-m', callback=lambda ctx, param, v: snutree.get_member_format(v), default='basic', help='Expected member format')
@click.option('input_format','--format', '-f', type=str, default=None, help='Input format for stdin')
@click.option('--seed', '-S', default=0, help='Use a different seed to move tree nodes around')
@click.option('--verbose', '-v', is_flag=True, default=False, help='Print progress')
@click.option('--debug', '-d', is_flag=True, default=False, help='Print debug information')
@click.option('--quiet', '-q', is_flag=True, default=False, help="Don't print anything, including warnings")
@logged
def cli(*args, **kwargs):
    return snutree.generate(*args, **kwargs)

if __name__ == '__main__':
    main()

