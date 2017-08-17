import subprocess
import logging
import sys
from typing import Any, List, IO
from pathlib import Path
from contextlib import contextmanager
from collections import MutableSequence, MutableMapping
import yaml
from cerberus import Validator
from pluginbase import PluginBase
from .errors import SnutreeError
from .logging import logged
from .tree import FamilyTree
from .cerberus import Validator

###############################################################################
###############################################################################
#### Cerberus Schemas                                                      ####
###############################################################################
###############################################################################

CONFIG_VALIDATOR = Validator({
    'readers' : {
        'type' : 'dict',
        'valueschema' : {
            'type' : 'dict',
            }
        },
    'schema' : {
        'type' : 'dict',
        },
    'tree' : {
        'type' : 'dict',
        },
    })

###############################################################################
###############################################################################
#### Plugins Setup                                                         ####
###############################################################################
###############################################################################

# The folder this file is located in (used for importing member formats)
if getattr(sys, 'frozen', False):
    # pylint: disable=no-member,protected-access
    SNUTREE_ROOT = Path(sys._MEIPASS)
else:
    SNUTREE_ROOT = Path(__file__).parent

def get_plugin_base(subpackage):
    '''
    Returns the plugin base of the subpackage whose name is a parameter.
    '''
    return PluginBase(package=f'snutree.{subpackage}', searchpath=[str(SNUTREE_ROOT/f'{subpackage}')])

def get_plugin_builtins(plugin_base):
    '''
    Takes the plugin base and returns all modules in that plugin base.
    '''
    return plugin_base.make_plugin_source(searchpath=[]).list_plugins()

# Plugin bases for each of the possible types of plugins
PLUGIN_BASES = tuple(get_plugin_base(p) for p in ('readers', 'schemas'))
READERS_PLUGIN_BASE, SCHEMAS_PLUGIN_BASE = PLUGIN_BASES

# Lists of the built-in plugins for each of the possible types of plugins
BUILTIN_LISTS = tuple(get_plugin_builtins(p) for p in PLUGIN_BASES)
BUILTIN_READERS, BUILTIN_SCHEMAS = BUILTIN_LISTS

def get_module(plugin_base, name, attributes=None, descriptor='module', custom=True):
    '''
    For the given PluginBase, validates the module whose name is given, by
    ensuring the module implements the expected attributes whose names are
    contained in the attributes parameter. Returns the validated module. (The
    descriptor is used in error messages.)

    If it is desired to not permit custom module paths to directly be provided
    (and instead just use the files in the builtins folder), set the custom
    flag to False.
    '''

    module_file = Path(name) if name else None
    if custom and module_file and module_file.exists() and module_file.suffix == '.py':
        # Add custom module's directory to plugin path
        searchpath = [str(module_file.parent)] # pluginbase does not support filenames in the searchpath
        module_name = module_file.stem
    else:
        # Assume it's a built-in schema
        searchpath = []
        module_name = name

    # Setting persist=True ensures module won't be garbage collected before its
    # call in cli(). It will stay in memory for the program's duration.
    plugin_source = plugin_base.make_plugin_source(searchpath=searchpath, persist=True)

    try:
        module = plugin_source.load_plugin(module_name)
    except ModuleNotFoundError:
        _or_custom_module = ' or the path to a custom Python module' if custom else ''
        builtins = get_plugin_builtins(plugin_base)
        msg = f'{descriptor} must be one of {builtins!r}{_or_custom_module}'
        raise SnutreeError(msg)

    if not all([hasattr(module, a) for a in attributes or []]):
        msg = f'{descriptor} module {module_name!r} must implement: {attributes!r}'
        raise SnutreeError(msg)

    return module

def get_schema_module(name):
    '''
    Return the member table schema module of the given name.
    '''
    return get_module(SCHEMAS_PLUGIN_BASE, name,
            attributes=['Rank', 'to_Members', 'description'],
            descriptor='member schema',
            custom=True)

def get_reader_module(filetype):
    '''
    Return the reader module for the given filetype.
    '''
    return get_module(READERS_PLUGIN_BASE, filetype,
            attributes=['get_table'],
            descriptor='input file format',
            custom=False)

###############################################################################
###############################################################################
#### API                                                                   ####
###############################################################################
###############################################################################

