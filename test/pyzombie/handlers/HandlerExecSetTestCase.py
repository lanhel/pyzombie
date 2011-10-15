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
from pyzombie.handlers import HandlerExecSet
from MockRequest import MockRequest
from HTTPResponse import HTTPResponse


class HandlerExecSetGetEmptyTest(unittest.TestCase):
    def runTest(self):
        req = MockRequest()
        hndlr = HandlerExecSet(req, {})
        hndlr.get()

        resp = HTTPResponse(req.wfile.getvalue())
        self.assertEqual(resp.protocol, "HTTP/1.1")
        self.assertEqual(resp.code, "200")
        self.assertEqual(resp.message, "OK")
        self.assertEqual(resp.header["Content-Type"], "text/html;UTF-8")
        self.assertEqual(resp.md5, resp.header["ETag"])
        self.assertEqual(int(resp.header["Content-Length"]), len(resp.body))


class HandlerExecSetPostTest(unittest.TestCase):
    LOC_RE = r"""http://MockServer:8008/(zombie_\d{7}T\d{6}Z(_\d{3})?)"""
    
    def runTest(self):
        data = self.__class__.__name__.encode("UTF-8")

        req = MockRequest()
        req.rfile.write(data)
        req.rfile.seek(0)
        req.headers["Content-Type"] = "text/plain"
        req.headers["Content-Length"] = str(len(data))
        hndlr = HandlerExecSet(req, {})
        hndlr.post()
        
        resp = HTTPResponse(req.wfile.getvalue())        
        self.assertEqual(resp.protocol, "HTTP/1.1")
        self.assertEqual(resp.code, "201")
        self.assertEqual(resp.message, "Created")
        self.assertRegexpMatches(resp.header["Location"], self.LOC_RE)
        self.assertEqual(int(resp.header["Content-Length"]), 0)
        
        file = re.match(self.LOC_RE, resp.header["Location"]).group(1)
        self.assertTrue(os.path.isdir(hndlr.executable.dirpath))
        self.assertTrue(os.path.isfile(hndlr.executable.binpath))
        self.assertEquals(open(hndlr.executable.binpath, 'rb').read(), data)



