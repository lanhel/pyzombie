#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""pyzombie HTTP RESTful server."""
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
import os
import unittest
import io
import pyzombie
from pyzombie.ZombieConfig import config


class ZombieConfigValuesTest(unittest.TestCase):
    def runTest(self):
        self.assertEqual("localhost", config.get("pyzombie", "address"))
        self.assertEqual("8008", config.get("pyzombie", "port"))

        self.assertEqual("zombie", config.get("pyzombie_filesystem", "execbase"))
        self.assertEqual("image", config.get("pyzombie_filesystem", "binary"))

        def assertVarDir(subdir, file="pyzombie"):
            path = os.path.join(os.getcwd(), "var", subdir, file)
            self.assertEqual(path, config.get("pyzombie_filesystem", subdir))

        assertVarDir("log")
        assertVarDir("run", file="pyzombie.pid")
        assertVarDir("data")
        assertVarDir("cache")
        assertVarDir("spool")
