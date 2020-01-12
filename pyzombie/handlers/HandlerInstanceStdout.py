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

__all__ = ["HandlerInstanceStdout"]


import sys
import os
import io
import re
import logging
import http.client
import http.server
from ..Handler import Handler
from ..Instance import Instance


class HandlerInstanceStdout(Handler):
    @classmethod
    def dispatch(cls):
        cls.initdispatch(
            r"""^/(?P<execname>\w+)/instances/(?P<instname>\w+)/stdout$""",
            "GET,OPTIONS,TRACE",
            "/help/RESTful",
        )
        return cls

    def head(self):
        self.content = "Headers"
        self.get()

    def get(self):
        name = self.urlargs["instname"]
        inst = Instance.getcached(self.executable, name)
        if inst and inst.returncode is not None:
            self.writefile(inst.stdout_path)
        elif inst and inst.returncode is None:
            self.writefp(inst.stdout, chunked=self.__instdone)
        else:
            self.error(http.client.NOT_FOUND)

    def __instdone(self):
        name = self.urlargs["instname"]
        inst = Instance.getcached(self.executable, name)
        return inst.returncode is not None
