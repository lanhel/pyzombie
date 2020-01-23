#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""pyzombie HTTP RESTful server handler giving a web form to add an
executable."""
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
__all__ = ["HandlerExecStart"]

import os
import http.client
from ..Instance import Instance
from .HandlerLeftovers import HandlerLeftovers


class HandlerExecStart(HandlerLeftovers):
    """Handle the add executable resource."""

    @classmethod
    def dispatch(cls):
        """Dispatch definition."""
        cls.initdispatch(
            r"""^/(?P<execname>\w+)/start$""", "GET,POST,OPTIONS,TRACE", "/help/RESTful"
        )
        return cls

    def __init__(self, req, urlargs):
        urlargs["leftover"] = "ExecStart.html"
        super().__init__(req, urlargs)

    def get(self):
        """Handler for HTTP GET."""
        env = [k for k in os.environ]
        env.sort()
        env = ["{0} = {1}".format(k, os.environ[k]) for k in env]
        env = os.linesep.join(env)
        argv = ""

        self.status = http.client.OK
        self.headers["Content-Type"] = "text/html;UTF-8"
        file = self.filepath()
        html = open(file, "r").read()
        html = html.format(self.executable.name, env, argv)
        self.writelines(html)
        self.flush()

    def post(self):
        """Handler for HTTP POST."""
        fs = self.multipart()
        if fs:
            environ = fs.getfirst("environ")
            environ = environ.split("\n")
            environ = [e.split("=") for e in environ]
            environ = [(l.strip(), r.strip()) for l, r in environ]
            environ = dict(environ)

            argv = fs.getfirst("arguments")
            argv = argv.split()
            argv = [a.strip() for a in argv]
            argv = [a for a in argv if a]

            self.inst = Instance(
                self.executable, Instance.createname(), environ=environ, arguments=argv
            )
            self.nocache = True
            self.status = http.client.CREATED
            self["Location"] = self.serverurl(self.inst.restname)
            self.flush()
            # TODO: If the accept type is HTML then do a redirect to the actual instance
        else:
            self.error(http.client.UNSUPPORTED_MEDIA_TYPE)
