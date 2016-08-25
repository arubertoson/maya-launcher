from __future__ import absolute_import

import sys

from .cli import dispatch


def main():
    return dispatch()


if __name__ == "__main__":
    sys.exit(main())
