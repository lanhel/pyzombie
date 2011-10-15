#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""pyzombie HTTP RESTful handler test cases."""
__author__ = ('Lance Finn Helsten',)
__version__ = '1.0.1'
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
import re
import unittest
from time import sleep
from pyzombie.Executable import Executable
from pyzombie.Instance import DELTA_T
from pyzombie.handlers import HandlerInstanceSet
from MockRequest import MockRequest
from HTTPResponse import HTTPResponse
import TestSourceCLI


class HandlerInstanceSetGetEmpty(unittest.TestCase):
    def runTest(self):
        req = MockRequest()
        hndlr = HandlerInstanceSet(req, {})
        hndlr.get()

        resp = HTTPResponse(req.wfile.getvalue())
        self.assertEqual(resp.protocol, "HTTP/1.1")
        self.assertEqual(resp.code, "200")
        self.assertEqual(resp.message, "OK")
        self.assertEqual(resp.header["Content-Type"], "text/html;UTF-8")
        self.assertEqual(resp.md5, resp.header["ETag"])
        self.assertEqual(int(resp.header["Content-Length"]), len(resp.body))


class HandlerInstanceSetPostJson(unittest.TestCase):
    
    def setUp(self):
        self.loc_re = r"http://MockServer:8008/" + \
            "(" + self.__class__.__name__ + ")" + \
            "/instances/(run_\d{7}T\d{6}Z?)"
        self.ex = Executable.getcached(self.__class__.__name__, mediatype="text/x-python")
        self.ex.writeimage(open(TestSourceCLI.__file__, "r"))
    
    def tearDown(self):
        self.ex.delete()

    def runTest(self):
        data = TestSourceCLI.restful_json()
        req = MockRequest()
        req.rfile.write(data)
        req.rfile.seek(0)
        req.headers["Content-Type"] = "application/json"
        req.headers["Content-Length"] = str(len(data))
        hndlr = HandlerInstanceSet(req, {'execname':self.__class__.__name__})
        hndlr.post()
        
        resp = HTTPResponse(req.wfile.getvalue())        
        self.assertEqual(resp.protocol, "HTTP/1.1")
        self.assertEqual(resp.code, "201")
        self.assertEqual(resp.message, "Created")
        self.assertRegexpMatches(resp.header["Location"], self.loc_re)
        self.assertEqual(int(resp.header["Content-Length"]), 0)
        
        match = re.match(self.loc_re, resp.header["Location"])        
        instance = list(hndlr.executable.instances.values())[0]
        self.assertIsNotNone(instance.process)
        self.assertIsNone(instance.process.returncode)
        instance.stdin.write(TestSourceCLI.STDIN.encode("UTF-8"))
        self.assertIsNone(instance.process.returncode)
        instance.stdin.close()
        self.assertTrue(instance.executable.name, match.group(1))
        self.assertTrue(instance.name, match.group(2))
        self.assertTrue(os.path.isdir(instance.datadir))
        while instance.process.returncode is None:
            sleep(DELTA_T)               
        TestSourceCLI.validateResults(self, self.__class__.__name__, 0,
            instance.stdout, instance.stderr)
        

