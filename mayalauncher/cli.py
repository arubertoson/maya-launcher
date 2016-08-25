from __future__ import absolute_import

import click
from pathlib import Path


class Cli(object):
    def __init__(self, filename=None, verbose=False, maya_version=None,
                 environment='user', extra_paths=None):
        self.filename = filename or ''
        self.verbose = verbose
        self.maya_version = maya_version or 0
        self.environment = environment
        self.extra_paths = extra_paths or []


pass_config = click.make_pass_decorator(Cli, ensure=True)


@click.group()
@click.option('-o', '--open-file', type=click.Path())
@click.option('-v', '--verbose', is_flag=True)
@click.option('-mv', '--maya-version', type=int)
@click.option('-env', '--environment', default='user')
@pass_config
def dispatch(config, open_file, verbose, maya_version, environment):
    """
    Cli commands for controlling maya environments and versions.
    """
    config.verbose = verbose
    click.echo('hello')


@dispatch.command()
@click.argument('extra_paths', nargs=-1, type=click.Path())
@pass_config
def extra_paths(config, extra_paths):
    """
    Add extra paths to parse for maya related files.
    """
    print(extra_paths)
    # for p in extra_paths:
    #     if not p.exists():
    #         if config.verbose:
    #             click.echo('ignoring {}, does not existgs'.format(p))
    #     click.echo(repr(p))
    #     click.echo(dir(p))


@dispatch.command()
@click.option('--no-start', is_flag=True)
@click.option('-e', '--edit', is_flag=True)
@pass_config
def debug(config, no_start, edit):
    """
    Debugging
    """


# @dispatch.group()
# @pass_config
# def config(config):
#     """
#     Config command.
#     """
#     click.echo('config')


# @config.command()
# def edit():
#     """
#     Edit config file.
#     """
#     click.echo('config edit')

