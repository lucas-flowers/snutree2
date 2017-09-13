
'''
A simple GUI frontend for the snutree program.
'''

import sys
import logging
from collections import OrderedDict
import gooey
from snutree import api
from snutree.errors import SnutreeError
from snutree.logging import setup_logger
from snutree import cli

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

    # ArgumentParser kwargs overrides
    gui_overrides = {

        'input' : {
            'metavar' : 'Input Files',
            'widget' : 'MultiFileChooser',
            'nargs' : '+',
            'help' : None,
        },

        'output' : {
            'metavar' : 'Output File',
            'widget' : 'FileSaver',
            'required' : True,
            'help' : None,
        },

        'schema' : {
            'metavar' : 'Schema',
            'default' : 'basic',
            'help' : None,
        },

        'config' : {
            'metavar' : 'Configuration Files',
            'widget' : 'MultiFileChooser',
            'help' : None,
        },

        'seed' : {
            'metavar' : 'Seed',
            'default' : 1,
            'help' : None,
        },

    }

    gui_options = OrderedDict()
    for key, value in cli.options.items():
        if key in gui_overrides:
            args, kwargs = value
            kwargs.update(gui_overrides[key])
            gui_options[key] = args, kwargs

    return gui_options

options = get_gui_options()

