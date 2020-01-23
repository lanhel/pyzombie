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
import json
import unittest
from time import sleep
import http.client
from http import HTTPStatus
from setuptools_scm import get_version
from pyzombie.Executable import Executable
from pyzombie.Instance import Instance, DELTA_T
from pyzombie.handlers import HandlerInstance
from MockRequest import MockRequest
from HTTPResponse import HTTPResponse
import TestSourceCLI


class HandlerInstanceGetJsonTest(unittest.TestCase):
    def setUp(self):
        self.ex = Executable.getcached(__name__, mediatype="text/x-python")
        self.ex.writeimage(open(TestSourceCLI.__file__, "r"))
        self.inst = Instance(
            self.ex,
            self.__class__.__name__,
            environ=TestSourceCLI.ENVIRON,
            arguments=TestSourceCLI.ARGV,
        )
        self.inst.stdin.write(TestSourceCLI.STDIN.encode("UTF-8"))

    def tearDown(self):
        if not self._outcome.errors:
            self.inst.delete()

    def makeRequest(self):
        req = MockRequest()
        req.headers[
            "Accept"
        ] = "spam/eggs; q=1.0, application/json; q=0.5, text/html;q=0.1, text/plain"

        hndlr = HandlerInstance(
            req, {"execname": __name__, "instname": self.__class__.__name__}
        )
        self.assertEqual(hndlr.executable, self.ex)
        urlself = hndlr.serverurl(
            path=__name__ + "/instances/" + self.__class__.__name__
        )
        hndlr.get()

        resp = HTTPResponse(req.wfile.getvalue())
        self.assertEqual(resp.protocol, "HTTP/1.1")
        self.assertEqual(resp.code, HTTPStatus.OK.value)
        self.assertEqual(resp.header["Content-Type"], "application/json")
        self.assertEqual(resp.md5, resp.header["ETag"])
        self.assertEqual(int(resp.header["Content-Length"]), len(resp.body))

        state = json.load(io.StringIO(str(resp.body, "UTF-8")))
        print(state)
        self.assertEqual(state["version"], get_version())
        self.assertEqual(state["self"], urlself)
        self.assertEqual(state["stdin"], urlself + "/stdin")
        self.assertEqual(state["stdout"], urlself + "/stdout")
        self.assertEqual(state["stderr"], urlself + "/stderr")
        self.assertEqual(state["returncode"], self.inst.returncode)
        self.assertEqual(state["start"], self.inst.start.strftime("%Y-%m-%dT%H:%M:%SZ"))
        self.assertEqual(
            state["remove"], self.inst.remove.strftime("%Y-%m-%dT%H:%M:%SZ")
        )

        return req, hndlr, state

    def runTest(self):
        ###
        ### Check while process is running
        ###
        req, hndlr, state = self.makeRequest()
        self.assertIsNone(state["end"])
        environ = state["environ"]
        argv = state["arguments"]

        ###
        ### Let the process stop
        ###
        self.inst.stdin.close()
        while self.inst.returncode is None:
            sleep(DELTA_T)
        self.inst.stdout.close()
        self.inst.stderr.close()

        ###
        ### Recheck the response for a completed process
        ###
        req, hndlr, state = self.makeRequest()
        self.assertEqual(state["end"], self.inst.end.strftime("%Y-%m-%dT%H:%M:%SZ"))
        TestSourceCLI.validateResults(
            self,
            self.inst.name,
            state["returncode"],
            self.inst.stdout,
            self.inst.stderr,
        )
        self.assertEqual(state["environ"], environ)
        self.assertEqual(state["arguments"], argv)


class HandlerInstanceDeleteTest(unittest.TestCase):
    LOC_RE = r"""http://MockServer:8008/(zombie_\d{7}T\d{6}Z)"""

    def setUp(self):
        self.ex = Executable.getcached(__name__, mediatype="text/x-python")
        self.ex.writeimage(open(TestSourceCLI.__file__, "r"))
        self.inst = Instance(
            self.ex,
            self.__class__.__name__,
            environ=TestSourceCLI.ENVIRON,
            arguments=TestSourceCLI.ARGV,
        )
        self.inst.stdin.write(TestSourceCLI.STDIN.encode("UTF-8"))

    def runTest(self):
        req = MockRequest()
        hndlr = HandlerInstance(
            req, {"execname": __name__, "instname": self.__class__.__name__}
        )
        hndlr.delete()

        resp = HTTPResponse(req.wfile.getvalue())
        self.assertEqual(resp.protocol, "HTTP/1.1")
        self.assertEqual(resp.code, HTTPStatus.OK.value)
        self.assertFalse(os.path.isdir(self.inst.datadir))
