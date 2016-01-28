# -*- coding: utf8 -*-

# Copyright (C) 2016 - Marcus Albertsson <marcus.arubertoson@gmail.com>
# This program is Free Software see LICENSE file for details

"""
Mayalauncher is a python launcher for Autodesk Maya.
"""

import os
import sys
import site
import platform
import logging
import argparse
import subprocess
import ConfigParser
import collections

from pathlib2 import Path
from shutilwhich import which


__version__ = '0.1.5b'

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)

DEBUG = False
DEVELOPER_NAME = 'Autodesk'
APPLICATION_NAME = 'Maya'
APPLICATION_BIN = 'bin'


def get_system_config_directory():
    """
    Return platform specific config directory.
    """
    if platform.system().lower() == 'windows':
        _cfg_directory = Path(os.getenv('APPDATA') or '~')
    elif platform.system().lower() == 'darwin':
        _cfg_directory = Path('~', 'Library', 'Preferences')
    else:
        _cfg_directory = Path(os.getenv('XDG_CONFIG_HOME') or '~/.config')

    logger.debug('Fetching configt directory for {}.'
                 .format(platform.system()))
    return _cfg_directory.joinpath(Path('mayalauncher/.config'))


def get_version_exec_mapping_from_path(path):
    """
    Find valid application version from given path object and return
    a mapping of version, executable.
    """
    versions_exec = {}
    for d in path.iterdir():
        if not d.name.startswith(APPLICATION_NAME):
            continue

        release = d.name.split(APPLICATION_NAME)[-1]
        exec_ = which(APPLICATION_NAME.lower(),
                      path=str(d.joinpath(APPLICATION_BIN)))
        versions_exec[release] = exec_
    return versions_exec


def find_applications_on_system():
    """
    Collect maya version from Autodesk PATH if exists, else try looking
    for custom executable paths from config file.
    """
    # First we collect maya versions from the Autodesk folder we presume
    # is addeed to the system environment "PATH"
    path_env = os.getenv('PATH').split(os.pathsep)
    versions = {}
    for each in path_env:
        path = Path(each).expanduser().resolve()
        if path.name.endswith(DEVELOPER_NAME):
            versions.update(get_version_exec_mapping_from_path(path))
    return versions


class Config(ConfigParser.RawConfigParser):
    """
    Config object for Maya Launch.
    """
    EXLUDE_PATTERNS = ['__*', '*.']
    ICON_EXTENSIONS = ['xpm', 'png', 'bmp', 'jpeg']

    # Sections
    DEFAULTS = 'defaults'
    EXECUTABLES = 'executables'
    PATTERNS = 'patterns'
    ENVIRONMENTS = 'environments'

    def __init__(self, config_file, *args, **kwargs):
        ConfigParser.RawConfigParser.__init__(self, *args, **kwargs)

        self.config_file = config_file
        try:
            self.readfp(self.config_file.open('r'))
        except IOError:
            self._create_default_config_file()

    def _create_default_config_file(self):
        """
        If config file does not exists create and set default values.
        """
        logger.info('Initialize Maya launcher, creating config file...\n')
        self.add_section(self.DEFAULTS)
        self.add_section(self.PATTERNS)
        self.add_section(self.ENVIRONMENTS)
        self.add_section(self.EXECUTABLES)
        self.set(self.DEFAULTS, 'executable', None)
        self.set(self.DEFAULTS, 'environment', None)
        self.set(self.PATTERNS, 'exclude', ', '.join(self.EXLUDE_PATTERNS))
        self.set(self.PATTERNS, 'icon_ext', ', '.join(self.ICON_EXTENSIONS))

        self.config_file.parent.mkdir(exist_ok=True)
        self.config_file.touch()
        with self.config_file.open('wb') as f:
            self.write(f)

        # If this function is run inform the user that a new file has been
        # created.
        sys.exit('Maya launcher has successfully created config file at:\n'
                 ' "{}"'.format(str(self.config_file)))

    def get_list(self, section, option):
        """
        Convert string value to list object.
        """
        if self.has_option(section, option):
            return self.get(section, option).replace(' ', '').split(',')
        else:
            raise KeyError('{} with {} does not exist.'.format(section,
                                                               option))

    def get(self, section, option):
        try:
            return ConfigParser.RawConfigParser.get(self, section, option)
        except ConfigParser.NoOptionError:
            return ''

    def edit(self):
        """
        Edit file with default os application.
        """
        if platform.system().lower() == 'windows':
            os.startfile(str(self.config_file))
        else:
            if platform.system().lower() == 'darwin':
                call = 'open'
            else:
                call = 'xdg-open'
            subprocess.call([call, self.config_file])


