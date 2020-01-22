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
__all__ = ["HandlerInstance"]

import io
import json
import http.client
import http.server
from ..Handler import Handler
from ..Instance import Instance


class HandlerInstance(Handler):
    """Handler for instance endpoint."""

    @classmethod
    def dispatch(cls):
        """Dispatch definition."""
        cls.initdispatch(
            r"""^/(?P<execname>\w+)/instances/(?P<instname>\w+)/?$""",
            "GET,DELETE,OPTIONS,TRACE",
            "/help/RESTful",
        )
        return cls

    def head(self):
        """Handler for HTTP HEAD."""
        self.content = "Headers"
        self.get()

    def get(self):
        """Handler for HTTP GET."""

        def update_resp(reprfunc, mediatype):
            reprfunc(inst, buf)
            self["Content-Type"] = mediatype
            self.writelines(buf.getvalue())
            self.status = http.client.OK
            self.flush()

        name = self.urlargs["instname"]
        inst = Instance.getcached(self.executable, name)
        if inst:
            buf = io.StringIO()
            for mediatype in self.accept:
                if mediatype == "text/html":
                    update_resp(self.representation_html, mediatype)
                    break
                elif mediatype == "application/json":
                    update_resp(self.representation_json, mediatype)
                    break
                elif mediatype == "application/yaml":
                    update_resp(self.representation_yaml, mediatype)
                    break
            else:
                self.error(http.client.UNSUPPORTED_MEDIA_TYPE)
        else:
            self.error(http.client.NOT_FOUND)

    def delete(self):
        """Handler for HTTP DELETE."""
        name = self.urlargs["instname"]
        if name in self.executable.instances:
            inst = self.executable.instances[name]
            inst.delete()
            self.status = http.client.OK
            self.flush()
        else:
            self.error(http.client.NOT_FOUND)

    def representation_html(self, inst, file):
        """Create an HTML representation of the instance.

        :param file: Pointer to file type object to write the HTML representation.
        """
        inststate = inst.state(self.serverurl(path=""), urlpath="instances")
        html = """<!DOCTYPE html>
<html lang='en'>
<head>
    <title>pyzombie: {name}</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <link rel="Contents" href="/"/>
</head>
<body>
    <h1>pyzombie</h1>
    <h2><a href="{self}">{name}</a></h2>
    <ul>
        <li>Result code: {returncode}</li>
        <li>Started: {start}</li>
        <li>Timeout: {timeout}</li>
        <li>Completed: {end}</li>
        <li>Remove: {remove}</li>
        <li><a href="{stdin}">stdin</a></li>
        <li><a href="{stdout}">stdout</a></li>
        <li><a href="{stderr}">stderr</a></li>
    </ul>
</body>
</html>
""".format(
            **inststate
        )
        file.write(html)

    def representation_json(self, inst, file):
        """Create a JSON representation of the instance.

        :param file: Pointer to file type object to write the JSON representation.
        """
        state = inst.state(self.serverurl(path=""), urlpath="instances")
        json.dump(state, file, sort_keys=True, indent=4)

    def representation_yaml(self, inst, file):
        """Create a YAML representation of the instance.

        :param file: Pointer to file type object to write the JSON
            representation.

        :param urlprefix: The URL scheme, host, port, etc. prefix for
            all URLs in the representation.

        :param urlpath: The additional path information between the
            executable name and the instance name.
        """
        state = inst.state(self.serverurl(path=""), urlpath="instances")
