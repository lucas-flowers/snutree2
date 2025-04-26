import logging
import sys
from contextlib import contextmanager
from typing import Any, List, IO
from pathlib import Path
from collections import MutableSequence, MutableMapping
import yaml
from cerberus import Validator
from pluginbase import PluginBase
from .errors import SnutreeError
from .tree import FamilyTree
from .utilities.logging import logged
from .utilities.cerberus import Validator

###############################################################################
###############################################################################
#### API                                                                   ####
###############################################################################
###############################################################################

def generate(input_files: List[IO[Any]],
             output_path: Path,
             config_files: List[IO[Any]],
             input_format: str,
             schema: str,
             writer: str,
             output_format: str,
             seed: int,
            ):
    '''
    Create a big-little family tree.
    '''

    logger = logging.getLogger(__name__)

    # Parameters for this function that can also be included in config files
    config_args = denullified({
        'readers' : {
            'stdin' : {
                'filetype' : input_format,
                },
            },
        'schema' : {
            'name' : schema,
            },
        'writer' : {
            'filetype' : output_format,
            'file' : output_path,
            'name' : writer,
            },
        'seed' : seed,
        })

    logger.info('Loading configuration files')
    config = get_config(config_files, config_args)

    logger.info('Loading member schema module')
    schema = get_schema_module(config['schema']['name'])

    logger.info('Reading member table from data sources')
    member_table = get_member_table(input_files, config['readers'])

    logger.info('Validating member table')
    members = schema.to_Members(member_table, **config['schema'])

    logger.info('Loading writer module')
    writer_name, writer = find_writer_module(config['writer']['filetype'], config['writer']['name'])

    # Standard usage
    if writer_name != 'table':

        logger.info('Building family tree')
        tree = FamilyTree(members, config['seed'])

        logger.info('Running writer module')
        output = writer.compile_tree(tree, schema.Rank, config['writer'])

    # Special handling for raw table output
    else:

        logger.warning('Bypassing tree generation and using raw table')
        output = writer.compile_table(member_table)

    logger.info('Writing to file')
    write_output(output, path=config['writer']['file'])

    logger.info('Done')

###############################################################################
###############################################################################
#### Configuration Schema                                                  ####
###############################################################################
###############################################################################

CONFIG_SCHEMA = {

    'readers' : {
        'description' : 'reader module configuration',
        'type' : 'dict',
        'allow_unknown' : True,
        'schema' : {
            'stdin' : {
                'description' : 'standard input reader configuration',
                'type' : 'dict',
                'schema' : {
                    'filetype' : {
                        'description' : 'type of files coming from stdin',
                        'type' : 'string',
                        'default' : 'csv',
                        }
                    }
                }
            },
        'keyschema' : {
            'description' : 'reader',
            },
        'valueschema' : {
            'description' : 'options for another reader',
            'type' : 'dict',
            }
        },

    'schema' : {
        'description' : 'members schema module configuration',
        'type' : 'dict',
        'allow_unknown' : True,
        'schema' : {
            'name' : {
                'description' : 'member schema module name',
                'type' : 'string',
                'default' : 'basic',
                }
            }
        },

    'writer' : {
        'description' : 'writer module configuration',
        'type' : 'dict',
        'allow_unknown' : True,
        'schema' : {
            'filetype' : {
                'description' : 'output filetype',
                'type' : 'string',
                'default_setter' : lambda doc: doc['file'].suffix[1:] \
                        if doc['file'] is not None and doc['file'].suffix \
                        else 'dot'
                },
            'name' : {
                'description' : 'writer module name',
                'type' : 'string',
                'default' : None,
                'nullable' : True,
                },
            'file' : {
                'description' : 'output file name',
                'default' : None,
                'nullable' : True
                }
            }
        },

    'seed' : {
        'description' : 'random number generator seed',
        'type' : 'integer',
        'default' : 71,
        },

    }

CONFIG_VALIDATOR = Validator(CONFIG_SCHEMA)

###############################################################################
###############################################################################
#### Plugins Setup                                                         ####
###############################################################################
###############################################################################

# The folder this file is located in (used for importing member formats)
SNUTREE_ROOT = Path(__file__).parent \
    if not getattr(sys, 'frozen', False) \
    else Path(sys._MEIPASS) # pylint: disable=no-member,protected-access

def get_plugin_base(subpackage):
    '''
    Returns the plugin base of the subpackage whose name is a parameter.
    '''
    package = 'snutree.{subpackage}'.format(subpackage=subpackage)
    searchpath = [str(SNUTREE_ROOT/'{subpackage}'.format(subpackage=subpackage))]
    return PluginBase(package=package, searchpath=searchpath)

def get_plugin_builtins(plugin_base):
    '''
    Takes the plugin base and returns all modules in that plugin base.
    '''
    return plugin_base.make_plugin_source(searchpath=[]).list_plugins()

# Plugin bases for each of the possible types of plugins
PLUGIN_BASES = tuple(get_plugin_base(p) for p in ('readers', 'schemas', 'writers'))
READERS_PLUGIN_BASE, SCHEMAS_PLUGIN_BASE, WRITERS_PLUGIN_BASE = PLUGIN_BASES

