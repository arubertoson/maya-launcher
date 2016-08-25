import os
import logging
import maya.cmds as cmds


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def set_project(path=None):
    logger.info('\nTrying to find project...')

    path = path or os.path.realpath(os.getcwd())
    root, dirs_ = os.path.splitdrive(path)

    iter_dirs = dirs_.split(os.sep)
    for x in xrange(len(iter_dirs)):
        current_dir = os.path.join(root, os.sep.join(iter_dirs))
        if 'workspace.mel' in os.listdir(current_dir):
            logger.info('Setting workspace to: {}'.format(current_dir))
            cmds.workspace(current_dir, o=True)
            break

        # walk one up
        iter_dirs.pop()


cmds.evalDeferred('set_project')

