#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""pyzombie mock server."""
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
import io
import datetime
import configparser
import http.client
from pyzombie.ZombieConfig import CONFIG_INIT


class MockServer:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read_file(io.StringIO(CONFIG_INIT))

        self.stamp = datetime.datetime(1966, 8, 29, 11, 53, 22, 435123)
        self.stamprfc850 = self.stamp.strftime("%a, %d %b %Y %H:%M:%S GMT")
        self.stampiso = self.stamp.isoformat()
        self.maxagedynamic = self.config.get("pyzombie", "maxage_dynamic")
        self.maxagestatic = self.config.get("pyzombie", "maxage_static")

    @property
    def server_name(self):
        return "MockServer"

    @property
    def server_port(self):
        return 8008
