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
import unittest
import io
from http import HTTPStatus
from pyzombie.handlers import HandlerLeftovers
from MockRequest import MockRequest
from HTTPResponse import HTTPResponse


class HandlerLeftoversGetTest(unittest.TestCase):
    def runTest(self):
        req = MockRequest()
        hndlr = HandlerLeftovers(req, {"leftover": "ExecAdd.html"})
        hndlr.get()
        resp = HTTPResponse(req.wfile.getvalue())

        self.assertEqual("HTTP/1.1", resp.protocol)
        self.assertEqual(HTTPStatus.OK.value, resp.code)
        self.assertEqual(HTTPStatus.OK.phrase, resp.message)
        self.assertEqual("text/html;UTF-8", resp.header["Content-Type"])
        self.assertEqual(resp.md5, resp.header["ETag"])
        self.assertEqual(int(resp.header["Content-Length"]), len(resp.body))


class HandlerLeftoversGetFaviconTest(unittest.TestCase):
    def runTest(self):
        req = MockRequest()
        hndlr = HandlerLeftovers(req, {"leftover": "Favicon.ico"})
        hndlr.get()
        resp = HTTPResponse(req.wfile.getvalue())

        self.assertEqual("HTTP/1.1", resp.protocol)
        self.assertEqual(HTTPStatus.OK.value, resp.code)
        self.assertEqual(HTTPStatus.OK.phrase, resp.message)
        self.assertEqual("image/x-icon", resp.header["Content-Type"])
        self.assertEqual(resp.md5, resp.header["ETag"])
        self.assertEqual(int(resp.header["Content-Length"]), len(resp.body))


class HandlerLeftoversBadGetTest(unittest.TestCase):
    def runTest(self):
        req = MockRequest()
        hndlr = HandlerLeftovers(req, {"leftover": "SpamAndEggs.html"})
        hndlr.get()
        resp = HTTPResponse(req.wfile.getvalue())
        self.assertEqual("HTTP/1.1", resp.protocol)
        self.assertEqual(HTTPStatus.NOT_FOUND.value, resp.code)
        self.assertEqual(HTTPStatus.NOT_FOUND.phrase, resp.message)
