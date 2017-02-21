import io
import nose.tools as nt
from pathlib import Path
from click.testing import CliRunner
from snutree.cli import cli
from inspect import cleandoc as trim

TESTS_ROOT = Path(__file__).parent

def invoke(args, input=None):
    runner = CliRunner()
    infile = None
    if input:
        infile = io.BytesIO(bytes(input, 'utf-8'))
        infile.name = '<stdin>'
    return runner.invoke(cli, args, input=infile)

def test_simple():

    good_csv = trim('''
        name,big_name,pledge_semester
        Bob,Sue,Fall 1967
        Sue,,Spring 1965
        ''')
    result = invoke(['--format', 'csv', '-'], good_csv)
    if result.exception:
        raise result.exception

    bad_csv = trim('''
        name,big_name,pledge_semester
        ,Sue,Fall 1967
        Sue,,Spring 1965
        ''')
    result = invoke(['-f', 'csv', '-'], bad_csv)
    nt.assert_true(result.exception)

def test_custom_module():

    # The custom module should be in the same folder this test file is in
    custom_module = str(Path(__file__).parent/'test_cli_custom_module.py')
    custom_csv = trim('''
        pid,cid,s
        A,B,5
        ,A,2
        ''')
    result = invoke(['-f', 'csv', '-', '-m', custom_module], custom_csv)

    if result.exception:
        raise result.exception

def example_template(
        example_name,
        config,
        schema,
        seed,
        arguments,
        expected
        ):

    root = TESTS_ROOT.parent/'examples'/example_name

    config = root/config
    paths = [str(root/argument) for argument in arguments]

    result = invoke([
        '--config', str(config),
        '--schema', schema,
        '--seed', seed,
        *paths
        ])

    if result.exception:
        raise result.exception

    nt.assert_equal(result.output, (TESTS_ROOT/expected).read_text())

def test_sigmanu_example():

    example_template(
            example_name='sigmanu-example',
            config='config.yaml',
            schema='sigmanu',
            seed=75,
            arguments=['directory-brothers_not_knights.csv', 'directory.csv'],
            expected='test_cli_sigmanu_out.dot'
            )

def test_sigmanu_chapters():

    example_template(
            example_name='sigmanu-chapters',
            config='config.yaml',
            schema='sigmanu_chapters',
            seed=76,
            arguments=['directory.csv'],
            expected='test_cli_chapters_out.dot'
            )

