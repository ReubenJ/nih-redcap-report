import PyInstaller.__main__

PyInstaller.__main__.run([
    '--name=NIH_Report',
    '--windowed',
    '--onefile',
    'report_app.py'
])
