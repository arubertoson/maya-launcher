"""
Mayalauncher is a python launcher that handles various environment setups
for Autodesk Maya.
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


__version__ = '0.1.2'

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

DEVELOPER_NAME = 'Autodesk'
APPLICATION_NAME = 'Maya'
APPLICATION_BIN = 'bin'


def get_config_directory():
    """
    Return platform specific config directory.
    """
    if platform.system().lower() == 'windows':
        _cfg_directory = Path(os.getenv('APPDATA') or '~')
    elif platform.system().lower() == 'darwin':
        _cfg_directory = Path('~', 'Library', 'Preferences')
    else:
        _cfg_directory = Path(os.getenv('XDG_CONFIG_HOME') or '~/.config')

    logger.debug('Trying to fetch configt directory for {}.'
                 .format(platform.system()))
    return _cfg_directory.joinpath(Path('mayalauncher/.config'))


def build_config(config_file=get_config_directory()):
    """
    Construct the config object from necessary elements.
    """
    config = Config(config_file)
    application_versions = find_applications_on_system()

    # Add found versions to config if they don't exist. Versions found
    # in the config file takes presidence over versions found in PATH.
    for item in application_versions.iteritems():
        if not config.has_option('executables', item[0]):
            config.set('executables', item[0], item[1])
    return config


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
        path = Path(each).resolve()
        if path.name.endswith(DEVELOPER_NAME):
            versions.update(get_version_exec_mapping_from_path(path))
    return versions


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


class Config(ConfigParser.RawConfigParser):
    """
    Config object for Maya Launche.
    """
    EXLUDE_PATTERNS = ['__', '.']
    ICON_EXTENSIONS = ['xpm', 'png', 'bmp']

    def __init__(self, config_file, *args, **kwargs):
        ConfigParser.RawConfigParser.__init__(self, *args, **kwargs)

        self.config_file = config_file
        try:
            self.readfp(self.config_file.open('r'))
        except IOError:
            self._create_default_config_file()

    def _create_default_config_file(self):
        """
        If config file does not exists creat and set default values.
        """
        self.add_section('patterns')
        self.add_section('environments')
        self.add_section('executables')
        self.set('environments', 'default', None)
        self.set('executables', 'default', None)
        self.set('patterns', 'exclude', ', '.join(self.EXLUDE_PATTERNS))
        self.set('patterns', 'icon_ext', ', '.join(self.ICON_EXTENSIONS))

        self.config_file.parent.mkdir(exist_ok=True)
        self.config_file.touch()
        with self.config_file.open('wb') as f:
            self.write(f)

    def get_list(self, section, option):
        """
        Convert string value to list object.
        """
        if self.has_option(section, option):
            return self.get(section, option).replace(' ', '').split(',')
        else:
            raise KeyError('{} with {} does not exist.'.format(section,
                                                               option))

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


def build_maya_environment():
    """
    Construct maya environment.
    """
    maya_env = MayaEnvironment()

    # p = r'G:\dev\maya'
    # maya_env.exclude_pattern = ('__*', '.*')

    # .. todo:: config must intercept before this so exclude pattern
    #           and icon extensions can be set.
    # .. todo:: collect paths from environment and config and pass
    #           them to maya_env for parsing.
    # maya_env.traverse_path_for_valid_application_paths(p)


def collect_user_environment_paths(env=None):
    """
    """
    if env is None:
        return []

    # .. todo:: collect and return paths


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

    def traverse_path_for_valid_application_paths(self, top_path):
        """
        """
        for p in self._walk(top_path):
            self.put_path(p)

    def _walk(self, root):
        logger.debug(self.exclude_pattern)
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

    def is_excluded(self, path, exclude=None):
        """
        Return if path is in exlude pattern.
        """
        for pattern in (exclude or self.exclude_pattern):
            if path.match(pattern):
                return True
        else:
            return False

    def is_package(self, path):
        return True if path.glob('__init__.py') else False

    def put_path(self, path):
        """
        Given path identify in which environment the path belong to and
        append it.
        """
        logger.debug(path)
        if self.is_package(path):
            self.python_paths.append(path)
            self.xbmlang_paths.extend(self.look_for_xbmlang_paths(path))
            return

        if path.glob('*.'+self.MEL).next():
            self.script_paths.append(path)

        if path.glob('*.'+self.PYTHON).next():
            self.python_paths.append(path)

    def look_for_xbmlang_paths(self, path, extensions=None):
        """
        Look for directories with image extensions in given directory and
        return a list with found dirs.

        .. note:: In deep filestructures this might get pretty slow.
        """
        return set([
            p.parent
            for ext in extensions or self.icon_extensions
            for p in path.rglob(ext)
            ])


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


def main():
    """
    """

    version_choices = [
        k for k in dict(config.items(_config_exec))
        if not k.startswith('default')
        ]

    parser = argparse.ArgumentParser(
        description="""
        Maya Launcher is a useful maya launcher that delas with all
        the PYTHONPATH/MAYA_SCRIPT_PATH.. etc under the hood.

        It aims to streamline the startup process of maya to a simple
        "mayalch my_test_file.ma" (provided the default env has been set)
        or create a shortcut with target set to
        "mayalch -env MAYA_DEFAULT" or something similar.
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
        choices=version_choices,
        help="""
        Launch Maya with given version.
        """)

    parser.add_argument(
        '-env', '--environment',
        metavar='env',
        default=config.get(_config_env, 'default'),
        help="""
        Launch maya with given environemnt, if no environment is specified
        will try to use default value. If not default value is specified
        Maya will behave with factory environment setup.
        """)

    parser.add_argument(
        '-p', '--paths',
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
        return open_file(str(config_path))

    # Get executbale from either default value in config or given value.
    # If neither exists exit launcher.
    if args.version is None:
        exec_default = config.get(_config_exec, 'default')
        if exec_default is None:
            raise OSError('No valid Maya executables could be found.')
        else:
            exec_ = exec_default
    else:
        exec_ = config.get(_config_exec, args.version)

    # If we get here its time to find the necessary launch ingridients.
    def collect_paths(env):
        return [Path(os.path.expanduser(p)) for p in env.split(os.pathsep)]

    paths = []
    if args.environment is not None:
        env = os.environ.get(args.environment, None)
        if env is not None:
            paths.extend(collect_paths(env))
        else:
            paths.extend(collect_paths(config.get(_config_env, 'default')))

    if args.path:
        paths.extend(args.path)

    launch(exec_, paths, file_=args.file)


def launch(exec_, paths=None, file_=None):
    """
    Launches application.
    """
    if exec_ is None:
        raise RuntimeError(
            'Mayalauncher could not find a maya executable, please specify'
            'a path in the config file (-e) or add the {} directory location'
            'to your PATH system environment.'.format(DEVELOPER_NAME)
           )

    # Launch Maya
    subprocess.Popen(exec_ if file_ is None else [exec_, file_])

    # .. todo:: find and set maya project


def find_maya_project():
    """
    """
    # traverse where script is launched from backwards and look for
    # workspace.mel files.

    # If found set the project to that directory.
    # else use maya default.


if __name__ == '__main__':
    main()
