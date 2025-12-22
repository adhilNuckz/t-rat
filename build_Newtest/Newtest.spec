# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Newtest.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'pandas', 'PyQt5', 'PyQt6', 'tkinter', 'IPython', 'jupyter', 'scipy.spatial', 'scipy.optimize', 'scipy.stats', 'scipy.linalg'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Newtest',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\Death\\AppData\\Local\\Temp\\_MEI108842\\bot_icon.ico'],
)
