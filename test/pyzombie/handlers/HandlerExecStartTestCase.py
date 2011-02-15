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
from time import sleep
import http.client
from pyzombie.Executable import Executable
from pyzombie.Instance import DELTA_T
from pyzombie.handlers import HandlerExecStart
from MockRequest import MockRequest
from HTTPResponse import HTTPResponse
import TestSourceCLI


class HandlerExecStartGetTest(unittest.TestCase):
    def runTest(self):
        req = MockRequest()
        hndlr = HandlerExecStart(req, {'execname':self.__class__.__name__})
        hndlr.get()

        resp = HTTPResponse(req.wfile.getvalue())
        self.assertEqual(resp.protocol, "HTTP/1.1")
        self.assertEqual(resp.code, str(http.client.OK))
        self.assertEqual(resp.header["Content-Type"], "text/html;UTF-8")
        self.assertEqual(resp.md5, resp.header["ETag"])
        self.assertEqual(int(resp.header["Content-Length"]), len(resp.body))


class HandlerExecStartPostTest(unittest.TestCase):    
    
    def setUp(self):
        self.ex = Executable.getcached(self.__class__.__name__, mediatype="text/x-python")
        self.ex.writeimage(open(TestSourceCLI.__file__, "r"))
        self.boundary = """NoBodyExpectsTheSpanishInquisition"""
        environ = TestSourceCLI.ENVIRON
        environ = ["{0} = {1}".format(k, environ[k]) for k in environ.keys()]
        environ = os.linesep.join(environ)
        argv = TestSourceCLI.ARGV
        argv = ' '.join(argv)
        self.form = """
--{0}
Content-Disposition: form-data; name="environ"

{1}
--{0}
Content-Disposition: form-data; name="arguments"

{2}
--{0}--


""".format(self.boundary, environ, argv)
        self.form = self.form.replace(os.linesep, '\r\n')
        self.form = self.form.encode("UTF-8")

    def runTest(self):
        req = MockRequest()
        req.readbuf = io.BytesIO(self.form)
        req.headers["Content-Type"] = "multipart/form-data; boundary={0}".format(self.boundary)
        req.headers["Content-Length"] = str(len(self.form))
        hndlr = HandlerExecStart(req, {'execname':self.ex.name})
        hndlr.post()
        
        resp = HTTPResponse(req.wfile.getvalue())        
        self.assertEqual(resp.protocol, "HTTP/1.1")
        self.assertEqual(resp.code, str(http.client.CREATED))

        self.assertIsNotNone(hndlr.inst.process)
        self.assertIsNone(hndlr.inst.process.returncode)
        hndlr.inst.stdin.write(TestSourceCLI.STDIN.encode("UTF-8"))
        self.assertIsNone(hndlr.inst.process.returncode)
        hndlr.inst.stdin.close()
        self.assertTrue(os.path.isdir(hndlr.inst.datadir))
        while hndlr.inst.process.returncode is None:
            sleep(DELTA_T)               
        TestSourceCLI.validateResults(self, self.__class__.__name__, 0,
            hndlr.inst.stdout, hndlr.inst.stderr)
        
        
    
