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

import os
import io
from configparser import ConfigParser, ExtendedInterpolation


CONFIG_INIT = f"""
[pyzombie]
    address:        localhost
    port:           8008
    maxage_dynamic: 3600
    maxage_static:  604800

[pyzombie_filesystem]
    execbase:   zombie
    binary:     image
    instance:   run

    home:       {os.getcwd()}
    var:        ${{home}}/var
    log:        ${{var}}/log/pyzombie
    run:        ${{var}}/run/pyzombie.pid
    data:       ${{var}}/data/pyzombie
    cache:      ${{var}}/cache/pyzombie
    spool:      ${{var}}/spool/pyzombie
"""


config = ConfigParser(interpolation=ExtendedInterpolation())
config.read_file(io.StringIO(CONFIG_INIT))
paths = config.read(
    [
        os.path.join("/", "etc"),
        os.path.join(os.environ["HOME"], ".config", "pyzombie", "pyzombie.conf"),
        os.path.join(os.getcwd(), "etc", "pyzombie.conf"),
    ]
)


def datadir():
    """Data directory in the pyzombie filesytem."""
    ret = config.get("pyzombie_filesystem", "data")
    if ret.startswith("."):
        ret = os.path.join(os.getcwd(), ret)
    ret = os.path.normpath(ret)
    if not os.path.isdir(ret):
        os.makedirs(ret)
    return ret
