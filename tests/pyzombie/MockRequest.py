#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""pyzombie mock request."""
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
import time
import configparser
import http.client
import unittest
from setuptools_scm import get_version
from MockServer import MockServer


class MockHeaders:
    """Handles the case insensitive nature of HTTP headers."""

    def __init__(self):
        self.headers = {}

    def __getitem__(self, key):
        return self.headers[key.lower()]

    def __setitem__(self, key, value):
        self.headers[key.lower()] = value

    def __delitem__(self, key):
        del self.headers[key.lower()]

    def __contains__(self, key):
        return key.lower() in self.headers

    def __str__(self):
        ret = ["{0}: {1}".format(k, self.headers[k]) for k in self.headers.keys()]
        return os.linesep.join(ret)


class MockRequest:
    """Mocks up an HTTP request for unit testing."""

    def __init__(self):
        self.server = MockServer()
        self.protocol_version = "HTTP/1.1"
        self.server_version = "MockRequest/" + get_version()
        self.error_content_type = "text/plain"
        self.error_message_format = (
            """Code: %(code)d\nMessage: %(message)s\nExplain: %(explain)s"""
        )
        self.config = self.server.config

    def __writeline(self, line):
        self.wfile.write(line.encode("UTF-8"))
        self.wfile.write(os.linesep.encode("UTF-8"))

    def send_response(self, code, message=None):
        if message is None:
            message = http.client.responses[code]
        out = "{0} {1} {2}".format(self.protocol_version, code, message)
        self.__writeline(out)
        self.send_header("Server", self.server_version)

    def send_error(self, code, message=None):
        self.send_response(code, message)
        self.send_header("Content-Type", self.error_content_type)
        body = self.error_message_format % {
            "code": code,
            "message": message,
            "explain": "<no long message>",
        }
        body = body.encode("UTF-8")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def send_header(self, keyword, value):
        out = "{0}: {1}".format(keyword, value)
        self.__writeline(out)

    def end_headers(self):
        self.__writeline("")

    def date_time_string(self, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        tm = time.gmtime(timestamp)
        return time.strftime("%a, %d %b %Y %H:%M:%S GMT", tm)

    @property
    def headers(self):
        if not hasattr(self, "_MockRequest__headers"):
            self.__headers = MockHeaders()
        return self.__headers

    @property
    def wfile(self):
        if not hasattr(self, "writebuf"):
            self.writebuf = io.BytesIO()
        return self.writebuf

    @property
    def rfile(self):
        if not hasattr(self, "readbuf"):
            self.readbuf = io.BytesIO(b"")
        return self.readbuf
