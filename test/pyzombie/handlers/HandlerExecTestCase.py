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
from pyzombie.handlers import HandlerExec
from MockRequest import MockRequest
from HTTPResponse import HTTPResponse

IMAGE = """HandlerExecTestCase Test Image"""


class HandlerExecGetTest(unittest.TestCase):
    def setUp(self):
        self.ex = Executable.getcached(self.__class__.__name__, mediatype="text/x-python")
        self.ex.writeimage(io.StringIO(IMAGE))

    def tearDown(self):
        self.ex.delete()

    def runTest(self):
        req = MockRequest()
        hndlr = HandlerExec(req, {'execname':self.__class__.__name__})
        hndlr.get()

        resp = HTTPResponse(req.wfile.getvalue())
        self.assertEqual(resp.protocol, "HTTP/1.1")
        self.assertEqual(resp.code, str(http.client.OK))
        self.assertEqual(resp.header["Content-Type"], "text/x-python")
        self.assertEqual(resp.md5, resp.header["ETag"])
        self.assertEqual(int(resp.header["Content-Length"]), len(resp.body))




class HandlerExecPutTest(unittest.TestCase):
    DATA = (IMAGE + " Replace").encode("UTF-8")
    
    def setUp(self):
        self.ex = Executable(self.__class__.__name__, mediatype="text/x-python")
        self.ex.writeimage(io.StringIO(IMAGE))

    def tearDown(self):
        self.ex.delete()

    def testValid(self):
        req = MockRequest()
        req.rfile.write(self.DATA)
        req.rfile.seek(0)
        req.headers["Content-Type"] = "text/x-python"
        req.headers["Content-Length"] = str(len(self.DATA))
        hndlr = HandlerExec(req, {'execname':self.__class__.__name__})
        hndlr.put()
        
        resp = HTTPResponse(req.wfile.getvalue())        
        self.assertEqual(resp.protocol, "HTTP/1.1")
        self.assertEqual(resp.code, str(http.client.OK))        
        self.assertEqual(open(self.ex.binpath, 'rb').read(), self.DATA)
    
    def testInvalidMediaType(self):
        req = MockRequest()
        req.rfile.write(self.DATA)
        req.rfile.seek(0)
        req.headers["Content-Type"] = "text/plain"
        req.headers["Content-Length"] = str(len(self.DATA))
        hndlr = HandlerExec(req, {'execname':self.__class__.__name__})
        hndlr.put()
        
        resp = HTTPResponse(req.wfile.getvalue())        
        self.assertEqual(resp.code, str(http.client.UNSUPPORTED_MEDIA_TYPE))




class HandlerExecDeleteTest(unittest.TestCase):
    LOC_RE = r"""http://MockServer:8008/(zombie_\d{7}T\d{6}Z)"""
    
    def setUp(self):
        self.ex = Executable(self.__class__.__name__, mediatype="text/x-python")
        self.ex.writeimage(io.StringIO(IMAGE))

    def tearDown(self):
        self.ex.delete()

    def runTest(self):
        req = MockRequest()
        hndlr = HandlerExec(req, {'execname':self.__class__.__name__})
        hndlr.delete()
        
        resp = HTTPResponse(req.wfile.getvalue())        
        self.assertEqual(resp.protocol, "HTTP/1.1")
        self.assertEqual(resp.code, str(http.client.OK))
        
        self.assertFalse(os.path.isdir(self.ex.dirpath))

