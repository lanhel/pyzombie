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

BUFFER = [random.randint(ord(" "), ord("~")) for i in range(4096)]
BUFFER = [chr(i) for i in BUFFER]
BUFFER = "".join(BUFFER)


class StdinFeeder:
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
        self.thread = threading.Thread(target=StdinFeeder(), kwargs={"Test": self})
        self.daemon = True
        self.thread.start()

    def tearDown(self):
        self.thread.join(0.5)

    #    self.ex.delete()

    def makeRequest(self, chunked=False):
        req = MockRequest()
        req.headers[
            "Accept"
        ] = "spam/eggs; q=1.0, application/json; q=0.5, text/html;q=0.1, text/plain"

        hndlr = HandlerInstanceStdout(
            req, {"execname": __name__, "instname": self.__class__.__name__}
        )
        self.assertEqual(hndlr.executable, self.ex)
        urlself = hndlr.serverurl(
            path="{0}/instances/{1}/stdout".format(__name__, self.__class__.__name__)
        )
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
