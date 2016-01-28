import os
import sys
from setuptools import setup

if sys.version_info[:2] < (2, 7):
    sys.exit('mayalauncher requires Python 2.7 or higher.')

here = os.path.abspath(os.path.dirname(__file__))

# Get long description
with open(os.path.join(here, 'README.rst'), 'r') as f:
    long_description = f.read()

# Get version string.
try:
    import mayalauncher
except ImportError:
    raise RuntimeError('Unable to find mayaluncher module.')


setup(
    name='mayalauncher',
    version=mayalauncher.__version__,
    description='Autodesk Maya application launcher.',
    long_description=long_description,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'Topic :: Multimedia :: Graphics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='autodesk maya launcher',

    author='Marcus Albertsson',
    author_email='marcus.arubertoson@gmail.com',
    url='https://github.com/arubertoson/maya-launcher',
    license='MIT',

    py_modules=['mayalauncher'],
    install_requires=['pathlib2', 'shutilwhich', 'argparse'],
    entry_points={
        'console_scripts': ['mayalauncher = mayalauncher:main']
        }
)
