# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[('ForPy/*.dll', 'ForPy'), ('ForPy_不加密/*.dll', 'ForPy_不加密'), ('iconengines/*.dll', 'iconengines'), ('imageformats/*.dll', 'imageformats'), ('mediaservice/*.dll', 'mediaservice'), ('platforms/*.dll', 'platforms'), ('playlistformats/*.dll', 'playlistformats'), ('printsupport/*.dll', 'printsupport'), ('styles/*.dll', 'styles')],
    datas=[('config/*', 'config'), ('data/db/medical_database.db', 'data/db'), ('db_master_style.qss', '.'), ('db_master.qrc', '.'), ('data_collection2.mp3', '.'), ('endTip.mp3', '.'), ('Pictures/*', 'Pictures'), ('res/*', 'res')],
    hiddenimports=['1','db_data','db_data_analyze','db_left_egg','db_login','db_main','db_master_rc','db_report','db_right_egg','db_school_login','db_set','hook_qt_plugins','local_analy','new_db_data_analyze','new_untitled','test','get_path'],
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
    name='MyAppV4',
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
