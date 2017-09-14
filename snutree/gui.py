
'''
A simple GUI frontend for the snutree program.
'''

import sys
import logging
from collections import OrderedDict
import gooey
from snutree import api
from . import cli
from .errors import SnutreeError
from .utilities.logging import setup_logger

@gooey.Gooey()
def main():
    '''
    Snutree GUI entry point.
    '''
    try:
        invoke()
    except SnutreeError as e:
        logging.getLogger('snutree').error(e)
        sys.exit(1)

def invoke(argv=None):
    '''
    Run snutree (configured for a GUI) using the provided list of arguments By
    default, the running script's actual command-line arguments are used (these
    are set by Gooey in main()).
    '''
    args = vars(parse_args(argv))
    args_log = dict(verbose=True, debug=False, quiet=False, log_path=None)
    args_api = dict(args, input_format=None, writer='dot', output_format=None)
    setup_logger(**args_log)
    api.generate(**args_api)

def parse_args(argv=None):
    '''
    Parse and return the program arguments. If `argv` is provided, arguments
    are read from that list instead of using the system arguments. Gooey may
    set these arguments if used in a GUI.
    '''
    parser = gooey.GooeyParser(prog='snutree', description=None)
    for args, kwargs in options.values():
        parser.add_argument(*args, **kwargs)
    parsed = parser.parse_args(argv)
    return parsed

def get_gui_options():
    '''
    Return argument parser arguments for the GooeyParser by making
    modifications to the CLI argument parser arguments.
    '''

    # ArgumentParser kwargs overrides. Only these arguments will be permitted
    # in the GUI.
    gui_overrides = OrderedDict([

        ('input', {
            'metavar' : 'Input Files',
            'widget' : 'MultiFileChooser',
            'nargs' : '+', # keeps GUI users away from stdin (unless '-' provided)
            'help' : None,
        }),

        ('output', {
            'metavar' : 'Output File',
            'widget' : 'FileSaver',
            'required' : True, # keeps GUI users away from stdout
            'help' : None,
        }),

        # Users can still enter file paths, just not with a file chooser
        ('schema', {
            'metavar' : 'Schema',
            'default' : 'basic',
            'help' : None,
        }),

        # MultiFileChooser has form '--config arg1 arg2 ...', which is unlike
        # snutree CLI's config flag form of '--config arg1 --config arg2'. To
        # adjust for this, 'nargs' is added and 'action' has been set to
        # 'store' from 'append'.
        ('config', {
            'metavar' : 'Configuration Files',
            'widget' : 'MultiFileChooser',
            'nargs' : '*',
            'action' : 'store',
            'help' : None,
        }),

        ('seed', {
            'metavar' : 'Seed',
            'default' : 1,
            'help' : None,
        }),

    ])

    gui_options = OrderedDict()
    for key, gui_kwargs in gui_overrides.items():
        args, cli_kwargs = cli.options[key]
        gui_options[key] = args, dict(cli_kwargs, **gui_kwargs)

    return gui_options

options = get_gui_options()

