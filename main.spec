# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all,collect_data_files

# for importing .so files as binaries
import glob

opencv_libs = glob.glob('/usr/lib/libopencv_*.so*')
binaries = [(lib, '.') for lib in opencv_libs]

hiddenimports = []
tmp_ret = collect_all('cv2')

# Collect the data files that textual needs (ie .css files)
datas = [('styles.css', '.')]

datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='moniker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
