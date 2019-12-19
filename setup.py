from setuptools import setup
from ubot.ubot import __version__

packages = [
    "ubot"
]

data_files = [
    ("config", [
        "config/config.ini",
        "config/config.ldplayer.ini",
        "config/config.leapdroid.ini"
    ])
]

setup(
    name="ubot",
    version=__version__,
    packages=packages,
    data_files=data_files,
    entry_points={
        'console_scripts': ['ubot = ubot.ubot:execute']
    },
    zip_safe=False
)
