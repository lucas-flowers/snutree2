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
    nt.assert_false(result.exception)

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
    nt.assert_false(result.exception)

def test_sigmanu_example():

    sigmanu_root = TESTS_ROOT.parent/'examples/sigmanu-example'

    config = sigmanu_root/'config.yaml'
    bnks = sigmanu_root/'directory-brothers_not_knights.csv'
    directory = sigmanu_root/'directory.csv'

    result = invoke([
        '--config', str(config),
        '--schema', 'sigmanu',
        '--seed', 75,
        # Arguments
        str(bnks), str(directory)
        ])

    nt.assert_false(result.exception)

    expected = (TESTS_ROOT/'test_cli_sigmanu_out.dot').read_text()
    nt.assert_equal(result.output, expected)

def test_sigmanu_chapters():

    chapters_root = TESTS_ROOT.parent/'examples/sigmanu-chapters'

    config = chapters_root/'config.yaml'
    directory = chapters_root/'directory.csv'

    result = invoke([
        '-c', str(config),
        '-m', 'sigmanu_chapters',
        '-S', 76,
        # Arguments
        str(directory)
        ])

    nt.assert_false(result.exception)

    expected = (TESTS_ROOT/'test_cli_chapters_out.dot').read_text()
    nt.assert_equal(result.output, expected)

