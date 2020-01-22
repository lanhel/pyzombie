#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""pyzombie HTTP RESTful server."""
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
import pyzombie


class MockSocketConnection:
    class Stream(io.BytesIO):
        def close(self):
            self.value = str(self.getvalue(), "UTF-8")
            super().close()

    def __init__(self, msg):
        self.msg = msg
        self.instream = MockSocketConnection.Stream(msg.encode("iso-8859-1"))
        self.outstream = MockSocketConnection.Stream()

    def makefile(self, mode, bufsize):
        if mode == "rb":
            return self.instream
        elif mode == "wb":
            return self.outstream
        else:
            raise ValueError("Unknown mode: " + mode)


class ZobieRequestGetTest(unittest.TestCase):
    def runTest(self):
        body = """GET /executable/1234 HTTP/1.1

        """
        pass
        # request = MockSocketConnection(body)
        # client = "client"
        # server = "server"
        # pyzombie.ZombieRequest.ZombieRequest(request, client, server)
        # print(request.outstream.value)
