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
import os
import io
import re
import unittest
import http.client
from pyzombie.Executable import Executable
from pyzombie.handlers import HandlerExecAdd
from MockRequest import MockRequest
from HTTPResponse import HTTPResponse


class HandlerExecAddGetTest(unittest.TestCase):
    def runTest(self):
        req = MockRequest()
        hndlr = HandlerExecAdd(req, {'execname':self.__class__.__name__})
        hndlr.get()

        resp = HTTPResponse(req.wfile.getvalue())
        self.assertEqual(resp.protocol, "HTTP/1.1")
        self.assertEqual(resp.code, str(http.client.OK))
        self.assertEqual(resp.header["Content-Type"], "text/html;UTF-8")
        self.assertEqual(resp.md5, resp.header["ETag"])
        self.assertEqual(int(resp.header["Content-Length"]), len(resp.body))


class HandlerExecAddPostTest(unittest.TestCase):    
    
    def setUp(self):
        self.image = """{0} Test Image""".format(self.__class__.__name__)
        self.boundary = """NoBodyExpectsTheSpanishInquisition"""
        self.form = """
--{0}
Content-Disposition: form-data; name="execfile"; filename="{1}"
Content-Type: text/x-python

{2}
--{0}
Content-Disposition: form-data; name="add"

Add
--{0}--


""".format(self.boundary, self.__class__.__name__, self.image)
        self.form = self.form.replace(os.linesep, '\r\n')
        self.form = self.form.encode("UTF-8")

    def runTest(self):
        req = MockRequest()
        req.readbuf = io.BytesIO(self.form)
        req.headers["Content-Type"] = "multipart/form-data; boundary={0}".format(self.boundary)
        req.headers["Content-Length"] = str(len(self.form))
        hndlr = HandlerExecAdd(req, {})
        hndlr.post()
        
        resp = HTTPResponse(req.wfile.getvalue())        
        self.assertEqual(resp.protocol, "HTTP/1.1")
        self.assertEqual(resp.code, str(http.client.CREATED))
        self.ex = Executable.getcached(hndlr.executable.name)
        self.assertEqual(str(open(self.ex.binpath, 'rb').read(), "UTF-8"), self.image)
        
    
