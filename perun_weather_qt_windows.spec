# PyInstaller build specification: Perun Weather for Windows using PySide6/Qt WebEngine.
#
# Run this file from the project root, where both this file and the
# "perun_weather" package directory are present:
#
#     py -m PyInstaller --clean perun_weather_qt_windows.spec
#
# Output:
#     dist\PerunWeather\PerunWeather.exe
#
# This is a folder build. Keep the whole dist\PerunWeather directory together;

import os
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules

SPEC_DIR = os.path.dirname(os.path.abspath(SPEC))

block_cipher = None

# Application HTML and JavaScript files.
app_datas = [
    ('perun_weather/data/*.html', 'perun_weather/data'),
    ('perun_weather/data/*.js', 'perun_weather/data'),
    ('perun_weather/data/*.css', 'perun_weather/data'),
]

# Qt WebEngine carries Chromium resources, helper executables, ICU data,
# translations and platform plugins. PyInstaller's PySide6 hooks find most
# automatically; these collections make the build explicit and robust.
pyside6_datas = collect_data_files('PySide6')
pyside6_binaries = collect_dynamic_libs('PySide6')
pyside6_hiddenimports = collect_submodules('PySide6.QtWebEngineCore') + [
    'PySide6.QtWebChannel',
    'PySide6.QtWebEngineCore',
    'PySide6.QtWebEngineWidgets',
    'PySide6.QtWidgets',
    'PySide6.QtGui',
    'PySide6.QtCore',
]

# Your source modules are discovered automatically through perun_weather_entry.py.
# The explicit imports below protect optional/indirect modules from being missed.
hidden_imports = pyside6_hiddenimports + [
    'perun_weather.api',
    'perun_weather.alerts',
    'perun_weather.config',
    'perun_weather.normalize',
    'perun_weather.main_windows',
]

a = Analysis(
    ['perun_weather_entry.py'],
    pathex=[],
    binaries=pyside6_binaries,
    datas=app_datas + pyside6_datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'gi',
        'webview',
        'clr',
        'clr_loader',
        'pythonnet',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PerunWeather',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    icon=os.path.join(SPEC_DIR, 'perun_weather.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='PerunWeather',
)
