#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""pyzombie HTTP RESTful handler test cases."""
__author__ = ("Lance Finn Helsten",)
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
import http.client
from pyzombie.Executable import Executable
from pyzombie.handlers import HandlerExec
from MockRequest import MockRequest
from HTTPResponse import HTTPResponse

IMAGE = """HandlerExecTestCase Test Image"""


class HandlerExecGetTest(unittest.TestCase):
    def setUp(self):
        self.ex = Executable.getcached(
            self.__class__.__name__, mediatype="text/x-python"
        )
        self.ex.writeimage(io.StringIO(IMAGE))

    def tearDown(self):
        self.ex.delete()

    def runTest(self):
        req = MockRequest()
        hndlr = HandlerExec(req, {"execname": self.__class__.__name__})
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
        hndlr = HandlerExec(req, {"execname": self.__class__.__name__})
        hndlr.put()

        resp = HTTPResponse(req.wfile.getvalue())
        self.assertEqual(resp.protocol, "HTTP/1.1")
        self.assertEqual(resp.code, str(http.client.OK))
        self.assertEqual(open(self.ex.binpath, "rb").read(), self.DATA)

    def testInvalidMediaType(self):
        req = MockRequest()
        req.rfile.write(self.DATA)
        req.rfile.seek(0)
        req.headers["Content-Type"] = "text/plain"
        req.headers["Content-Length"] = str(len(self.DATA))
        hndlr = HandlerExec(req, {"execname": self.__class__.__name__})
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
        hndlr = HandlerExec(req, {"execname": self.__class__.__name__})
        hndlr.delete()

        resp = HTTPResponse(req.wfile.getvalue())
        self.assertEqual(resp.protocol, "HTTP/1.1")
        self.assertEqual(resp.code, str(http.client.OK))

        self.assertFalse(os.path.isdir(self.ex.dirpath))
