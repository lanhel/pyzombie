#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""pyzombie HTTP RESTful server handler returning the representation of an
executable."""
__author__ = ('Lance Finn Helsten',)
__version__ = '0.0'
__copyright__ = """Copyright (C) 2009 Lance Finn Helsten"""
__license__ = """
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
__docformat__ = "reStructuredText en"

__all__ = ['HandlerInstance']


import sys
import os
import io
import re
import string
from datetime import datetime
import logging
import cgi
import mimetypes
import http.client
import http.server
from ..Handler import Handler


class HandlerInstance(Handler):    
    @classmethod
    def dispatch(cls):
        cls.initdispatch(r"""^/(?P<execname>\w+)/instances/(?P<instname>\w+)/?$""",
            "GET,DELETE,OPTIONS,TRACE",
            "/help/RESTful")
        return cls
            
    def head(self):
        self.content = "Headers"
        self.get()
    
    def get(self):
        name = self.urlargs["instname"]
        if name in self.executable.instances:
            inst = self.executable.instances[name]
            buf = io.StringIO()
            for mediatype in self.accept:
                if mediatype == "application/json":
                    inst.representation_json(buf)
                    break
                elif mediatype == "application/yaml":
                    inst.representation_yaml(buf)
                    break
            if mediatype:
                self["Content-Type"] = mediatype
                self.writelines(buf.getvalue())
                self.status = http.client.OK
                self.flush()
            else:
                self.error(http.client.UNSUPPORTED_MEDIA_TYPE)
        else:
            self.error(http.client.NOT_FOUND)
        
    
    def delete(self):
        name = self.urlargs["instname"]
        if name in self.executable.instances:
            inst = self.executable.instances[name]
            inst.delete()
            self.status = http.client.OK
            self.flush()
        else:
            self.error(http.client.NOT_FOUND)
        

