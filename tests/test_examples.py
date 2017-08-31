import io
from inspect import cleandoc as trim
from pathlib import Path
import pytest
from click.testing import CliRunner
from snutree.errors import SnutreeSchemaError
from snutree.cli import cli

EXAMPLES_ROOT = Path(__file__).parent/'../examples'
runner = CliRunner()

def invoke(args, infile=None):
    if infile:
        infile = io.BytesIO(bytes(infile, 'utf-8'))
        infile.name = '<stdin>'
    else:
        infile = None
    return runner.invoke(cli, args, input=infile)

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

    result = invoke(config_params + schema_params + [
        '--output', str(output),
        '--debug',
        *[str(p) for p in input_paths]
    ])

    if result.exception:
        raise result.exception

    assert output.read_text() == expected.read_text()

def test_simple():

    good_csv = trim('''
        name,big_name,semester
        Bob,Sue,Fall 1967
        Sue,,Spring 1965
        ''')
    result = invoke(['--from', 'csv', '-'], good_csv)
    assert not result.exception

    result = invoke(['-'], good_csv)
    assert not result.exception

    bad_csv = trim('''
        name,big_name,semester
        ,Sue,Fall 1967
        Sue,,Spring 1965
        ''')
    result = invoke(['-f', 'csv', '-'], bad_csv)
    with pytest.raises(SnutreeSchemaError):
        assert result.exception
        raise result.exception

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