def build_config(config_file=get_system_config_directory()):
    """
    Construct the config object from necessary elements.
    """
    config = Config(config_file, allow_no_value=True)
    application_versions = find_applications_on_system()

    # Add found versions to config if they don't exist. Versions found
    # in the config file takes precedence over versions found in PATH.
    for item in application_versions.iteritems():
        if not config.has_option(Config.EXECUTABLES, item[0]):
            config.set(Config.EXECUTABLES, item[0], item[1])
    return config


class EnvironmentList(collections.MutableSequence):
    """
    Converts the system environment
    """
    def __init__(self, environment):
        env = os.getenv(environment)
        self.env = [] if env is None else env.split(os.pathsep)
        self.name = environment

    def __str__(self):
        return '{}'.format(self.env)

    def __repr__(self):
        return '{}({}({}))'.format(self.__class__.__name__, self.name,
                                   self.env)

    def __len__(self):
        return len(self.env)

    def __getitem__(self, item):
        return self.env[item]

    def __setitem__(self, idx, item):
        self.env[idx] = str(item); self.update()

    def __delitem__(self, item):
        self.env.remove(str(item)); self.update()

    def insert(self, idx, value):
        self.env.insert(idx, str(value)); self.update()

    def update(self):
        os.environ[self.name] = os.pathsep.join(self.env)


class MayaEnvironment(object):

    MAYA_SCRIPT_PATH = 'MAYA_SCRIPT_PATH'
    MAYA_PYTHON_PATH = 'PYTHONPATH'
    MAYA_XBMLANG_PATH = 'XBMLANGPATH'
    MAYA_PLUG_IN_PATH = 'MAYA_PLUG_IN_PATH'

    # Identifiers
    PYTHON, MEL = 'py', 'mel'

    def __init__(self, paths=None):
        self.paths = paths or []

        self.script_paths = EnvironmentList(self.MAYA_SCRIPT_PATH)
        self.python_paths = EnvironmentList(self.MAYA_PYTHON_PATH)
        self.xbmlang_paths = EnvironmentList(self.MAYA_XBMLANG_PATH)
        self.plug_in_paths = EnvironmentList(self.MAYA_PLUG_IN_PATH)

        self.exclude_pattern = []
        self.icon_extensions = []

    def has_next(self, gen):
        """
        Check if generator is empty
        """
        try:
            gen.next(); return True
        except StopIteration:
            return False

    def is_excluded(self, path, exclude=None):
        """
        Return if path is in exclude pattern.
        """
        for pattern in (exclude or self.exclude_pattern):
            if path.match(pattern):
                return True
        else:
            return False

    def is_package(self, path):
        return True if self.has_next(path.glob('__init__.py')) else False

    def _walk(self, root):
        for root, dirs, files in os.walk(str(root), topdown=True):

            # Cut unwanted paths from dirs.
            dirs_ = []
            for d in dirs:
                p = Path(d)
                if self.is_excluded(p):
                    continue

                # Dont look further down in packages, assume that
                # they are set up properly
                if not self.is_package(p):
                    dirs_.append(str(p))
                yield Path(root, str(p)).resolve()
            dirs[:] = dirs_

    def get_directories_with_extensions(self, start, extensions=None):
        """
        Look for directories with image extensions in given directory and
        return a list with found dirs.

        .. note:: In deep file structures this might get pretty slow.
        """
        return set([p.parent for ext in extensions for p in start.rglob(ext)])

    def put_path(self, path):
        """
        Given path identify in which environment the path belong to and
        append it.
        """
        if self.is_package(path):
            self.python_paths.append(path)
            xbmdirs = self.get_directories_with_extensions(
                path,
                self.icon_extensions,
                )
            self.xbmlang_paths.extend(xbmdirs)
            return

        if self.has_next(path.glob('*.'+self.MEL)):
            logger.debug('adding {} to mel environ.'.format(str(path)))
            self.script_paths.append(path)

        if self.has_next(path.glob('*.'+self.PYTHON)):
            logger.debug('adding {} to python environ.'.format(str(path)))
            self.python_paths.append(path); site.addsitedir(str(path))

        for ext in self.icon_extensions:
            if self.has_next(path.glob('*.'+ext)):
                logger.debug('adding {} to xbm environ.'.format(str(path)))
                self.xbmlang_paths.append(path)
                break

    def traverse_path_for_valid_application_paths(self, top_path):
        """
        For every path beneath top path that does not contain the exclude
        pattern look for python, mel and images and place them in their
        corresponding system environments.
        """
        self.put_path(Path(top_path))
        for p in self._walk(top_path):
            self.put_path(p)


