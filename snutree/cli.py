#!/usr/bin/env python
import subprocess, click, logging, sys, yaml, csv, importlib.util
from pathlib import Path
from cerberus import Validator
from .schemas import basic, sigmanu, sigmanu_chapter
from .readers import sql, dotread
from .tree import FamilyTree, TreeError
from .entity import TreeEntityAttributeError
from .utilities import logged, SettingsError, nonempty_string, validate
from .directory import Directory, DirectoryError

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

directory_types = {
        'sigmanu' : sigmanu.Directory,
        'sigmanu_chapters' : sigmanu_chapter.Directory,
        'default' : basic.Directory,
        }

@click.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), default=None)
@click.option('--config', '-c', type=click.Path(exists=True), multiple=True)
@click.option('--seed', '-S', default=0)
@click.option('--debug', '-d', is_flag=True, default=False)
@click.option('--verbose', '-v', is_flag=True, default=False)
@click.option('--quiet', '-q', is_flag=True, default=False)
@click.option('--schema', '-m', type=str, default=None)
@logged
def cli(paths, output, config, seed, debug, verbose, quiet, schema):
    '''
    Create a big-little family tree.
    '''

    if output is not None:
        if debug:
            logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format='%(asctime)s %(levelname)s: %(name)s - %(message)s')
        elif verbose:
            logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(levelname)s: %(message)s')
        elif not quiet:
            logging.basicConfig(level=logging.WARNING, stream=sys.stdout, format='%(levelname)s: %(message)s')

    logging.info('Retrieving big-little data from data sources')
    members = get_from_sources(paths)

    logging.info('Validating directory')
    # TODO clean this up
    # TODO don't subclass directory, but have factories?
    DirectoryType = directory_types.get(schema or 'default')
    if not DirectoryType:
        path = Path(schema)
        if not path.exists() or path.suffix != '.py':
            # TODO better error
            raise Exception('Must be one of ??? or a custom Python module')
        module_name = path.stem
        try:
            spec = importlib.util.spec_from_file_location(module_name, str(path))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception:
            raise Exception('Could not import custom module.')
        try:
            DirectoryType = module.Directory
        except AttributeError as e:
            raise Exception('Custom module must have a Directory class')
        if not issubclass(DirectoryType, Directory):
            raise Exception('Custom Directory class must subclass snutree.Directory')

    directory = DirectoryType(members)

    logging.info('Loading tree configuration')
    tree_cnf = load_configuration(config)

    logging.info('Constructing family tree data structure')
    tree = FamilyTree(directory, tree_cnf)

    logging.info('Creating internal DOT code representation')
    dotgraph = tree.to_dot_graph()

    logging.info('Converting DOT code representation to text')
    dotcode = dotgraph.to_dot()

    logging.info('Writing output')
    write_output(dotcode, output)

def write_output(dotcode, output=None):

    filetype = Path(output).suffix if output is not None else None
    output = output or sys.stdout

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

def get_from_sources(paths):

    # TODO get better name
    table_getters = {
        '.yaml' : get_from_sql_settings,
        '.csv' : get_from_csv,
        '.dot' : get_from_dot
        }

    members = []
    for path in paths or []:
        filetype = Path(path).suffix
        table_getter = table_getters.get(filetype)
        if not table_getter:
            # TODO subclass NotImplementedError and catch it
            msg = 'Input filetype "{}" not supported'
            raise NotImplementedError(msg.format(filetype))
        members += table_getter(path)

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

def get_from_dot(path):
    return dotread.get_table(path)

def get_from_csv(path):
    with open(path, 'r') as f:
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

def get_from_sql_settings(path):
    with open(path, 'r') as f:
        return get_from_sql(yaml.safe_load(f))

def get_from_sql(cnf):
    '''
    Get the table of members from the SQL database.
    '''

    cnf = validate(MYSQL_CNF_VALIDATOR, cnf)
    return sql.get_table(cnf['query'], cnf['mysql'], ssh_cnf=cnf['ssh'])

if __name__ == '__main__':
    main()

