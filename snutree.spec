# -*- mode: python -*-
# pylint: disable=E0602

block_cipher = None

pathex = ['snutree']
if os.name == 'nt':
    # Workaround for QT on Windows; might be fixed in newer versions of QT,
    # making this unecessary
    from pathlib import Path
    qt_path = Path(os.environ['VIRTUAL_ENV'])/'Lib/site-packages/PyQt5/Qt/bin'
    pathex.append(str(qt_path))

analysis_kwargs = dict(
        pathex=pathex,
        binaries=[],
        datas=[
            ('snutree/member', 'member')
            ],
        hiddenimports=[
            'voluptuous',
            'voluptuous.humanize',
            'snutree.utilities.voluptuous'
            ],
        hookspath=[],
        runtime_hooks=[],
        excludes=[
            'matplotlib'
            ],
        win_no_prefer_redirects=False,
        win_private_assemblies=False,
        cipher=block_cipher
        )

a_gui = Analysis(['snutree-gui.py'], **analysis_kwargs)
a_cli = Analysis(['snutree.py'], **analysis_kwargs)

# Problem: snutree.py (the script) and snutree/ (the module) resolve to the
# same name "snutree". This means:
#
#   + When snutree/__main__.py is compiled (i.e., when Analysis()'s first
#   argument includes snutree/__main__.py), everything works fine. (Note that
#   we aren't compiling with snutree/__main__.py.
#
#   + When snutree.py script is compiled, its name is covered up by the
#   snutree/ *module*, so the compiled executable doesn't work at all.
#
# Solution: When compiling snutree.py as we are now, go into the analysis
# scripts TOC object and replace the name of snutree.py's entry (named
# "snutree") with something else (e.g., "snutree_cli").
#
# Context on TOC: The TOC object, according to the current PyInstaller source,
# is a(n ordered) list of 3-tuples with the constraint that the first element
# of each tuple is unique among all first elements in the list.
#
# Implementation is as follows:
#
#   1. Find the index of the snutree.py entry
#   2. Store the entry
#   3. Replace the name of that entry with "snutree_cli"
#
i = [name for name, path, code in a_cli.scripts].index('snutree')
entry = a_cli.scripts[i]
a_cli.scripts[i] = (lambda name, path, code : ('snutree_cli', path, code))(*entry)

pyz_cli = PYZ(
        a_cli.pure,
        a_cli.zipped_data,
        cipher=block_cipher
        )

pyz_gui = PYZ(
        a_gui.pure,
        a_gui.zipped_data,
        cipher=block_cipher
        )

exe_args = dict(
        debug=False,
        strip=False,
        upx=True,
        )

# Compile CLI
exe_cli = EXE(pyz_cli,
        a_cli.scripts,
        a_cli.binaries,
        a_cli.zipfiles,
        a_cli.datas,
        name='snutree',
        **exe_args
        )

# Compile GUI
exe_gui = EXE(pyz_gui,
        a_gui.scripts,
        a_gui.binaries,
        a_gui.zipfiles,
        a_gui.datas,
        name='snutree-gui',
        console=False,
        **exe_args
        )

# # One directory
# exe = EXE(pyz,
#         a.scripts,
#         exclude_binaries=True,
#         **exe_args
#         )
# coll = COLLECT(exe,
#         a.binaries,
#         a.zipfiles,
#         a.datas,
#         strip=False,
#         upx=True,
#         name='snutree')

# vim: filetype=python