# Lists of the built-in plugins for each of the possible types of plugins
BUILTIN_LISTS = tuple(get_plugin_builtins(p) for p in PLUGIN_BASES)
BUILTIN_READERS, BUILTIN_SCHEMAS, BUILTIN_WRITERS = BUILTIN_LISTS

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
    except ImportError: # 3.6: ModuleNotFoundError:
        _or_custom_module = ' or the path to a custom Python module' if custom else ''
        builtins = get_plugin_builtins(plugin_base)
        msg = '{descriptor} must be one of {builtins!r}{_or_custom_module}'.format(descriptor=descriptor, builtins=builtins, _or_custom_module=_or_custom_module)
        raise SnutreeError(msg)

    if not all([hasattr(module, a) for a in attributes or []]):
        msg = '{descriptor} module {module_name!r} must implement: {attributes!r}'.format(descriptor=descriptor, module_name=module_name, attributes=attributes)
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

def get_writer_module(name):
    '''
    Return the writer of the given name.
    '''
    return get_module(WRITERS_PLUGIN_BASE, name,
                      attributes=['filetypes', 'compile_tree'],
                      descriptor='writer',
                      custom=True)

###############################################################################
###############################################################################
#### API Helper Functions                                                  ####
###############################################################################
###############################################################################

@logged
def get_config(config_files, config_args):
    '''
    Loads the YAML configuration files and combines their contents with the
    configuration arguments provided. Validates the combined configurations and
    returns the result as a dictionary.

    When there is overlap between configurations, keys from dictionaries
    processed earlier will be overwritten by those extended later (lists will
    be extended, dictionaries recursively updated, and scalars replaced). The
    values in config_args will always be processed last.
    '''
    config = {}
    for c in load_config_files(config_files) + [config_args]:
        deep_update(config, c)
    return CONFIG_VALIDATOR.validated(config)

def load_config_files(files):
    '''
    Load configuration YAML files from the given files. Returns a list of
    dictionaries representing each configuraton file.
    '''

    configs = []
    for f in files:
        try:
            config = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            path = f.name
            msg = 'problem reading configuration file {path!r}:\n{e}'.format(path=path, e=e)
            raise SnutreeError(msg)
        if not isinstance(config, dict):
            path = f.name
            msg = 'configuration YAML file must represent a dict, not a {type}:\n{path}'.format(type=type(config), path=path)
            raise SnutreeError(msg)

        configs.append(config)

    return configs

@logged
def get_member_table(files, reader_configs):
    '''
    Retrieves a list of members from the provided files, using the file
    extensions to determine what format to interpret the inputs as (stdin will
    use the format provided by reader_configs['stdin']['filetype']). The reader
    may use the dictionary reader_configs[READER_NAME] to configure itself.
    '''

    members = []
    for f in files:

        # Filetype is the path suffix or stdin's format if input is stdin
        if f.name == '<stdin>':
            filetype = reader_configs['stdin']['filetype']
            if not filetype:
                msg = 'data from stdin requires an input format'
                raise SnutreeError(msg)
        else:
            filetype = Path(f.name).suffix[1:] # ignore first element (a dot)

        reader = get_reader_module(filetype)
        members += reader.get_table(f, **reader_configs.get(filetype, {}))

    return members

def find_writer_module(filetype, writer_name=None):
    '''
    Returns the writer module with the given writer name. If no writer name
    is given, use the filetype to guess.
    '''

    if writer_name is not None:
        return writer_name, get_writer_module(writer_name)

    writers = {}
    for name in BUILTIN_WRITERS:
        module = get_writer_module(name)
        for supported_type in module.filetypes:
            writers.setdefault(supported_type, []).append((name, module))

    filetype_writers = writers.get(filetype)
    if filetype_writers and len(filetype_writers) == 1:
        writer_name, module = filetype_writers[0]
        return writer_name, module
    elif not filetype_writers:
        msg = 'format {filetype!r} has no supported writers'.format(filetype=filetype)
        raise SnutreeError(msg)
    else:
        conflicting_writers = {name for name, _ in filetype_writers}
        msg = 'format {filetype!r} has multiple writers; choose a writer from: {conflicting_writers!r}'.format(filetype=filetype, conflicting_writers=conflicting_writers)
        raise SnutreeError(msg)

def write_output(output, path=None):
    '''
    Write the output to a file at the given path. If the path is None, then
    write to stdout.
    '''
    if path is not None:
        stream_open = lambda: path.open('wb+')
    else:
        # Buffer since we are writing binary
        stream_open = contextmanager(lambda: (yield sys.stdout.buffer))
    with stream_open() as f:
        f.write(output)

###############################################################################
###############################################################################
#### General Utilities                                                     ####
###############################################################################
###############################################################################

def deep_update(original, update):
    '''
    Recursively updates the original dictionary with the update dictionary. The
    update dictionary overwrites keys that are also in the original dictionary,
    except for lists, which are extended with the elements in the update
    dictionary. If an updated value is None where the old value was a sequence
    or mapping, the old value is not updated.
    '''
    for key, new_value in update.items():
        old_value = original.get(key)
        old_map = isinstance(old_value, MutableMapping)
        old_seq = isinstance(old_value, MutableSequence)
        new_map = isinstance(new_value, MutableMapping)
        new_seq = isinstance(new_value, MutableSequence)
        if old_map and new_map:
            deep_update(old_value, new_value)
        elif old_seq and new_seq:
            original[key].extend(new_value)
        elif (old_map or old_seq) and new_value is None:
            pass
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

