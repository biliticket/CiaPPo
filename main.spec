# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata
import platform

datas = []

if platform.system() == "Windows":
    print(platform.machine())
    if "arm" in platform.machine():
        name = "CiaPPo-Windows-arm"
    else:
        name = "CiaPPo-Windows"
elif platform.system() == "Linux":
    name = "CiaPPo-Linux"
elif platform.system() == "Darwin":
    print(platform.machine())
    if "arm" in platform.machine():
        name = "CiaPPo-macOS-Apple_Silicon"
    elif "64" in platform.machine():
        name = "CiaPPo-macOS-Intel"
    else:
        name = "CiaPPo-macOS"
else:
    name = "CiaPPo"

import os
version = os.environ.get("version", "unknown")
name = f"{version}-{name}"

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
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
    name=name,
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
    runtime_tmp_dir="./ciappo_runtime_tmpdir"
)
