import io
import nose.tools as nt
from pathlib import Path
from click.testing import CliRunner
from snutree.cli import cli
from inspect import cleandoc as trim

def invoke(args, input):
    runner = CliRunner()
    infile = io.BytesIO(bytes(input, 'utf-8'))
    infile.name = '<stdin>'
    return runner.invoke(cli, args, input=infile)

def test_simple():

    good_csv = trim('''
        name,big_name,pledge_semester
        Bob,Sue,Fall 1967
        Sue,,Spring 1965
        ''')
    result = invoke(['-f', 'csv', '-'], good_csv)
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
    custom_module = str(Path(__file__).parent / 'test_cli_custom_module.py')
    custom_csv = trim('''
        pid,cid,s
        A,B,5
        ,A,2
        ''')
    result = invoke(['-f', 'csv', '-', '-m', custom_module], custom_csv)
    nt.assert_false(result.exception)


