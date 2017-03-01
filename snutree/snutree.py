import subprocess
import logging
import sys
from typing import Any, List, IO
from pathlib import Path
import yaml
from pluginbase import PluginBase
from . import SnutreeError
from .readers import sql, dotread, csv
from .tree import FamilyTree
from .utilities import logged

if getattr(sys, 'frozen', False):
    # pylint: disable=no-member,protected-access
    SNUTREE_ROOT = Path(sys._MEIPASS)
else:
    # The folder this file is located in (used for importing member formats)
    SNUTREE_ROOT = Path(__file__).parent

# Location of all built-in member formats
PLUGIN_BASE = PluginBase(package='snutree.member', searchpath=[str(SNUTREE_ROOT/'member')])

def get_member_format(value):
    '''
    Validates the provided member module and returns the appropriate Python
    module to import.

    Example: "get_member_format('basic')" will import and return member.basic
    Example: "get_member_format(PATH/'plugin.py')" will import and return plugin.py

    Any module imported here is assumed to implement a function called
    validate(members) that takes a list of member dictionaries, validates it,
    and yields a list of member objects.
    '''

    module_file = Path(value)

    if module_file.exists() and module_file.suffix == '.py':
        # Add custom module's directory to plugin path
        searchpath = [str(module_file.parent)] # pluginbase does not support filenames in the searchpath
        module_name = module_file.stem
    else:
        # Assume it's  builtin
        searchpath = []
        module_name = value

    # Setting persist=True ensures module won't be garbage collected before its
    # call in cli(). It will stay in memory for the program's duration.
    plugin_source = PLUGIN_BASE.make_plugin_source(searchpath=searchpath, persist=True)

    try:
        module = plugin_source.load_plugin(module_name)
    except ImportError:
        msg = 'must be one of {!r} or the path to a custom Python module'
        val = plugin_source.list_plugins()
        raise SnutreeError(msg.format(val))

    return module

def generate(
        files:List[IO[Any]],
        output_path:str,
        log_path:str,
        config_paths:List[str],
        member_format:str,
        input_format:str,
        seed:int,
        debug:bool,
        verbose:bool,
        quiet:bool,
        ):
    '''
    Create a big-little family tree.
    '''

    files = files or []
    config_paths = config_paths or []

    # Set up logging when it won't conflict with stdout
    if log_path or output_path:
        log_stream = open(log_path, 'w') if log_path else sys.stdout
        if debug:
            logging.basicConfig(level=logging.DEBUG, stream=log_stream, format='%(asctime)s %(levelname)s: %(name)s - %(message)s')
        elif verbose:
            logging.basicConfig(level=logging.INFO, stream=log_stream, format='%(levelname)s: %(message)s')
        elif not quiet:
            logging.basicConfig(level=logging.WARNING, stream=log_stream, format='%(levelname)s: %(message)s')

    logging.info('Retrieving data from sources')
    member_dicts = read_sources(files, stdin_fmt=input_format)
    member_module = get_member_format(member_format)

    logging.info('Validating data')
    members = member_module.dicts_to_members(member_dicts)

    logging.info('Loading tree configuration')
    tree_cnf = load_configuration(config_paths)
    tree_cnf['seed'] = seed or tree_cnf.get('seed', 0)

    logging.info('Constructing family tree data structure')
    tree = FamilyTree(members, tree_cnf)

    logging.info('Creating DOT code representation')
    dotgraph = tree.to_dot_graph()

    logging.info('Converting DOT code representation to text')
    dotcode = dotgraph.to_dot()

    logging.info('Writing output')
    write_output(dotcode, output_path)

@logged
def read_sources(files, stdin_fmt=None):
    '''
    Retrieves a list of members from the provided open files. Using the file
    extensions to determine what format to interpret the inputs as. Use the
    provided stdin_fmt if files are coming from stdin.
    '''

    readers = {
            # SQL query
            'yaml' : sql.get_table,
            # CSV table
            'csv' : csv.get_table,
            # DOT source code
            'dot' : dotread.get_table,
            }

    members = []
    for f in files or []:

        # Filetype is the path suffix or stdin's format if input is stdin
        filetype = Path(f.name).suffix[1:] if f.name != '<stdin>' else stdin_fmt

        read = readers.get(filetype)
        if not read:
            msg = 'data source filetype {!r} not supported'
            raise SnutreeError(msg.format(filetype))

        members += read(f)

    return members

@logged
def load_configuration(paths):
    '''
    Load configuration YAML files from the given paths. Later paths override
    the settings in earlier paths.
    '''

    config = {}
    for path in paths:
        with open(path, 'r') as f:
            config.update(yaml.safe_load(f))

    return config

@logged
def write_output(dotcode, path=None):
    '''
    Use the path's extension to determine an output format. Then, compile the
    DOT code to that format and write into the file at the given path (or
    stdout, if no path is provided).
    '''

    filetype = Path(path).suffix if path is not None else None
    if not path:
        write_stream(dotcode, filetype, sys.stdout)
    else:
        with open(path, 'wb+') as f:
            write_stream(bytes(dotcode, 'utf-8'), filetype, f)

def write_stream(output, fmt, stream):
    '''
    Write output of the given format to the streem.
    '''

    # TODO catch errors when dot does not exist
    # TODO bundle DOT?

    if fmt == '.pdf':
        # `shell=True` is necessary for Windows, but not for Linux. The
        # program arguments are constants, so shell=True should be fine
        result = subprocess.run(['dot', '-Tpdf'], check=True, shell=True,
                input=output, stdout=subprocess.PIPE)
        output = result.stdout
    elif fmt not in ('.dot', None):
        msg = 'output filetype "{}" not supported'
        raise SnutreeError(msg.format(fmt))

    stream.write(output)

