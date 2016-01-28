Maya Launcher
=============

Maya launcher was developed for easy environment setup between maya
sessions. It's easy to use but requires some setup.


Features
--------

-  Utilize *target* in shortcut properties to specify arguments.
-  Given paths are identified and added to the correct system variable.
-  Start several maya sessions with different environment setups.
-  Easily controllable through the commandline/terminal.
-  Highly customizable.


Installation
------------

.. code:: bash

    $ pip install mayalauncher


Options
-------

.. code:: bash

    $ mayal -h
    usage: mayal [-h] [-v {2015}] [-env env] [-p path [path ...]] [-e] [file]

    Maya Launcher is a useful script that tries to deal with all important system
    environments maya uses when starting up. It aims to streamline the setup
    process of maya to a simple string instead of constantly having to make sure
    paths are setup correctly.

    positional arguments:
      file                  file is an optional argument telling maya what file to
                            open with the launcher.

    optional arguments:
      -h, --help            show this help message and exit
      -v {2015}, --version {2015}
                            Launch Maya with given version.
      -env env, --environment env
                            Launch maya with given environemnt, if no environment
                            is specified will try to use default value. If not
                            default value is specified Maya will behave with
                            factory environment setup.
      -p path [path ...], --path path [path ...]
                            Path is an optional argument that takes an unlimited
                            number of paths to use for environment creation.
                            Useful if you don't want to create a environment
                            variable. Just pass the path you want to use.
      -e, --edit            Edit config file.


Usage
-----

To make use of *mayalauncher* some setup is required and there is mainly
two ways to work with it: environments and a config file


Environments
^^^^^^^^^^^^

1. Add your Autodesk folder to your system PATH.

   **How to edit your system PATH:**

   -  `Windows <http://www.howtogeek.com/118594/how-to-edit-your-system-path-for-easy-command-line-access/>`__
   -  `UNIX based
      systems <http://hathaway.cc/post/69201163472/how-to-edit-your-path-environment-variables-on-mac>`__


2. Create system variables to store paths that you want to use.

   **How to add system variables:**

   -  `Windows <https://www.google.de/search?hl=en&q=how+to+add+system+variables+windows&gws_rd=cr,ssl&ei=qzapVpqiIMucsgGRgoygBA>`__
   -  `Unix based
      systems <http://www.cyberciti.biz/faq/set-environment-variable-linux/>`__

3. Use maya launcher to start maya with chosen environment and maya release.

.. code:: bash

    $ mayalauncher some_file.ma -env YOUR_ENV -v 2016


Config file
^^^^^^^^^^^

When running mayalauncher the first time it will not try to launch maya.
It will create the config file. To edit the file use the command:

::

    mayalauncher -e

This will most likely prompt you to choose an application to open it with,
your preferred text editor perhaps.

.. code:: ini

    # This is the default state of the config.

    [defaults]
    executable
    environment

    [patterns]
    exclude = __*, *.
    icon_ext = xpm, png, bmp, jpeg

    [environments]

    [executables]

This is how it might look edited.

.. code:: ini

    # Defaults specifies which executable and environment
    # to use when no argument has been provided.
    #
    # NOTE: If executable is empty mayalauncher will try to
    #       find the latest Maya release to launch.
    [defaults]
    executable=2011
    environment=MAYA_DEV

    # Patterns come in two fold:
    #
    # exclude: Define patterns to exclude while walking a directory
    #          structure. Useful when you don't want to jump down
    #          and look through git folders.
    # icon_ext: What image extensions to look for while searching for
    #           xbmlang paths.
    [patterns]
    exclude = __*, *.git,
    icon_ext = xpm, png, bmp, jpeg, jpg


    # Specify environments that mayalauncher can use, follow format:
    # `environment_name=path/to/rootpath, path2/to/otherroot`
    [environments]
    MAYA_USER=c:\users\<user>\documents\maya\scripts, g:/scripts, g:/tools/scripts
    PYTHON_DEV=g:\dev\maya, c:\python27\lib\site-packages

    # Hardcoded paths to maya executables. The preferred way to
    # format is:
    # release_year=/path/to/executable
    [executables]
    2015=%PROGRAMFILES%/Autodesk/Maya2015/bin/maya.exe
    2014=%PROGRAMFILES%/Autodesk/Maya2014/bin/maya.exe
    2011=%PROGRAMFILES%/Autodesk/Maya2011/bin/maya.exe

Resources
---------

* `GitHub repository <https://github.com/arubertoson/maya-launcher>`_
