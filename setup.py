from setuptools import setup

APP = ['runnet.py']
# 画像ファイルをアプリ内に含めるように指定
DATA_FILES = ['sleep.PNG', 'fly-1.PNG', 'kyurun-1.PNG', 'kyurun-2.PNG']
OPTIONS = {
    'argv_emulation': True,
    'packages': ['rumps'],
    'plist': {
        'LSUIElement': True, # Dockアイコンを隠す設定
    }
}

setup(
    app=APP,
    name='PingMonitor', # アプリ名
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
