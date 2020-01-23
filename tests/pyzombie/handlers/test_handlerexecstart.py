#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""pyzombie HTTP RESTful handler test cases."""
__author__ = ("Lance Finn Helsten",)
__copyright__ = """Copyright 2009 Flying Titans, Inc."""
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
from time import sleep
import http.client
from http import HTTPStatus
from pyzombie.Executable import Executable
from pyzombie.Instance import DELTA_T
from pyzombie.handlers import HandlerExecStart
from MockRequest import MockRequest
from HTTPResponse import HTTPResponse
import TestSourceCLI


class HandlerExecStartGetTest(unittest.TestCase):
    def runTest(self):
        req = MockRequest()
        hndlr = HandlerExecStart(req, {"execname": self.__class__.__name__})
        hndlr.get()

        resp = HTTPResponse(req.wfile.getvalue())
        self.assertEqual(resp.protocol, "HTTP/1.1")
        self.assertEqual(resp.code, HTTPStatus.OK.value)
        self.assertEqual(resp.header["Content-Type"], "text/html;UTF-8")
        self.assertEqual(resp.md5, resp.header["ETag"])
        self.assertEqual(int(resp.header["Content-Length"]), len(resp.body))


class HandlerExecStartPostTest(unittest.TestCase):
    def setUp(self):
        self.ex = Executable.getcached(
            self.__class__.__name__, mediatype="text/x-python"
        )
        self.ex.writeimage(open(TestSourceCLI.__file__, "r"))
        self.boundary = """NoBodyExpectsTheSpanishInquisition"""
        environ = TestSourceCLI.ENVIRON
        environ = ["{0} = {1}".format(k, environ[k]) for k in environ.keys()]
        environ = os.linesep.join(environ)
        argv = TestSourceCLI.ARGV
        argv = " ".join(argv)
        self.form = """
--{0}
Content-Disposition: form-data; name="environ"

{1}
--{0}
Content-Disposition: form-data; name="arguments"

{2}
--{0}--


""".format(
            self.boundary, environ, argv
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
        hndlr = HandlerExecStart(req, {"execname": self.ex.name})
        hndlr.post()

        resp = HTTPResponse(req.wfile.getvalue())
        self.assertEqual(resp.protocol, "HTTP/1.1")
        self.assertEqual(resp.code, HTTPStatus.CREATED.value)

        self.assertIsNotNone(hndlr.inst.process)
        self.assertIsNone(hndlr.inst.process.returncode)
        hndlr.inst.stdin.write(TestSourceCLI.STDIN.encode("UTF-8"))
        self.assertIsNone(hndlr.inst.process.returncode)
        hndlr.inst.stdin.close()
        self.assertTrue(os.path.isdir(hndlr.inst.datadir))
        while hndlr.inst.process.returncode is None:
            sleep(DELTA_T)
        TestSourceCLI.validateResults(
            self, self.__class__.__name__, 0, hndlr.inst.stdout, hndlr.inst.stderr
        )
