"""
Module contains config class for reading and writing json.
"""
from __future__ import print_function, unicode_literals, absolute_import

import errno
import os
import sys
import json
from pathlib import Path


CONFIG_NAME = 'launcher.conf'


def get_system_config_directory():
    """
    Return platform specific config directory.
    """
    platform = sys.platform
    if platform.lower() == 'win32':
        config_path = os.path.expanduser('~')
    elif platform.lower() == 'darwin':
        config_path = os.path.join(os.path.expanduser('~'), 'Library', 'Preferences')
    else:
        config_path = os.getenv('XDG_CONFIG_HOME') or os.path.expanduser('~')
    return config_path


class Config(dict):
    """Config dict object."""

    def __init__(self, file_name=None):
        self.config_file = Path(get_system_config_directory(), '.mam', file_name)
        # Create or fetch config file.
        try:
            self.config_file.parent.mkdir(parents=True)
        except OSError, err:
            if err.errno == errno.EEXIST and self.config_file.parent.is_dir():
                pass
            else:
                raise

        # Base config
        data = {
            'exclude': ['__*', '.*'],
            'icon_ext': ['xpm', 'png', 'bmp', 'jpeg', 'jpg'],
        }
        if not self.config_file.exists():
            with self.config_file.open('w', encoding='utf-8') as f:
                f.write(unicode(json.dumps(data, ensure_ascii=False)))
        else:
            with self.config_file.open('r', encoding='utf-8') as f:
                data = json.loads(f.read())

        super(Config, self).__init__(data)

    def __setitem__(self, key, value):
        super(Config, self).__setitem__(key, value)
        self.dump()

    def dump(self):
        with self.config_file.open('w', encoding='utf-8') as f:
            f.write(unicode(json.dumps(self, indent=4, sort_keys=4,
                                       ensure_ascii=False)))


config = Config(CONFIG_NAME)
