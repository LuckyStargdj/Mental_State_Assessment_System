# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('config/*', 'config'), ('data/db/medical_database.db', 'data/db'), ('db_master_style.qss', '.'), ('db_master.qrc', '.')],
    hiddenimports=['1','db_data','db_data_analyze','db_left_egg','db_login','db_main','db_master_rc','db_report','db_right_egg','db_school_login','db_set','hook_qt_plugins','local_analy','new_db_data_analyze','new_untitled','test'],
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
    name='MyApp',
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
