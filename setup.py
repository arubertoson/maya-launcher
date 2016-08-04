#! /usr/bin/env python

import os
import sys
from setuptools import setup

if sys.version_info[:2] < (2, 7):
    sys.exit('mayalauncher requires Python 2.7 or higher.')

here = os.path.abspath(os.path.dirname(__file__))

# Get long description
try:
    with open(os.path.join(here, 'README.rst'), 'r') as f:
        long_description = f.read()
except IOError:
    pass

setup(
    name='mayalauncher',
    version='0.2.0',
    description='Autodesk Maya application launcher.',
    long_description=long_description,
    author='Marcus Albertsson',
    author_email='marcus.arubertoson@gmail.com',
    url='https://github.com/arubertoson/maya-launcher',
    license='MIT',
    py_modules=['mayalauncher'],
    extras_require={
        ':python_version=="2.6"': [
            'argsparse', 'pathlib', 'shutilwhich',
        ],
        ':python_version=="2.7"': [
            'pathlib', 'shutilwhich',
        ],
        ':python_version=="3.2"': [
            'pathlib', 'shutilwhich',
        ],
        ':python_version=="3.5"': [
            'pathlib', 'shutilwhich',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': ['mayalauncher = mayalauncher:main']},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2',
        'Intended Audience :: End Users/Desktop',
        'Environment :: Console',
    ],
)
