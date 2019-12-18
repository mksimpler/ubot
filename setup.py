from setuptools import setup, find_packages

packages = [
    "ubot"
]

package_data = {
    "config": [
        "config/config.ini",
        "config/config.ldplayer.ini",
        "config/config.leapdroid.ini"
    ]
}

setup(
    name="ubot",
    packages=packages,
    package_data=package_data,
    include_package_data=True,
    entry_points={
        'console_scripts': ['ubot = ubot.ubot:execute']
    },
    zip_safe=False
)
