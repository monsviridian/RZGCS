# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [
    ('../RZGCSContent', 'RZGCSContent'),
    ('../Python', 'Python'),
    ('../LICENSE.md', '.'),
    ('../THIRD_PARTY_LICENSES.md', '.'),
    ('../README.md', '.'),
]

a = Analysis(['../main.py'],
             pathex=['C:\Users\fuckheinerkleinehack\Documents\RZGS2\RZGCS'],
             binaries=[],
             datas=added_files,
             hiddenimports=['PyQt5.QtQuick', 'PyQt5.QtQml', 'PyQt5.QtSvg', 'numpy', 'matplotlib'],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='RZGCS',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon='../RZGCSContent/icon.ico')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='RZGCS')
