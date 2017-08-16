import io
from inspect import cleandoc as trim
from pathlib import Path
from click.testing import CliRunner
from snutree.errors import SnutreeError, SnutreeSchemaError
from snutree.cli import cli
from snutree.logging import setup_logger

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
        example_name=None,
        configs=None,
        seed=None,
        inputs=None,
        ):

    example_root = TESTS_ROOT.parent/'examples'/example_name
    example_configs = [example_root/config for config in configs] if configs else []
    example_inputs = [example_root/input_file for input_file in inputs] if inputs else []

    output = (TESTS_ROOT/'test_cli'/example_name).with_suffix('.dot')
    expected = (TESTS_ROOT/'test_cli'/(example_name+'-expected')).with_suffix('.dot')

    config_params = []
    for config in example_configs:
        config_params.append('--config')
        config_params.append(str(config))

    setup_logger(verbose=False, debug=True, quiet=False)
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
        name,big_name,pledge_semester
        Bob,Sue,Fall 1967
        Sue,,Spring 1965
        ''')
    result = invoke(['--format', 'csv', '-'], good_csv)
    if result.exception:
        raise result.exception

    result = invoke(['-'], good_csv)
    assert isinstance(result.exception, SnutreeError)

    bad_csv = trim('''
        name,big_name,pledge_semester
        ,Sue,Fall 1967
        Sue,,Spring 1965
        ''')
    result = invoke(['-f', 'csv', '-'], bad_csv)
    assert isinstance(result.exception, SnutreeSchemaError)

def test_custom_module():
    # The custom module should be in the same folder this test file is in
    custom_module = str(Path(__file__).parent/'test_cli/custom_module.py')
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
            configs=['config.yaml'],
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

