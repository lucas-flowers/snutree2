import subprocess
import logging
import sys
from typing import Any, List, IO
from pathlib import Path
from contextlib import contextmanager
from collections import MutableSequence, MutableMapping
import yaml
from pluginbase import PluginBase
from . import SnutreeError
from .readers import sql, dotread, csv
from .tree import FamilyTree
from .utilities import logged

# The folder this file is located in (used for importing member formats)
if getattr(sys, 'frozen', False):
    # pylint: disable=no-member,protected-access
    SNUTREE_ROOT = Path(sys._MEIPASS)
else:
    SNUTREE_ROOT = Path(__file__).parent

# Location of all built-in member formats
PLUGIN_BASE = PluginBase(package='snutree.member', searchpath=[str(SNUTREE_ROOT/'member')])

def get_member_type(value):
    '''
    Validates the provided member module and returns the appropriate Python
    module to import.

    Example: "get_member_type('basic')" will import and return member.basic
    Example: "get_member_type(PATH/'plugin.py')" will import and return plugin.py

    Any module imported here is assumed to implement these two variables:

    + dicts_to_members(members): Takes a list of member dictionaries, validates
    it, and yields a list of member objects.

    + RankType(string): Converts a string to RankType, where RankType is a type
    like int or Semester representing the value of each rank (such as a year or
    year/season combination) and implementing integer addition.

    + schema_information: A dictionary whose keys are column names and whose
    values are written descriptions of those columns.

    '''

    module_file = Path(value) if value else None
    if module_file and module_file.exists() and module_file.suffix == '.py':
        # Add custom module's directory to plugin path
        searchpath = [str(module_file.parent)] # pluginbase does not support filenames in the searchpath
        module_name = module_file.stem
    else:
        # Assume it's a built-in schema
        searchpath = []
        module_name = value or 'basic' # fall back to basic schema if none provided

    # Setting persist=True ensures module won't be garbage collected before its
    # call in cli(). It will stay in memory for the program's duration.
    plugin_source = PLUGIN_BASE.make_plugin_source(searchpath=searchpath, persist=True)

    try:
        module = plugin_source.load_plugin(module_name)
    except ImportError:
        builtins = PLUGIN_BASE.make_plugin_source(searchpath=[]).list_plugins()
        msg = f'must be one of {builtins!r} or the path to a custom Python module'
        raise SnutreeError(msg)

    expected_functions = ['RankType', 'dicts_to_members', 'schema_information']
    if not all([hasattr(module, attr) for attr in expected_functions]):
        msg = f'member module {module_name!r} must implement: {expected_functions!r}'
        raise SnutreeError(msg)

    return module

def generate(
        files:List[IO[Any]],
        output_path:str,
        log_path:str,
        config_paths:List[str],
        member_type:str,
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

    # TODO move code to separate function
    logging.info('Loading configuration')
    configs = load_configuration(config_paths) + [{
        'data_formats' : {},
        'member_schema' : { 'type' : member_type } if member_type else {},
        'output' : { 'seed' : seed } if seed else {}
        }]
    config = {}
    for c in configs:
        deep_update(config, c)

    logging.info('Retrieving data from sources')
    member_dicts = read_sources(files, config['data_formats'], stdin_fmt=input_format)
    member_module = get_member_type(config['member_schema'].get('type'))

    logging.info('Validating data')
    members = member_module.dicts_to_members(member_dicts, **config['member_schema'])

    logging.info('Constructing family tree data structure')
    tree = FamilyTree(members, member_module.RankType, config['output'])

    logging.info('Creating DOT code representation')
    dotgraph = tree.to_dot_graph()

    logging.info('Converting DOT code representation to text')
    dotcode = dotgraph.to_dot()

    logging.info('Writing output')
    write_output(dotcode, output_path)

@logged
def read_sources(files, data_format_cnf, stdin_fmt=None):
    '''
    Retrieves a list of members from the provided open files. Using the file
    extensions to determine what format to interpret the inputs as. Use the
    provided stdin_fmt if files are coming from stdin and use the
    data_format_cnf dictionary to provide any needed configuration.
    '''

    readers = {
            # SQL query
            'sql' : sql.get_table,
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
            msg = f'data source filetype {filetype!r} not supported'
            raise SnutreeError(msg)

        members += read(f, **data_format_cnf)

    return members

@logged
def load_configuration(paths):
    '''
    Load configuration YAML files from the given paths. Returns a list of
    dictionaries representing each configuraton file.
    '''

    configs = []
    for path in paths:
        with open(path, 'r') as f:

            try:
                config = yaml.safe_load(f) or {}
            except yaml.YAMLError as e:
                msg = f'problem reading configuration:\n{e}'
                raise SnutreeError(msg)

            configs.append(config)

    return configs

def deep_update(original, update):
    '''
    Recursively updates the original dictionary with the update dictionary. The
    update dictionary overwrites keys that are also in the original dictionary,
    except for lists, which are extended with the elements in the update
    dictionary.
    '''

    for key, new_value in update.items():
        old_value = original.get(key)
        if isinstance(old_value, MutableMapping) and isinstance(new_value, MutableMapping):
            deep_update(old_value, new_value)
        elif isinstance(old_value, MutableSequence) and isinstance(new_value, MutableSequence):
            original[key].extend(new_value)
        else:
            original[key] = new_value

@logged
def write_output(dotcode, filename=None):
    '''
    If a filename is provided: Use the filename to determine the output format,
    then compile the DOT code to the target format and write to the file.

    If no filename is provided: Write the DOT code directly to sys.stdout.
    '''

    path = Path(filename) if filename is not None else None
    filetype = path.suffix if path else '.dot'

    if filetype == '.dot':
        dot_compile = lambda x : bytes(x, sys.getdefaultencoding())
    elif filetype == '.pdf':
        dot_compile = compile_pdf
    else:
        msg = f'output filetype {filetype!r} not supported'
        raise SnutreeError(msg)

    if path:
        stream_open = lambda : path.open('wb+')
    else:
        # Buffer since we are writing binary
        stream_open = contextmanager(lambda : (yield sys.stdout.buffer))

    with stream_open() as f:
        f.write(dot_compile(dotcode))

def compile_pdf(source):
    '''
    Use dot to convert the DOT source code into a PDF, then return the result.
    '''

    try:
        # `shell=True` is necessary for Windows, but not for Linux. The command
        # string is constant, so shell=True should be fine
        result = subprocess.run('dot -Tpdf', check=True, shell=True,
                # The input will be a str and the output will be binary, but
                # subprocess.run requires they both be str or both be binary.
                # So, use binary and send the source in as binary (with default
                # encoding).
                input=bytes(source, sys.getdefaultencoding()),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE # Windows doesn't like it when stderr is left alone
                )
    except OSError as exception:
        msg = f'had a problem compiling to PDF:\n{exception}'
        raise SnutreeError(msg)

    return result.stdout

