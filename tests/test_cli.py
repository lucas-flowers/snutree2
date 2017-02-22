import io
from unittest import TestCase
from pathlib import Path
from click.testing import CliRunner
from snutree.cli import cli
from inspect import cleandoc as trim

TESTS_ROOT = Path(__file__).parent

class TestCliCommon(TestCase):

    def setUp(self):
        self.runner = CliRunner()

    def invoke(self, args, input=None):
        if input:
            infile = io.BytesIO(bytes(input, 'utf-8'))
            infile.name = '<stdin>'
        else:
            infile = None
        return self.runner.invoke(cli, args, input=infile)

    def example_template(self,
            example_name,
            config,
            schema,
            seed,
            inputs,
            ):

        example_root = TESTS_ROOT.parent/'examples'/example_name
        example_config = example_root/config
        example_inputs = [example_root/input_file for input_file in inputs]

        output = (TESTS_ROOT/'test_cli'/example_name).with_suffix('.dot')
        expected = (TESTS_ROOT/'test_cli'/(example_name+'-expected')).with_suffix('.dot')

        result = self.invoke([
            '--config', str(example_config),
            '--schema', schema,
            '--seed', seed,
            '--output', str(output),
            '--debug',
            *[str(p) for p in example_inputs]
            ])

        if result.exception:
            msg = '{}. <<OUTPUT\n{}\nOUTPUT'
            values = result.exception, result.output
            self.fail(msg.format(*values))

        self.assertEqual(output.read_text(), expected.read_text())

class TestCli(TestCliCommon):

    def test_simple(self):

        good_csv = trim('''
            name,big_name,pledge_semester
            Bob,Sue,Fall 1967
            Sue,,Spring 1965
            ''')
        result = self.invoke(['--format', 'csv', '-'], good_csv)
        if result.exception:
            raise result.exception

        bad_csv = trim('''
            name,big_name,pledge_semester
            ,Sue,Fall 1967
            Sue,,Spring 1965
            ''')
        result = self.invoke(['-f', 'csv', '-'], bad_csv)
        self.assertTrue(result.exception)

    def test_custom_module(self):

        # The custom module should be in the same folder this test file is in
        custom_module = str(Path(__file__).parent/'test_cli/custom_module.py')
        custom_csv = trim('''
            pid,cid,s
            A,B,5
            ,A,2
            ''')
        result = self.invoke(['-f', 'csv', '-', '-m', custom_module], custom_csv)

        if result.exception:
            raise result.exception

    def test_sigmanu_example(self):

        self.example_template(
                example_name='sigmanu-example',
                config='config.yaml',
                schema='sigmanu',
                seed=75,
                inputs=['directory-brothers_not_knights.csv', 'directory.csv'],
                )

    def test_sigmanu_chapters(self):

        self.example_template(
                example_name='sigmanu-chapters',
                config='config.yaml',
                schema='sigmanu_chapter',
                seed=76,
                inputs=['directory.csv'],
                )

