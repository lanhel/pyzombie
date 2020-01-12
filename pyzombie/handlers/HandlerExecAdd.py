#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""pyzombie HTTP RESTful server handler giving a web form to add an
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

__all__ = ["HandlerExecAdd"]

import sys
import io
import logging
import mimetypes
import http.client
from .HandlerLeftovers import HandlerLeftovers


class HandlerExecAdd(HandlerLeftovers):
    """Handle the add executable resource."""

    @classmethod
    def dispatch(cls):
        cls.initdispatch(r"""^/add$""", "GET,POST,OPTIONS,TRACE", "/help/RESTful")
        return cls

    def __init__(self, req, urlargs):
        super().__init__(req, {"leftover": "ExecAdd.html"})

    def post(self):
        fs = self.multipart()
        if fs:
            ctype, enc = mimetypes.guess_type(fs["execfile"].filename)
            self.initexecutable(mediatype=ctype)
            datafp = fs["execfile"].file
            self.executable.writeimage(datafp)
            self.nocache = True
            self.status = http.client.CREATED
            self["Location"] = self.serverurl(self.executable.name)
            self.flush()
        else:
            self.error(http.client.UNSUPPORTED_MEDIA_TYPE)