def generate(
        input_files:List[IO[Any]],
        output_path:str,
        config_paths:List[str],
        schema:str,
        input_format:str,
        seed:int,
        ):
    '''
    Create a big-little family tree.
    '''

    # Parameters for this function that can also be included in config files
    config_args = denullified({
        'readers' : {
            'stdin' : {
                'format' : input_format,
                },
            },
        'schema' : {
            'name' : schema,
            },
        'tree' : {
            'seed' : seed,
            }
        })

    logger = logging.getLogger(__name__)

    logger.info('Loading configuration files')
    config = get_config(config_paths, config_args)

    logger.info('Loading member schema module')
    schema = get_schema_module(config['schema'].get('name', 'basic'))

    logger.info('Reading member table from data sources')
    member_table = get_member_table(input_files, config['readers'])

    logger.info('Validating member table')
    members = schema.to_Members(member_table, **config['schema'])

    logger.info('Building family tree')
    tree = FamilyTree(members, schema.Rank, config['tree'])

    logger.info('Building DOT graph')
    from snutree.writers import dot
    dot_graph = dot.to_dot_graph(tree, schema.Rank, config['tree'])

    logger.info('Composing DOT source code')
    dot_src = dot_graph.to_dot()

    logger.info('Writing to output file')
    write_output(dot_src, output_path)

###############################################################################
###############################################################################
#### API Helper Functions                                                  ####
###############################################################################
###############################################################################

@logged
def get_config(config_paths, config_args):
    '''
    Loads the YAML configuration files at the given paths and combines their
    contents with the configuration arguments dictionary provided. Validates
    the combined configurations and returns the result as a dictionary. If
    there is overlap between configurations, keys from files earlier in the
    list will be overwritten by those later in the list (anything in
    config_args will overwrite any keys from the list itself). If there are
    lists inside the configuration, those lists will be extended, not
    overwritten.
    '''
    config = {}
    for c in load_config_files(config_paths) + [config_args]:
        deep_update(config, c)
    return CONFIG_VALIDATOR.validated(config)

def load_config_files(paths):
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
                msg = f'problem reading configuration file {path!r}:\n{e}'
                raise SnutreeError(msg)
            configs.append(config)

    return configs

@logged
def get_member_table(files, reader_configs):
    '''
    Retrieves a list of members from the provided files, using the file
    extensions to determine what format to interpret the inputs as (stdin will
    use the format provided by reader_configs['stdin']['format']). The reader
    may use the dictionary reader_configs[READER_NAME] to configure itself.
    '''

    members = []
    for f in files:

        # Filetype is the path suffix or stdin's format if input is stdin
        if f.name == '<stdin>':
            filetype = reader_configs.get('stdin', {}).get('format')
            if not filetype:
                msg = f'data from stdin requires an input format'
                raise SnutreeError(msg)
        else:
            filetype = Path(f.name).suffix[1:] # ignore first element (a dot)

        reader = get_reader_module(filetype)
        members += reader.get_table(f, **reader_configs.get(filetype, {}))

    return members

@logged
def write_output(src, filename=None):
    '''
    If a filename is provided: Use the filename to determine the output format,
    then compile the DOT source code to the target format and write to the file.

    If no filename is provided: Write DOT source code directly to sys.stdout.
    '''

    path = Path(filename) if filename is not None else None
    filetype = path.suffix[1:] if path else 'dot'

    compiled = WRITERS.get(filetype)
    if compiled is None:
        msg = f'output filetype {filetype!r} not supported'
        raise SnutreeError(msg)

    if path:
        stream_open = lambda : path.open('wb+')
    else:
        # Buffer since we are writing binary
        stream_open = contextmanager(lambda : (yield sys.stdout.buffer))

    with stream_open() as f:
        f.write(compiled(src))

###############################################################################
###############################################################################
#### Output Helper Functions                                               ####
###############################################################################
###############################################################################

def compile_pdf(src):
    '''
    Uses Graphviz dot to convert the DOT source into a PDF. Returns the PDF.
    '''

    try:
        # `shell=True` is necessary for Windows, but not for Linux. The command
        # string is constant, so shell=True should be fine
        result = subprocess.run('dot -Tpdf', check=True, shell=True,
                # The input will be a str and the output will be binary, but
                # subprocess.run requires they both be str or both be binary.
                # So, use binary and send the source in as binary (with default
                # encoding).
                input=bytes(src, sys.getdefaultencoding()),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE # Windows doesn't like it when stderr is left alone
                )
    except OSError as exception:
        msg = f'had a problem compiling to PDF:\n{exception}'
        raise SnutreeError(msg)

    return result.stdout

def compile_dot(src):
    '''
    Converts the DOT source into bytes suitable for writing (bytes, not
    characters, are expected by the main output writer).
    '''
    return bytes(src, sys.getdefaultencoding())

# Available output writers
WRITERS = {
        'dot' : compile_dot,
        'pdf' : compile_pdf,
        }

###############################################################################
###############################################################################
#### Utilities                                                             ####
###############################################################################
###############################################################################

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

def denullified(mapping):
    '''
    Creates and returns a new mapping from the provided mapping, but with all
    None-valued keys in the mapping recursively removed.
    '''

    new_mapping = {}
    for key, value in list(mapping.items()):
        if isinstance(value, MutableMapping):
            new_mapping[key] = denullified(value)
        elif value is not None:
            new_mapping[key] = value
    return new_mapping

