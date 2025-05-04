# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('img', 'img'), ('db', 'db'), ('controller', 'controller'), ('runs', 'runs'), ('opencv_videoio_ffmpeg4100_64.dll', '.')],
    hiddenimports=['account', 'animals', 'animals_count', 'animals_count_2', 'barns_management', 'employee_management', 'environment', 'login', 'statistics_p', 'vaccination', 'work_shifts'],
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
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
