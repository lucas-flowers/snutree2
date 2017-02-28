# -*- mode: python -*-
# pylint: disable=E0602

block_cipher = None

a = Analysis(
        ['snutree/__main__.py'],
        pathex=[
            '***REMOVED***'
            ],
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

pyz = PYZ(
        a.pure,
        a.zipped_data,
        cipher=block_cipher
        )

exe_args = {
        'name' : 'snutree',
        'debug' : False,
        'strip' : False,
        'upx' : True,
        'console' : True,
        }

# One file
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
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
