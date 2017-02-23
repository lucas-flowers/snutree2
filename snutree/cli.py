#!/usr/bin/env python
import subprocess, click, logging, sys, yaml, csv, importlib.util
from pathlib import Path
from cerberus import Validator
from .readers import sql, dotread
from .tree import FamilyTree, TreeError
from .entity import TreeEntityAttributeError, DirectoryError
from .utilities import logged, SettingsError, nonempty_string, validate

def main():

    try:
        cli()
    # except:
    #     import pdb; pdb.post_mortem()
    except (TreeError, TreeEntityAttributeError, DirectoryError, SettingsError) as e:
        logging.error(e)
        sys.exit(1)
    except Exception as e:
        logging.error('Unexpected error.', exc_info=True)
        sys.exit(1)

SNUTREE_ROOT = Path(__file__).parent
STANDARD_MODULES = {'basic', 'sigmanu', 'sigmanu_chapter'}

def validate_directory_module(ctx, parameter, value):

    # Get the path of the custom module
    module_file = Path(value)
    if value in STANDARD_MODULES:
        module_path = SNUTREE_ROOT/'schemas'/module_file.with_suffix('.py')
    elif module_file.exists() and module_file.suffix == '.py':
        module_path = module_file
    else:
        # There is no custom module; giveup and raise an error
        msg = 'must be one of {!r} or the path to a custom Python module'
        raise click.BadParameter(msg.format(STANDARD_MODULES))

    # Use the module
    module_name = module_path.stem
    spec = importlib.util.spec_from_file_location(module_name, str(module_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module

@click.command()
@click.argument('files', nargs=-1, type=click.File('r'))
@click.option('output_path', '--output', '-o', type=click.Path(), default=None)
@click.option('log_stream', '--log', '-l', type=click.File('w'), default=sys.stdout)
@click.option('config_paths', '--config', '-c', type=click.Path(exists=True), multiple=True)
@click.option('schema_module', '--schema', '-m', callback=validate_directory_module, default='basic')
@click.option('input_format', '--format', '-f', type=str, default=None)
@click.option('--seed', '-S', default=0)
@click.option('--debug', '-d', is_flag=True, default=False)
@click.option('--verbose', '-v', is_flag=True, default=False)
@click.option('--quiet', '-q', is_flag=True, default=False)
@logged
def cli(files, output_path, log_stream, config_paths, seed, debug, verbose, quiet, schema_module, input_format):
    '''
    Create a big-little family tree.
    '''

    if log_stream is not sys.stdout or output_path:
        if debug:
            logging.basicConfig(level=logging.DEBUG, stream=log_stream, format='%(asctime)s %(levelname)s: %(name)s - %(message)s')
        elif verbose:
            logging.basicConfig(level=logging.INFO, stream=log_stream, format='%(levelname)s: %(message)s')
        elif not quiet:
            logging.basicConfig(level=logging.WARNING, stream=log_stream, format='%(levelname)s: %(message)s')

    logging.info('Retrieving big-little data from data sources')
    members = get_from_sources(files, stdin_fmt=input_format)

    logging.info('Validating directory')
    members = schema_module.validate(members)

    logging.info('Loading tree configuration')
    tree_cnf = load_configuration(config_paths)
    tree_cnf['seed'] = seed or tree_cnf.get('seed', 0)

    logging.info('Constructing family tree data structure')
    tree = FamilyTree(members, tree_cnf)

    logging.info('Creating internal DOT code representation')
    dotgraph = tree.to_dot_graph()

    logging.info('Converting DOT code representation to text')
    dotcode = dotgraph.to_dot()

    logging.info('Writing output')
    write_output(dotcode, output_path)

def write_output(dotcode, path=None):

    filetype = Path(path).suffix if path is not None else None
    output = path or sys.stdout

    writers = {
            '.pdf' : write_pdffile,
            '.dot' : write_dotfile,
            None : write_textio
            }

    write = writers.get(filetype)
    if not write:
        # TODO subclass NotImplementedError and catch it
        msg = 'Output filetype "{}" not supported'
        raise NotImplementedError(msg.format(filetype))

    write(dotcode, output)

def load_configuration(paths):
    config = {}
    for path in paths:
        with open(path, 'r') as f:
            config.update(yaml.safe_load(f))
    return config

def get_from_sources(files, stdin_fmt=None):

    # TODO get better name
    table_getters = {
        'yaml' : get_from_sql_settings,
        'csv' : get_from_csv,
        'dot' : get_from_dot
        }

    members = []
    for f in files or []:

        # Filetype is the path suffix or stdin's format if input is stdin
        filetype = Path(f.name).suffix[1:] if f.name != '<stdin>' else stdin_fmt

        table_getter = table_getters.get(filetype)
        if not table_getter:
            # TODO subclass NotImplementedError and catch it
            msg = 'input filetype {!r} not supported'
            raise NotImplementedError(msg.format(filetype))
        members += table_getter(f)

    return members

@logged
def write_textio(dotcode, output):
    output.write(dotcode)

@logged
def write_dotfile(dotcode, filename):
    with open(filename, 'w+') as dotfile:
        dotfile.write(dotcode)

@logged
def write_pdffile(dotcode, pdf_filename):
    subprocess.run(['dot', '-Tpdf', '-o', pdf_filename],
            check=True, input=dotcode, universal_newlines=True)

def get_from_dot(f):
    return dotread.get_table(f)

def get_from_csv(f):
    return list(csv.DictReader(f))

MYSQL_CNF_VALIDATOR = Validator({

    'query' : nonempty_string,

    'mysql' : {
        'type' : 'dict',
        'required' : True,
        'schema' : {
            'host' : nonempty_string,
            'user' : nonempty_string,
            'passwd' : nonempty_string,
            'port' : { 'type': 'integer' },
            'db' : nonempty_string,
            }
        },

    # SSH for remote MySQL databases
    'ssh' : {
        'type' : 'dict',
        'required' : False,
        'schema' : {
            'host' : nonempty_string,
            'port' : { 'type' : 'integer' },
            'user' : nonempty_string,
            'public_key' : nonempty_string,
            }
        }

    })

def get_from_sql_settings(f):
    return get_from_sql(yaml.safe_load(f))

def get_from_sql(cnf):
    '''
    Get the table of members from the SQL database.
    '''

    cnf = validate(MYSQL_CNF_VALIDATOR, cnf)
    return sql.get_table(cnf['query'], cnf['mysql'], ssh_cnf=cnf['ssh'])

if __name__ == '__main__':
    main()

