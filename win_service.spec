# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['flask_service.py'],
             pathex=['C:\\Personal\\MiniConda\\envs\\flask_service\\Lib\\site-packages'],
             datas=[('C:\\Personal\\project\\flask_service\\custom_config.json','.')],
             hiddenimports=['win32timezone',
                            'altgraph',
                            'Click'
                            'Flask',
                            'future',
                            'itsdangerous',
                            'flask_restful',
                            'Jinja2',
                            'macholib',
                            'MarkupSafe',
                            'pefile',
                            'PyInstaller',
                            'pyodbc',
                            'pywin32',
                            'pywin32-ctypes',
                            'Werkzeug'
                            ],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='flask_service',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='ethylene_scheduling_service')

