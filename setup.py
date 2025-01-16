from setuptools import setup
from setuptools.command.install import install
import os
import shutil
import sys
import platform


if __name__ == '__main__':
    setup(
        cmdclass={
            'install': install,
    })
