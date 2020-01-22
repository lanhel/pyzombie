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

    ``--address`
        Server address or DNS name (default: localhost).

    ``--port``
        Start pyzombie listening on this port (default: 8008).

    ``--verbose {{critical,error,warning,info,debug}}``
        Change the root logger logging level and the root logger
        handler name ``console`` logging level. Other loggers and
        handlers are unchanged, but named loggers that use ``console``
        handler may emit more log information.

Environment
===========

``${{HOME}}``
    The root location for all directories and files.


Directories and Files
---------------------

    ``${{HOME}}/etc/pyzombie.conf``
        Configuration file.

    ``${{HOME}}/var/run/pyzombie.pid``
        File that contains the current pyzombie process id.

    ``${{HOME}}/var/log/pyzombie``
        Directory that contains pyzombie log files.

    ``${{HOME}}/var/spool/pyzombie``
        Directory that contains executions waiting to run.

    ``${{HOME}}/tmp/pyzombie``
        Directory to contain temporary files.


Configuration
=============

Configuration may be done through command line options or may be set in
configuration files that are read from the following locations (later
files will override settings in earlier files):

    - ``/etc/pyzombie.conf``
    - ``${{HOME}}/.config/pyzombie/pyzombie.conf``
    - ``${{PWD}}/pyzombie.conf``


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
schema. The logging configuraiton will be read from the first file
found in the following locations (if none found then an internal
default configuration will be used):

    - ``${PWD}/pyzombie_logging.conf``
    - ``${HOME}/.config/pyzombie/pyzombie_logging.conf``
    - ``/etc/pyzombie_logging.conf``.

Named Loggers
-------------

``root``
    The default "unamed" logger.

``zombie``
"""
__author__ = ("Lance Finn Helsten",)
__copyright__ = """Copyright 2009 Lance Finn Helsten (helsten@acm.org)"""
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
import os
import errno
import logging
import logging.config
import datetime
import ast
import pathlib
import argparse
from setuptools_scm import get_version
from ..ZombieConfig import config as zombie_config

# from pyzombie import __version__


def configure_logging():
    """Configure the logging system."""

    paths = []
    paths.append(os.getcwd())
    paths.append(os.path.join(os.environ["HOME"], ".config", "pyzombie"))
    paths.append(os.path.join("/", "etc"))
    for dirp in (os.path.join(d, "pyzombie_logging_conf") for d in paths):
        try:
            with open(path, "r") as file:
                conf = ast.literal_eval(file.read())
                logging.config.dictConfig(conf)
            break
        except OSError:
            pass
    else:
        try:
            package = pathlib.PurePosixPath(__file__).parent
            path = package / "logging_default.txt"
            with open(path, "r") as file:
                conf = ast.literal_eval(file.read())
            logdir = pathlib.Path.cwd() / "var" / "log"
            now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            def fixfilename(name):
                filename = f"{name}_{now}.log"
                path = logdir / filename
                conf["handlers"][name]["filename"] = path

            fixfilename("zombie")
            os.makedirs(logdir, exist_ok=True)
            logging.config.dictConfig(conf)
        except OSError as err:
            print(f"Unable to configure logging: {err}", file=sys.stderr)
            sys.exit(errno.EIO)


def parse_commandline(args=None, config=None):
    """Construct commandline parser and then parse arguments.

    :param args: Command line arguments to parse. If none are
        given then ``sys.argv`` is used by default.

    :param config: ``configparser.ConfigParser`` object that
        contains the initial configuration of the system. The
        default is to use ``load_configuration`` to get the
        default.

    :return: A namespace that contains attributes with values
        determined from ``config`` and then command line
        arguments.
    """
    if not config:
        config = zombie_config
    section = config["pyzombie"]

    parser = argparse.ArgumentParser(description="pyzombie service")
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )
    parser.add_argument(
        "--address",
        default=section["address"],
        help=f"Server address or DNS name (default: {section['address']}).",
    )
    parser.add_argument(
        "--port",
        default=section["port"],
        help=f"Start pyzombie listening on this port (default: {section['port']}).",
    )
    parser.add_argument(
        "--verbose",
        default="warning",
        choices=["critical", "error", "warning", "info", "debug"],
        help="Change default logging verbosity.",
    )
    args = parser.parse_args(args)
    return args


def update_configuration(args, config):
    """Update configuration based on environment and arguments."""
    config["pyzombie"]["address"] = args.address
    config["pyzombie"]["port"] = args.port
    config["pyzombie_filesysem"]["home"] = os.environ["HOME"]
