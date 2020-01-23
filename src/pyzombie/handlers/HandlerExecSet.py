#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""pyzombie HTTP RESTful server handler returning the set of available
executables."""
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
__all__ = ["HandlerExecSet"]

import os
from datetime import datetime
import cgi
import http.client
import http.server
from ..Handler import Handler

INDEX_HTML = """<!DOCTYPE html>
<html lang='en'>
<head>
    <title>pyzombie Executables</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <link rel="Contents" href="/"/>
</head>
<body>
  <h1>pyzombie</h1>
  <h2>Executables</h2>
  <ol>
{0}
  </ol>
</body>
</html>
"""

INDEX_ROW = """    <li><a href="{0}">{0}</a></li>"""


class HandlerExecSet(Handler):
    """Handler for executable set endpoint."""

    @classmethod
    def dispatch(cls):
        """Dispatch definition."""
        cls.initdispatch(r"""^/$""", "GET,POST,OPTIONS,TRACE", "/help/RESTful")
        return cls

    def head(self):
        """Handler for HTTP HEAD."""
        self.content = "Headers"
        self.get()

    def get(self):
        """Handler for HTTP GET."""
        mtime = datetime.utcfromtimestamp(os.path.getmtime(self.datadir))

        dirs = [
            INDEX_ROW.format(d)
            for d in os.listdir(self.datadir)
            if os.path.isdir(os.path.join(self.datadir, d))
        ]
        body = os.linesep.join(dirs)
        html = INDEX_HTML.format(body)

        self.status = http.client.OK
        self["Cache-Control"] = "public max-age=3600"
        self["Last-Modified"] = mtime.strftime("%a, %d %b %Y %H:%M:%S GMT")
        self["Content-Type"] = "text/html;UTF-8"
        self.writelines(html)
        self.flush()

    def post(self):
        """Handler for HTTP POST."""
        ctype, pdict = cgi.parse_header(self.req.headers["Content-Type"])
        self.initexecutable(mediatype=ctype)
        self.executable.writeimage(self.rfile_safe())
        self.nocache = True
        self.status = http.client.CREATED
        self["Location"] = self.serverurl(self.executable.name)
        self.flush()
