from setuptools import setup

APP = ['runnet.py']
# 画像ファイルをアプリ内に含めるように指定
DATA_FILES = [
    'fly1.PNG', 'fly2.PNG', 'fly3.PNG', 'fly4.PNG', 'fly4-2.PNG', 'fly5.PNG',
    'kyurun-1.PNG', 'kyurun-2.PNG',
    'sleepy-1.PNG', 'sleepy-2.PNG', 'sleepy-3.PNG', 'sleepy-4.PNG'
]
OPTIONS = {
    'argv_emulation': True,
    'packages': ['rumps'],
    'iconfile': 'icon-shimaenaga.icns', # ← ここでアプリのアイコンを指定
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