def flatten_combine_lists(*args):
    """
    Flattens and combines list of lists.
    """
    return [p for l in args for p in l]


def get_environment_paths(config, env):
    """
    Get environment paths from given environment variable.
    """
    if env is None:
        return config.get(Config.DEFAULTS, 'environment')

    # Config option takes precedence over environment key.
    if config.has_option(Config.ENVIRONMENTS, env):
        env = config.get(Config.ENVIRONMENTS, env).replace(' ', '').split(';')
    else:
        env = os.getenv(env)
        if env:
            env = env.split(os.pathsep)
    return env


def build_maya_environment(config, env=None, arg_paths=None):
    """
    Construct maya environment.
    """
    maya_env = MayaEnvironment()
    maya_env.exclude_pattern = config.get_list(Config.PATTERNS, 'exclude')
    maya_env.icon_extensions = config.get_list(Config.PATTERNS, 'icon_ext')

    env = get_environment_paths(config, env)
    if not env and arg_paths is None:
        return logger.info('Using maya factory environment setup.')

    logger.debug('Launching with addon paths: {}'.format(arg_paths))
    logger.debug('Launching with environment paths: {}'.format(env))

    if arg_paths:
        arg_paths = arg_paths.split(' ')
    for directory in flatten_combine_lists(env, arg_paths or ''):
        maya_env.traverse_path_for_valid_application_paths(directory)
    return maya_env


def get_executable_choices(versions):
    """
    Return available Maya releases.
    """
    return [k for k in versions if not k.startswith(Config.DEFAULTS)]


def launch(exec_, file_=None):
    """
    Launches application.
    """
    logger.debug('launcher executable: {}'.format(exec_))
    if not exec_:
        raise RuntimeError(
            'Mayalauncher could not find a maya executable, please specify'
            'a path in the config file (-e) or add the {} directory location'
            'to your PATH system environment.'.format(DEVELOPER_NAME)
           )

    # Launch Maya
    if not DEBUG:
        subprocess.Popen(exec_ if file_ is None else [exec_, file_])


def main():
    """
    Main function of maya launcher. Parses the arguments and tries to
    launch maya with given them.
    """
    config = build_config()

    parser = argparse.ArgumentParser(
        description="""
        Maya Launcher is a useful script that tries to deal with all
        important system environments maya uses when starting up.

        It aims to streamline the setup process of maya to a simple string
        instead of constantly having to make sure paths are setup correctly.
        """
        )

    parser.add_argument(
        'file',
        nargs='?',
        default=None,
        help="""
        file is an optional argument telling maya what file to open with
        the launcher.
        """)

    parser.add_argument(
        '-v', '--version',
        type=str,
        choices=get_executable_choices(dict(config.items(
                                            Config.EXECUTABLES))),
        help="""
        Launch Maya with given version.
        """)

    parser.add_argument(
        '-env', '--environment',
        metavar='env',
        type=str,
        default=config.get(Config.DEFAULTS, 'environment'),
        help="""
        Launch maya with given environemnt, if no environment is specified
        will try to use default value. If not default value is specified
        Maya will behave with factory environment setup.
        """)

    parser.add_argument(
        '-p', '--path',
        metavar='path',
        type=str,
        nargs='+',
        help="""
        Path is an optional argument that takes an unlimited number of paths
        to use for environment creation.

        Useful if you don't want to create a environment variable. Just
        pass the path you want to use.
        """)

    parser.add_argument(
        '-e', '--edit',
        action='store_true',
        help="""
        Edit config file.
        """)

    # Parse the arguments
    args = parser.parse_args()
    if args.edit:
        return config.edit()

    # Get executable from either default value in config or given value.
    # If neither exists exit launcher.
    if args.version is None:
        exec_default = config.get(Config.DEFAULTS, 'executable')
        if not exec_default and config.items(Config.EXECUTABLES):
            items = dict(config.items(Config.EXECUTABLES))
            exec_ = items[sorted(items.keys(), reverse=True)[0]]
        else:
            exec_ = exec_default
    else:
        exec_ = config.get(Config.EXECUTABLES, args.version)

    build_maya_environment(config, args.environment, args.path)
    launch(exec_, args.file)


if __name__ == '__main__':
    main()
