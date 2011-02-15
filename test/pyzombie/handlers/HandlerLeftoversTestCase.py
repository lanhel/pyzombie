#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""pyzombie HTTP RESTful handler test cases."""
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
import unittest
import io
from pyzombie.handlers import HandlerLeftovers
from MockRequest import MockRequest
from HTTPResponse import HTTPResponse


class HandlerLeftoversGetTest(unittest.TestCase):
    def runTest(self):
        req = MockRequest()
        hndlr = HandlerLeftovers(req, {"leftover":"ExecAdd.html"})
        hndlr.get()
        resp = HTTPResponse(req.wfile.getvalue())
                
        self.assertEqual("HTTP/1.1", resp.protocol)
        self.assertEqual("200", resp.code)
        self.assertEqual("OK", resp.message)
        self.assertEqual("text/html;UTF-8", resp.header["Content-Type"])
        self.assertEqual(resp.md5, resp.header["ETag"])
        self.assertEqual(int(resp.header["Content-Length"]), len(resp.body))


class HandlerLeftoversGetFaviconTest(unittest.TestCase):
    def runTest(self):
        req = MockRequest()
        hndlr = HandlerLeftovers(req, {"leftover":"Favicon.ico"})
        hndlr.get()
        resp = HTTPResponse(req.wfile.getvalue())
        
        self.assertEqual("HTTP/1.1", resp.protocol)
        self.assertEqual("200", resp.code)
        self.assertEqual("OK", resp.message)
        self.assertEqual("image/x-icon", resp.header["Content-Type"])
        self.assertEqual(resp.md5, resp.header["ETag"])
        self.assertEqual(int(resp.header["Content-Length"]), len(resp.body))


class HandlerLeftoversBadGetTest(unittest.TestCase):    
    def runTest(self):
        req = MockRequest()
        hndlr = HandlerLeftovers(req, {"leftover":"SpamAndEggs.html"})
        hndlr.get()
        resp = HTTPResponse(req.wfile.getvalue())
        self.assertEqual("HTTP/1.1", resp.protocol)
        self.assertEqual("404", resp.code)
        self.assertEqual("Not Found", resp.message)

