Maya Launcher
=============

Maya launcher was developed for easy environment setup between maya
sessions. It's easy to use but requires some setup.

Features
~~~~~~~~

-  Utilize *target* in shortcut properties to specify arguments.
-  Given paths are identified and added to the correct system variable.
-  Start several maya sessions with different environment setups.
-  Easily controllable through the commandline/terminal.
-  Highly customizable.

Installing Maya Launcher
------------------------

Maya launcher requires that you have a python version between 2.6 and
2.7. It's not tested with other versions of python.

PyPi
^^^^

mayalauncher is available through the python package as
**mayalauncher**.

::

    pip install mayalauncher

distutils/setuptools
^^^^^^^^^^^^^^^^^^^^

::

    git clone git@github.com:arubertoson/maya-launcher.git
    cd maya-launcher
    python setup.py install

Setup
-----

To make use of *mayalauncher* some setup is required and there is mainly
two ways to work with it.

-  through the config file.
-  through system environments.

You will greatly help maya launcher if you put the Autodesk directory on
your system PATH. This will let the script find all versions of maya
that you have installed and automatically add them as arguments to the
command line script.

**How to edit your system PATH:**

-  `Windows <http://www.howtogeek.com/118594/how-to-edit-your-system-path-for-easy-command-line-access/>`__
-  `UNIX based
   systems <http://hathaway.cc/post/69201163472/how-to-edit-your-path-environment-variables-on-mac>`__

Furthermore you can specify your own system variables to use when launcing
maya.

**How to add system variables:**

-  `Windows <https://www.google.de/search?hl=en&q=how+to+add+system+variables+windows&gws_rd=cr,ssl&ei=qzapVpqiIMucsgGRgoygBA>`__
-  `Unix based
   systems <http://www.cyberciti.biz/faq/set-environment-variable-linux/>`__

So if you added a variable called: **MAYA\_DEV** containing
``['c:/dev;g:/dev']`` and fire ``mayalauncher -env MAYA_DEV``. The
launcher will automatically traverse the paths contained in the
**MAYA\_DEV** variable and add them to their maya environment variables
(*MAYA\_SCRIPT\_PATH*, *PYTHONPATH* ... ).

Using the Config file
~~~~~~~~~~~~~~~~~~~~~

When running mayalauncher the first time it will not try to launch maya.
It will create the config file. To edit the file use the command:

::

    mayalauncher -e

This will probably prompt you to choose an application to open it with.
Choose your preferred text editor. This is the config in its clean
state.

.. code:: ini

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

    [defaults]
    executable=2011
    environment=MAYA_DEV

    [patterns]
    exclude = __*, *.git,
    icon_ext = xpm, png, bmp, jpeg, jpg

    [environments]
    MAYA_USER=c:\users\<user>\documents\maya\scripts, g:/scripts, g:/tools/scripts
    PYTHON_DEV=g:\dev\maya, c:\python27\lib\site-packages

    [executables]
    2015=%PROGRAMFILES%/Autodesk/Maya2015/bin/maya.exe
    2014=%PROGRAMFILES%/Autodesk/Maya2014/bin/maya.exe
    2011=%PROGRAMFILES%/Autodesk/Maya2011/bin/maya.exe

Breakdown
~~~~~~~~~

-  **defaults**

These are the arguments that will be used if you don't explicitly call
them when invoking the command. Meaning

.. code:: bash

    mayalauncher my_file.ma  # This translates to ...
    mayalauncher my_file.ma -env MAYA_DEV -v 2011  # This.

-  **patterns**

   -  **exclude** are the patterns to ignore when traversing the given
      paths. If a path starts with \*\*\_\_\*\* It will be ignored and
      all underlying folder structure will be ignored as well.

   -  **icon\_ext** is essentially what image extensions to look for.

-  **environments**

If you don't want to fiddle with your system environments this is the
substitute. Paths are unlike in the system string divided by "**,**".

::

    environment_name = path1, path2, path3

-  **executables**

Hardcoded paths to your maya executables if you prefer this way over
adding your Autodesk folder to the system PATH.

::

    2010 = /path/to/Maya2010/executable
