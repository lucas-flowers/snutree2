import sys
from io import StringIO
from inspect import cleandoc as trim
from pathlib import Path
from contextlib import contextmanager
import pytest
from snutree import cli
from snutree.errors import SnutreeSchemaError

EXAMPLES_ROOT = Path(__file__).parent/'../examples'

@contextmanager
def redirect_stdin(string):
    '''
    Temporarily replace stdin with the provided string as a text stream.
    '''
    stdin = sys.stdin
    sys.stdin = StringIO(string)
    sys.stdin.name = '<stdin>'
    yield
    sys.stdin = stdin

def run_example(examples_root=EXAMPLES_ROOT,
                schema=None,
                example_name=None,
                configs=None,
                inputs=None,
                ):

    example = examples_root/example_name

    config_paths = [example/config for config in configs or []]
    input_paths = [example/input_file for input_file in inputs or []]

    expected = (example/example_name).with_suffix('.dot')
    output = (example/(example_name + '-actual')).with_suffix('.dot')

    config_params = []
    for config in config_paths:
        config_params.append('--config')
        config_params.append(str(config))

    schema_params = []
    if schema:
        schema_params.append('--schema')
        schema_params.append(str(schema))

    cli.invoke(config_params + schema_params + [
        '--output', str(output),
        '--debug',
        *[str(p) for p in input_paths]
    ])

    assert output.read_text(encoding='utf-8') == expected.read_text(encoding='utf-8')

@pytest.mark.parametrize('args', [
    ['--from', 'csv', '-'],
    ['-'],
])
def test_simple(args):
    good_csv = trim('''
        name,big_name,semester
        Bob,Sue,Fall 1967
        Sue,,Spring 1965
    ''')
    with redirect_stdin(good_csv):
        cli.invoke(args)

@pytest.mark.parametrize('args', [
    ['-f', 'csv', '-'],
])
def test_simple_bad(args):
    bad_csv = trim('''
        name,big_name,semester
        ,Sue,Fall 1967
        Sue,,Spring 1965
    ''')
    with redirect_stdin(bad_csv):
        with pytest.raises(SnutreeSchemaError):
            cli.invoke(args)

def test_custom_module():
    run_example(
        example_name='custom',
        schema=EXAMPLES_ROOT/'custom/custom_module.py',
        configs=['config.yaml'],
        inputs=['custom.csv'],
    )

def test_sigmanu_example():
    run_example(
        example_name='sigmanu',
        configs=['config-input.yaml', 'config.yaml'],
        inputs=['sigmanu_nonknights.csv', 'sigmanu.csv'],
    )

def test_chapters():
    run_example(
        example_name='chapter',
        configs=['config-dot.yaml', 'config.yaml'],
        inputs=['chapter.csv'],
    )

def test_basic():
    run_example(
        example_name='basic',
        configs=[],
        inputs=['basic.csv'],
    )

def test_keyed():
    run_example(
        example_name='keyed',
        configs=['config.yaml'],
        inputs=['keyed.csv'],
    )

