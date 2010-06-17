#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#$Id: setup.py 902 2009-10-16 16:38:28Z lance $
#-------------------------------------------------------------------------------
"""pyzombie HTTP RESTful handler."""
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
from pyzombie.handlers import HandlerExecSet
from MockRequest import MockRequest
from HTTPResponse import HTTPResponse


class HandlerExecSetGetEmptyTest(unittest.TestCase):
    def runTest(self):
        req = MockRequest()
        hndlr = HandlerExecSet(req, {})
        hndlr.get()

        resp = HTTPResponse(req.wfile.getvalue())
        self.assertEqual("HTTP/1.1", resp.protocol)
        self.assertEqual("200", resp.code)
        self.assertEqual("OK", resp.message)
        self.assertEqual("text/html;UTF-8", resp.header["Content-Type"])
        self.assertEqual(resp.md5, resp.header["ETag"])
        self.assertEqual(int(resp.header["Content-Length"]), len(resp.body))


class HandlerExecSetPostTest(unittest.TestCase):
    LOC_RE = r"""http://MockServer:8008/(zombie_\d{7}T\d{6}Z)"""
    
    def runTest(self):
        data = b"ExecSetPostTest"

        req = MockRequest()
        req.rfile.write(data)
        req.rfile.seek(0)
        req.headers["Content-Type"] = "text/plain"
        req.headers["Content-Length"] = str(len(data))
        hndlr = HandlerExecSet(req, {})
        hndlr.post()
        
        resp = HTTPResponse(req.wfile.getvalue())        
        self.assertEqual("HTTP/1.1", resp.protocol)
        self.assertEqual("201", resp.code)
        self.assertEqual("Created", resp.message)
        self.assertRegexpMatches(resp.header["Location"], self.LOC_RE)
        self.assertEqual(int(resp.header["Content-Length"]), 0)
        
        file = re.match(self.LOC_RE, resp.header["Location"]).group(1)
        self.assertTrue(os.path.isdir(hndlr.executable.dirpath))
        self.assertTrue(os.path.isfile(hndlr.executable.binpath))
        self.assertEquals(open(hndlr.executable.binpath, 'rb').read(), data)



