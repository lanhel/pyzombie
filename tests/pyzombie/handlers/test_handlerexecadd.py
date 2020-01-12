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
from pyzombie.handlers import HandlerExecAdd
from MockRequest import MockRequest
from HTTPResponse import HTTPResponse


class HandlerExecAddGetTest(unittest.TestCase):
    def runTest(self):
        req = MockRequest()
        hndlr = HandlerExecAdd(req, {"execname": self.__class__.__name__})
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


""".format(
            self.boundary, self.__class__.__name__, self.image
        )
        self.form = self.form.replace(os.linesep, "\r\n")
        self.form = self.form.encode("UTF-8")

    def runTest(self):
        req = MockRequest()
        req.readbuf = io.BytesIO(self.form)
        req.headers["Content-Type"] = "multipart/form-data; boundary={0}".format(
            self.boundary
        )
        req.headers["Content-Length"] = str(len(self.form))
        hndlr = HandlerExecAdd(req, {})
        hndlr.post()

        resp = HTTPResponse(req.wfile.getvalue())
        self.assertEqual(resp.protocol, "HTTP/1.1")
        self.assertEqual(resp.code, str(http.client.CREATED))
        self.ex = Executable.getcached(hndlr.executable.name)
        self.assertEqual(str(open(self.ex.binpath, "rb").read(), "UTF-8"), self.image)
