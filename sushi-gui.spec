# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['sushi-gui.py'],
    pathex=[],
    binaries=[],
    datas=[('./sushi_rpc_pb2_grpc.py', '.'), ('./sushi_rpc_pb2.py', '.')],
    hiddenimports=['google.protobuf.descriptor'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='sushi-gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch="universal2",
    codesign_identity="Developer ID Application: Modern Ancient Instruments Networked AB (6YBYXC3S8B)",
    entitlements_file=None,
)
app = BUNDLE(
    exe,
    name='sushi-gui.app',
    icon=None,
    bundle_identifier=None,
)
