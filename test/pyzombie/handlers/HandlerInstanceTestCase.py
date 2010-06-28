#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""pyzombie HTTP RESTful handler test cases."""
__author__ = ('Lance Finn Helsten',)
__version__ = '0.0'
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
import os
import io
import re
import unittest
import http.client
from pyzombie.Executable import Executable
from pyzombie.Instance import Instance
from pyzombie.handlers import HandlerInstance
from MockRequest import MockRequest
from HTTPResponse import HTTPResponse
import TestSourceCLI



class HandlerInstanceGetJsonTest(unittest.TestCase):
    def setUp(self):
        self.ex = Executable.getcached(__name__, mediatype="text/x-python")
        self.ex.writeimage(open(TestSourceCLI.__file__, "r"))
        self.inst = Instance(self.ex, self.__class__.__name__,
        	environ=TestSourceCLI.ENVIRON, arguments=TestSourceCLI.ARGV)
        self.inst.stdin.write(TestSourceCLI.STDIN.encode("UTF-8"))

    def tearDown(self):
        self.ex.delete()

    def runTest(self):
        req = MockRequest()
        req.headers["Accept"] = "spam/eggs; q=1.0, application/json; q=0.5, text/html; q=1.0, text/plain"
        hndlr = HandlerInstance(req, {'execname':__name__, 'instname':self.__class__.__name__})
        self.assertEqual(hndlr.executable, self.ex)
        hndlr.get()

        resp = HTTPResponse(req.wfile.getvalue())
        self.assertEqual(resp.protocol, "HTTP/1.1")
        self.assertEqual(resp.code, str(http.client.OK))
        self.assertEqual(resp.header["Content-Type"], "application/json")
        self.assertEqual(resp.md5, resp.header["ETag"])
        self.assertEqual(int(resp.header["Content-Length"]), len(resp.body))


class HandlerInstanceDeleteTest(unittest.TestCase):
    LOC_RE = r"""http://MockServer:8008/(zombie_\d{7}T\d{6}Z)"""
    
    def setUp(self):
        self.ex = Executable.getcached(__name__, mediatype="text/x-python")
        self.ex.writeimage(open(TestSourceCLI.__file__, "r"))
        self.inst = Instance(self.ex, self.__class__.__name__,
        	environ=TestSourceCLI.ENVIRON, arguments=TestSourceCLI.ARGV)
        self.inst.stdin.write(TestSourceCLI.STDIN.encode("UTF-8"))

    def runTest(self):
        req = MockRequest()
        hndlr = HandlerInstance(req, {'execname':__name__, 'instname':self.__class__.__name__})
        hndlr.delete()
        
        resp = HTTPResponse(req.wfile.getvalue())        
        self.assertEqual(resp.protocol, "HTTP/1.1")
        self.assertEqual(resp.code, str(http.client.OK))
        self.assertFalse(os.path.isdir(self.inst.datadir))

