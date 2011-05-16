#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""
**Name**
    pyzombied — Start pyzombie server.

**Synopsis**
    ``pyzombied.py [options]``

**Description**
    The ``pyzombied.py`` command shall start the *pyzombie* HTTP RESTful
    server.

**Options**
    ``--home``
        Home directory to override $PYZOMBIEHOME.
    
    ``--config``
        Configuration file. Default: ``$PYZOMBIEHOME/etc/pyzombie.conf``.
    
    ``--deamon``
        Start pyzombie as a deamon under current user.
    
    ``--port``
        Start pyzombie listening on this port. Default: 8008.
    
    ``--verbose``
        Change default logging verbosity: ``critical``, ``error``,
        ``warning``, ``info``, ``debug``.

**Environment**
    PYZOMBIEHOME
        - pyzombie's home directory.
        - Default: current working directory.
        - Demon Mode: current user's home directory or empty if user is root.

**Directories and Files**
    ``$PYZOMBIEHOME/etc/pyzombie.conf``
        Configuration file.
    
    ``$PYZOMBIEHOME/var/run/pyzombie.pid``
        File that contains the current pyzombie process id.
        
    ``$PYZOMBIEHOME/var/log/pyzombie``
        Directory that contains pyzombie log files.
    
    ``$PYZOMBIEHOME/var/spool/pyzombie``
        Directory that contains executions waiting to run.
    
    ``$PYZOMBIEHOME/tmp/pyzombie``
        Directory to contain temporary files.

**Configuration**
    [pyzombie]
        ``address``
            The server address or DNS name: default localhost.
        ``port``
            The TCP/IP port to listen: default 8008.
    
    [pyzombie_filesystem]
        ``var``
            The variable data root directory: default /var
    
    [loggers]
        ``root``
            Required
        ``zombie``
            Required
    
    [handlers]
    
    [formatters]
"""
__author__ = ('Lance Finn Helsten',)
__version__ = '1.0.1'
__copyright__ = """Copyright (C) 2009 Lance Finn Helsten"""
__license__ = """
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
__docformat__ = "reStructuredText en"

import sys
if sys.version_info < (3, 0):
    raise Exception("{0} Requires Python 3.0 or higher.".format(sys.argv[0]))
import os
import errno
import io
import configparser
import logging
from optparse import OptionParser
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


### Parse the arguments
parser = OptionParser(
    description='pyzombie service',
    version='%%prog %s' % (__version__,),
    usage='usage: %prog [options]')

parser.add_option('', '--home',
    action='store', type='string', dest='home', default=None,
    help='Home directory to override $PYZOMBIEHOME.')
parser.add_option('', '--config',
    action='store', type='string', dest='config', default=None,
    help='Configuration file. Default: $PYZOMBIEHOME/etc/pyzombie.conf')
parser.add_option('', '--deamon',
    action='store_true', dest='deamon', default=False,
    help='Start pyzombie as a deamon under current user.')
parser.add_option('', '--port',
        action='store', type='string', dest='port', default=None,
        help='TCP port pyzombie will listen (default: 8008).')
parser.add_option('', '--verbose',
    action='store', type='string', dest='verbose', default=None,
    help='Change default logging verbosity: critical, error, warning, info, debug.')
                
options, args = parser.parse_args()


###
### Environment
###
if 'PYZOMBIEHOME' in os.environ:
    os.environ['PYZOMBIEHOME'] = os.environ['PYZOMBIEHOME']
else:
    if options.deamon:
        if os.environ['USER'] == 'root':
            os.environ['PYZOMBIEHOME'] = '/'
        else:
            os.environ['PYZOMBIEHOME'] = os.environ['HOME']
    else:
        os.environ['PYZOMBIEHOME'] = os.curdir

if not os.path.isdir(resolvepath(os.environ['PYZOMBIEHOME'])):
    print("""$PYZOMBIEHOME="{0[PYZOMBIEHOME]}" does not exist or is not a directory.""".format(os.environ), file=sys.stderr)
    sys.exit(1)

if not options.config:
    options.config = os.path.join(resolvepath(os.environ['PYZOMBIEHOME']), 'etc', 'pyzombie.conf')

print("Configuration:", options.config)
pyzombie.ZombieConfig.config.read(options.config)

if options.port:
    pyzombie.ZombieConfig.config.set('pyzombie', 'port', options.port)
if options.verbose:
    pyzombie.ZombieConfig.config.set('logger_zombie', 'level', options.verbose.upper())


###
### Setup logging configuration
###
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


### Start the zombie
try:
    zombie = pyzombie.ZombieServer()
    zombie.start()
except KeyboardInterrupt:
    print("User cancel.")

