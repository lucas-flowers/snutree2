import io
from inspect import cleandoc as trim
from pathlib import Path
import pytest
from click.testing import CliRunner
from snutree.errors import SnutreeSchemaError
from snutree.cli import cli

TESTS_ROOT = Path(__file__).parent
runner = CliRunner()

def invoke(args, infile=None):
    if infile:
        infile = io.BytesIO(bytes(infile, 'utf-8'))
        infile.name = '<stdin>'
    else:
        infile = None
    return runner.invoke(cli, args, input=infile)

def run_example(
        tests_root=TESTS_ROOT,
        example_name=None,
        configs=None,
        seed=None,
        inputs=None,
        ):

    files = tests_root/'files'
    trees = files/'trees'
    example = trees/example_name
    output = files/'output'
    expected = output/'expected'
    actual = output/'actual'
    if not actual.exists():
        actual.mkdir()

    example_configs = [example/config for config in configs] if configs else []
    example_inputs = [example/input_file for input_file in inputs] if inputs else []

    output = (actual/example_name).with_suffix('.dot')
    expected = (expected/(example_name + '-expected')).with_suffix('.dot')

    config_params = []
    for config in example_configs:
        config_params.append('--config')
        config_params.append(str(config))

    result = invoke(config_params + [
        '--seed', seed,
        '--output', str(output),
        '--debug',
        *[str(p) for p in example_inputs]
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
    # The custom module should be in the same folder this test file is in
    custom_module = str(TESTS_ROOT/'files/custom_module.py')
    custom_csv = trim('''
        pid,cid,s
        A,B,5
        ,A,2
        ''')
    result = invoke(['-f', 'csv', '-', '-m', custom_module], custom_csv)
    if result.exception:
        raise result.exception

def test_sigmanu_example():
    run_example(
            example_name='sigmanu-cwru-old',
            configs=['config-input.yaml', 'config.yaml'],
            seed=75,
            inputs=['directory-brothers_not_knights.csv', 'directory.csv'],
            )

def test_chapters():
    run_example(
            example_name='fake-chapter',
            configs=['config-dot.yaml', 'config.yaml'],
            seed=76,
            inputs=['directory.csv'],
            )

def test_fake():
    run_example(
            example_name='fake',
            configs=['config.yaml'],
            seed=79,
            inputs=['fake.csv'],
            )

