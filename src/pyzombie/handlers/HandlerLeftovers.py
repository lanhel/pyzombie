#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""pyzombie HTTP RESTful server handler for root resource."""
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
__all__ = ["HandlerLeftovers"]

import os
from ..Handler import Handler

HTTPFILES = os.path.normpath(os.path.join(os.path.dirname(__file__), "../httpfiles"))


class HandlerLeftovers(Handler):
    """This will handle any normal file resources that are at the root of the
    server. For example '/favicon.ico' or 'base.css'. And then only if it has
    not been handled by a previous handler. All of these files must be in
    httpfiles."""

    @classmethod
    def dispatch(cls):
        """Dispatch definition."""
        cls.initdispatch(
            r"""^/(?P<leftover>.+)?$""", "GET,OPTIONS,TRACE", "/help/RESTful"
        )
        return cls

    def filepath(self):
        """Return the normalized path to the HTTP file identified by "leftover"."""
        file = os.path.join(HTTPFILES, self.urlargs["leftover"])
        file = os.path.normpath(file)
        return file

    def head(self):
        """Handler for HTTP HEAD."""
        self.content = "Headers"
        self.get()

    def get(self):
        """Handler for HTTP GET."""
        file = self.filepath()
        self.writefile(file)
        self.flush()
