from setuptools import setup

packages = [
    "ubot"
]

setup(
    name="ubot",
    packages=packages,
    entry_points={
        'console_scripts': ['ubot = main:execute']
    },
)
