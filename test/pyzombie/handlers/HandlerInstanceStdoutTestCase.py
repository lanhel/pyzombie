#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""pyzombie HTTP RESTful handler test cases."""
__author__ = ('Lance Finn Helsten',)
__version__ = '0.1'
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
import random
import threading
import unittest
from time import sleep
import http.client
from pyzombie.Executable import Executable
from pyzombie.Instance import Instance, DELTA_T
from pyzombie.handlers import HandlerInstanceStdout
from MockRequest import MockRequest
from HTTPResponse import HTTPResponse
import TestSourceCopy

BUFFER = [random.randint(ord(' '), ord('~')) for i in range(4096)]
BUFFER = [chr(i) for i in BUFFER]
BUFFER = ''.join(BUFFER)

class StdinFeeder():
    def __call__(self, *args, **kwargs):
        test = kwargs["Test"]
        test.inst.stdin.write(BUFFER.encode("UTF-8"))
        sleep(0.01)
        test.inst.stdin.close()


class HandlerInstanceStdoutGetTest(unittest.TestCase):
    def setUp(self):
        self.ex = Executable.getcached(__name__, mediatype="text/x-python")
        self.ex.writeimage(open(TestSourceCopy.__file__, "r"))
        self.inst = Instance(self.ex, self.__class__.__name__)
        self.thread = threading.Thread(target=StdinFeeder(), kwargs={"Test":self})
        self.daemon = True
        self.thread.start()

    def tearDown(self):
        self.thread.join(0.5)
    #    self.ex.delete()
    
    
    def makeRequest(self, chunked=False):
        req = MockRequest()
        req.headers["Accept"] = "spam/eggs; q=1.0, application/json; q=0.5, text/html;q=0.1, text/plain"

        hndlr = HandlerInstanceStdout(req, {'execname':__name__, 'instname':self.__class__.__name__})
        self.assertEqual(hndlr.executable, self.ex)        
        urlself = hndlr.serverurl(path="{0}/instances/{1}/stdout".format(__name__, self.__class__.__name__))
        hndlr.get()

        resp = HTTPResponse(req.wfile.getvalue())
        self.assertEqual(resp.protocol, "HTTP/1.1")
        self.assertEqual(resp.code, str(http.client.OK))
        self.assertEqual(resp.header["Content-Type"], "text/plain;UTF-8")
        self.assertEqual(resp.md5, resp.header["ETag"])
        return resp

    def runTest(self):
        resp = self.makeRequest()
        self.assertEqual(resp.body, BUFFER)

        
