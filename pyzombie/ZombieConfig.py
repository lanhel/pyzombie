#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""pyzombie HTTP RESTful server configuration that conforms to a configparser
interface."""
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

__all__ = []

import sys
import os
import io
import time
import threading
import configparser
from datetime import datetime
from datetime import timedelta
import logging
import logging.config

###
### Initial Configuration
###
CONFIG_INIT = """
[pyzombie]
address:        localhost
port:           8008
maxage_dynamic: 3600
maxage_static:  604800

[pyzombie_filesystem]
execbase:   zombie
binary:     image
instance:   run

var=./build/var
log:        %(var)s/log/pyzombie
run:        %(var)s/run/pyzombie.pid
data:       %(var)s/data/pyzombie
cache:      %(var)s/cache/pyzombie
spool:      %(var)s/spool/pyzombie

[loggers]
keys=root,zombie

[handlers]
keys=consoleHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=DEBUG
handlers=consoleHandler

[logger_zombie]
level=INFO
handlers=consoleHandler
qualname=zombie
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=DEBUG
formatter=simpleFormatter
args=(sys.stdout,)

[formatter_simpleFormatter]
format=%(asctime)s %(levelname)s %(message)s
datefmt=
"""


###
### Global configuration
###
config = configparser.SafeConfigParser()
config.readfp(io.StringIO(CONFIG_INIT))


def datadir():
    ret = config.get("pyzombie_filesystem", "data")
    if ret.startswith("."):
        ret = os.path.join(os.getcwd(), ret)
    ret = os.path.normpath(ret)
    if not os.path.isdir(ret):
        os.makedirs(ret)
    return ret
