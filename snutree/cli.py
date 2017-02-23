#!/usr/bin/env python
import subprocess, click, logging, sys, yaml, csv, importlib.util
from pathlib import Path
from . import SnutreeError
from .readers import sql, dotread
from .tree import FamilyTree
from .utilities import logged

def main():

    try:
        cli()
    # except:
    #     import pdb; pdb.post_mortem()
    except SnutreeError as e:
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
@click.option('log_path', '--log', '-l', type=click.Path(exists=False), default=None)
@click.option('config_paths', '--config', '-c', type=click.Path(exists=True), multiple=True)
@click.option('schema_module', '--schema', '-m', callback=validate_directory_module, default='basic')
@click.option('input_format', '--format', '-f', type=str, default=None)
@click.option('--seed', '-S', default=0)
@click.option('--debug', '-d', is_flag=True, default=False)
@click.option('--verbose', '-v', is_flag=True, default=False)
@click.option('--quiet', '-q', is_flag=True, default=False)
@logged
def cli(files, output_path, log_path, config_paths, seed, debug, verbose, quiet, schema_module, input_format):
    '''
    Create a big-little family tree.
    '''

    if log_path or output_path:
        log_stream = open(log_path, 'w') if log_path else sys.stdout
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

@logged
def get_from_sources(files, stdin_fmt=None):

    readers = {
            'yaml' : lambda f : sql.get_table_from_cnf(yaml.safe_load(f)),
            'csv' : lambda f : list(csv.DictReader(f)),
            'dot' : lambda f : dotread.get_members(f)
            }

    members = []
    for f in files or []:

        # Filetype is the path suffix or stdin's format if input is stdin
        filetype = Path(f.name).suffix[1:] if f.name != '<stdin>' else stdin_fmt

        table_getter = readers.get(filetype)
        if not table_getter:
            msg = 'input filetype {!r} not supported'
            raise SnutreeError(msg.format(filetype))
        members += table_getter(f)

    return members

@logged
def load_configuration(paths):
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

    if fmt == '.pdf':
        result = subprocess.run(['dot', '-Tpdf'], check=True,
                input=output, stdout=subprocess.PIPE)
        output = result.stdout
    elif fmt not in ('.dot', None):
        msg = 'output filetype "{}" not supported'
        raise SnutreeError(msg.format(fmt))

    stream.write(output)

if __name__ == '__main__':
    main()

