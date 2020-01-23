#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""pyzombie HTTP RESTful server handler for root resource."""
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
__all__ = ["HandlerHelp"]

import os
import http.client
import http.server
from ..Handler import Handler


HELPDIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "../httphelp"))


INDEX_HTML = """<!DOCTYPE html>
<html lang='en'>
<head>
    <title>pyzombie Help Contents</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <link rel="Contents" href="/add"/>
    <link rel="stylesheet" href="/help/help.css" type="text/css" media="screen"/>
</head>
<body>
  <h1>pyzombie Help</h1>
  <ol>
{0}
  </ol>
</body>
</html>
"""

INDEX_ROW = """    <li><a href="help/{0}">{0}</a></li>"""


class HandlerHelp(Handler):
    """Handle the help and documentation resource."""

    @classmethod
    def dispatch(cls):
        """Dispatch definition."""
        cls.initdispatch(
            r"""^/help(/(?P<helpfile>\w+(\.\w+)?)?)?$""",
            "GET,OPTIONS,TRACE",
            "/help/RESTful",
        )
        return cls

    def head(self):
        """Handler for HTTP HEAD."""
        self.content = "Headers"
        self.get()

    def get(self):
        """Handler for HTTP GET."""
        html = None
        if self.urlargs["helpfile"] is None:
            files = [os.path.splitext(f) for f in os.listdir(HELPDIR)]
            files = [INDEX_ROW.format(f[0]) for f in files if f[1] == ".html"]
            body = os.linesep.join(files)
            html = INDEX_HTML.format(body)
            self.status = http.client.OK
            self["Cache-Control"] = "public"
            self["Last-Modified"] = self.startstamprfc850
            self["Content-type"] = "text/html;UTF-8"
            self.writelines(html)
        elif os.path.splitext(self.urlargs["helpfile"])[1] == "":
            file = os.path.join(HELPDIR, self.urlargs["helpfile"] + ".html")
            file = os.path.normpath(file)
            self.writefile(file)
        else:
            file = os.path.join(HELPDIR, self.urlargs["helpfile"])
            file = os.path.normpath(file)
            self.writefile(file)
        self.flush()
