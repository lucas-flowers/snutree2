# -*- mode: python -*-

# pylint: disable=undefined-variable

from pathlib import Path
import gooey

gui = bool(os.environ.get('SNUTREE_GUI'))

pathex=['snutree']

block_cipher = None

analysis = Analysis(
    ['snutree.py' if not gui else 'snutree-gui.py'],
    pathex=['snutree'],
    binaries=[],
    datas=[
        # This is needed because plugins---including builtins---are not
        # automatically imported (so pyinstaller can't find them). TODO:
        # Just import the builtins directly; it's too much hassle to treat
        # them like any other plugin
        ('snutree/schemas', 'schemas'),
        ('snutree/readers', 'readers'),
        ('snutree/writers', 'writers'),
    ],
    hiddenimports=[
        # pass
    ] + (['gooey'] if gui else []),
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher
)

if not gui:
    # Problem: snutree.py (the script) and snutree/ (the module) resolve to the
    # same name "snutree". This means:
    #
    #   + When snutree/__main__.py is compiled (i.e., when Analysis()'s first
    #   argument includes snutree/__main__.py), everything works fine. (Note
    #   that we aren't compiling with snutree/__main__.py.
    #
    #   + When snutree.py script is compiled, its name is covered up by the
    #   snutree/ *module*, so the compiled executable doesn't work at all.
    #
    # Solution: When compiling snutree.py as we are now, go into the analysis
    # scripts TOC object and replace the name of snutree.py's entry (named
    # "snutree") with something else (e.g., "snutree_cli").
    #
    # Context on TOC: The TOC object, according to the current PyInstaller
    # source, is a(n ordered) list of 3-tuples with the constraint that the
    # first element of each tuple is unique among all first elements in the
    # list.
    #
    # Implementation is as follows:
    #
    #   1. Find the index of the snutree.py entry
    #   2. Store the entry
    #   3. Replace the name of that entry with "snutree_cli"
    #
    i = [name for name, path, code in analysis.scripts].index('snutree')
    entry = analysis.scripts[i]
    analysis.scripts[i] = (lambda name, path, code : ('snutree_cli', path, code))(*entry)

pyz = PYZ(
    analysis.pure,
    analysis.zipped_data,
    cipher=block_cipher
)

gooey_root = Path(gooey.__file__).parent
exe = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.zipfiles,
    analysis.datas,
    *((
        [('u', None, 'OPTION')],
        Tree(str(gooey_root/'languages'), prefix='gooey/languages'),
        Tree(str(gooey_root/'images'), prefix='gooey/images'),
    ) if gui else ()),
    debug=False,
    strip=False,
    upx=True,
    **(dict(
        name='snutree-gui',
        console=False,
        windows=True,
        icon=str(gooey_root/'images/program_icon.ico'),
    ) if gui else dict(
        name='snutree'
    ))
)

# vim: filetype=python
