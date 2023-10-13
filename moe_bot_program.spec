# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ["moe_bot_program.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=True,
    cipher=block_cipher,
    noarchive=False,
)

a.datas += Tree("./imgs",prefix="./imgs")
a.datas += Tree("./arayuz",prefix="./arayuz")

# splash = Splash("arayuz/splash.png", binaries=a.binaries, datas=a.datas, text_pos=(10, 50), text_size=14, text_color="black",always_on_top=False,full_tk=True)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    #splash,
    #splash.binaries,
    a.binaries,
    a.datas,
    [],
    name="moe_gatherer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch="64bit",
    codesign_identity=None,
    entitlements_file=None,
    icon="arayuz/moe_icon.ico",
)
