
import os
from pathlib import Path
from snutree import gui

def test_invoke(tmpdir):
    '''
    Simple test that everything works (on empty inputs).
    '''

    tmpdir = Path(str(tmpdir))
    filenames = ['config1.yaml', 'config2.yaml', 'input1.csv', 'input2.csv']
    for filename in filenames:
        Path.touch(tmpdir/filename)

    # The parameters for invocation are different from the real CLI; arguments
    # that take multiple files only need their flag once (i.e., "-c config1
    # config2" instead of "-c config1 -config2"). This is due to how Gooey's
    # MultiFileChooser works.
    gui.invoke([
        '--config', str(tmpdir/'config1.yaml'), str(tmpdir/'config2.yaml'),
        '--output', os.devnull,
        '--', str(tmpdir/'input1.csv'), str(tmpdir/'input2.csv'),
    ])

