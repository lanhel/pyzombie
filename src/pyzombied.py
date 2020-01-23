#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
pyzombie — Start pyzombie server.

*****
Usage
*****

Name
====
    pyzombie

Description
===========
    ``pyzombie`` command starts the *pyzombie* HTTP RESTful server.

Options
=======

    ``-h --help``
        Display help.

    ``--version``
        Show version of pyzombie.

    ``--home``
        Home directory to override $PYZOMBIEHOME.

    ``--config``
        Configuration file. Default: ``$PYZOMBIEHOME/etc/pyzombie.conf``.

    ``--daemon``
        Start pyzombie as a daemon under current user.

    ``--port``
        Start pyzombie listening on this port. Default: 8008.

    ``--verbose {{critical,error,warning,info,debug}}``
        Change the root logger logging level and the root logger
        handler name ``console`` logging level. Other loggers and
        handlers are unchanged, but named loggers that use ``console``
        handler may emit more log information.

Environment
===========

``${HOME}``
    The root location for all directories and files.


Directories and Files
---------------------

    ``${HOME}/etc/pyzombie.conf``
        Configuration file.

    ``${HOME}/var/run/pyzombie.pid``
        File that contains the current pyzombie process id.

    ``${HOME}/var/log/pyzombie``
        Directory that contains pyzombie log files.

    ``${HOME}/var/spool/pyzombie``
        Directory that contains executions waiting to run.

    ``${HOME}/tmp/pyzombie``
        Directory to contain temporary files.


Configuration
=============

Configuration may be done through command line options or may be set in
configuration files that are read from the following locations (later
files will override settings in earlier files):

    - ``/etc/pyzombie.conf``
    - ``${HOME}/.config/pyzombie/pyzombie.conf``
    - ``${PWD}/pyzombie.conf``


Sections and Options
--------------------

``[pyzombie]``

    ``address``
        The server address or DNS name: default localhost.

    ``port``
        The TCP/IP port to listen: default 8008.


Logging
=======

Logging configuration is done through the Python logging dictionary
schema. The logging configuration will be read from the first file
found in the following locations (if none found then an internal
default configuration will be used):

    - ``${PWD}/pyzombie_logging.conf``
    - ``${HOME}/.config/pyzombie/pyzombie_logging.conf``
    - ``/etc/pyzombie_logging.conf``

Named Loggers
-------------

root
    The default "unnamed" logger.

zombie
    The main logger
"""
__author__ = ("Lance Finn Helsten",)
__copyright__ = """Copyright 2009 Flying Titans, Inc."""
__license__ = """
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
__docformat__ = "reStructuredText en"

import sys

if sys.version_info < (3, 8):
    raise Exception("{0} Requires Python 3.8 or higher.".format(sys.argv[0]))

import os
import errno
import io
import configparser
import logging
from optparse import OptionParser
from setuptools_scm import get_version
import pyzombie


###
### Functions
###


def resolvepath(path):
    """Fully resolve the given path into an absolute path taking into account,
    the user, variables, etc.
    """
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    path = os.path.abspath(path)
    return path


def main(args=None):
    """Configure system from CLI arguments and configuration files."""

    import errno

    configure_logging()
    args = parse_commandline(args=args)

    try:
        logconf = io.StringIO()
        pyzombie.ZombieConfig.config.write(logconf)
        logconf.seek(0)
        logging.config.fileConfig(logconf)
    except configparser.NoSectionError:
        logging.config.fileConfig(io.StringIO(CONFIG_INIT))
        logging.getLogger("zombie").setLevel(logging.INFO)
        logging.getLogger().info("Using default logging configuration.")
    logging.getLogger().info("Logging initialized.")

    try:
        zombie = pyzombie.ZombieServer()
        zombie.start()
    except KeyboardInterrupt:
        logging.debug("Keyboard interrupt")
        sys.exit(errno.EINTR)


###
### Environment
###
if "PYZOMBIEHOME" in os.environ:
    os.environ["PYZOMBIEHOME"] = os.environ["PYZOMBIEHOME"]
else:
    if options.daemon:
        if os.environ["USER"] == "root":
            os.environ["PYZOMBIEHOME"] = "/"
        else:
            os.environ["PYZOMBIEHOME"] = os.environ["HOME"]
    else:
        os.environ["PYZOMBIEHOME"] = os.curdir

if not os.path.isdir(resolvepath(os.environ["PYZOMBIEHOME"])):
    print(
        """$PYZOMBIEHOME="{0[PYZOMBIEHOME]}" does not exist or is not a directory.""".format(
            os.environ
        ),
        file=sys.stderr,
    )
    sys.exit(1)

if not options.config:
    options.config = os.path.join(
        resolvepath(os.environ["PYZOMBIEHOME"]), "etc", "pyzombie.conf"
    )

print("Configuration:", options.config)
pyzombie.ZombieConfig.config.read(options.config)

if options.port:
    pyzombie.ZombieConfig.config.set("pyzombie", "port", options.port)
if options.verbose:
    pyzombie.ZombieConfig.config.set("logger_zombie", "level", options.verbose.upper())


if __name__ == "__main__":
    main()
