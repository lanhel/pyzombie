#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""pyzombie HTTP RESTful server handler returning the representation of an
executable."""
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
__all__ = ["HandlerInstanceStdin"]

import io
import cgi
import http.client
import http.server
from ..Instance import Instance
from .HandlerLeftovers import HandlerLeftovers


class HandlerInstanceStdin(HandlerLeftovers):
    """Executable instance stdin handler."""

    @classmethod
    def dispatch(cls):
        cls.initdispatch(
            r"""^/(?P<execname>\w+)/instances/(?P<instname>\w+)/stdin$""",
            "GET,POST,OPTIONS,TRACE",
            "/help/RESTful",
        )
        return cls

    def __init__(self, req, urlargs):
        urlargs["leftover"] = "InstanceStdin.html"
        super().__init__(req, urlargs)

    def get(self):
        """Handle HTTP GET."""
        name = self.urlargs["instname"]
        inst = Instance.getcached(self.executable, name)
        self.status = http.client.OK
        self.headers["Content-Type"] = "text/html;UTF-8"
        file = self.filepath()
        html = open(file, "r").read()
        html = html.format(self.executable.name, inst.name)
        self.writelines(html)
        self.flush()

    def post(self):
        """Handle HTTP POST."""
        name = self.urlargs["instname"]
        inst = Instance.getcached(self.executable, name)
        postfile = None
        ctype, _ = cgi.parse_header(self.req.headers["Content-Type"])
        if ctype == "text/plain":
            postfile = self.req.rfile
        elif ctype == "multipart/form-data":
            partfile = self.multipart()
            if partfile:
                postfile = io.StringIO(partfile["stdin"])

        if postfile is not None:
            databuf = postfile.read()
            inst.stdin.write(databuf)
        else:
            self.error(http.client.UNSUPPORTED_MEDIA_TYPE)
