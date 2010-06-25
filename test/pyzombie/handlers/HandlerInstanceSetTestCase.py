#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#$Id: setup.py 902 2009-10-16 16:38:28Z lance $
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
from pyzombie.Executable import Executable
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

        self.ex = Executable(self.__class__.__name__, mediatype="text/x-python")
        self.ex.writeimage(open(TestSourceCLI.__file__, "r"))
    
    #def tearDown(self):
    #    self.ex.delete()

    def runTest(self):
        data = TestSourceCLI.restful_json()
        req = MockRequest()
        req.rfile.write(data)
        req.rfile.seek(0)
        req.headers["Content-Type"] = "application/json"
        req.headers["Content-Length"] = str(len(data))
        hndlr = HandlerInstanceSet(req, {'execname':self.__class__.__name__})
        hndlr.post()
        hndlr.inst.stdin.close()
        
        resp = HTTPResponse(req.wfile.getvalue())        
        self.assertEqual(resp.protocol, "HTTP/1.1")
        self.assertEqual(resp.code, "201")
        self.assertEqual(resp.message, "Created")
        self.assertRegexpMatches(resp.header["Location"], self.loc_re)
        self.assertEqual(int(resp.header["Content-Length"]), 0)
        
        match = re.match(self.loc_re, resp.header["Location"])        
        instance = list(hndlr.executable.instances)[0]
        
        self.assertTrue(instance.executable.name, match.group(1))
        self.assertTrue(instance.name, match.group(2))
        self.assertTrue(os.path.isdir(instance.datadir))
        
        #test to make sure json state has everything
        #test to make sure stdout is correct
        #test to make sure stderr is correct

