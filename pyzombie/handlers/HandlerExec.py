#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""pyzombie HTTP RESTful server handler returning the representation of an
executable."""
__author__ = ('Lance Finn Helsten',)
__version__ = '1.0.1'
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

__all__ = ['HandlerExec']


import sys
import os
import re
import string
from datetime import datetime
import logging
import cgi
import mimetypes
import http.client
import http.server
from ..Handler import Handler


class HandlerExec(Handler):    
    @classmethod
    def dispatch(cls):
        cls.initdispatch(r"""^/(?P<execname>\w+)/?$""",
                "GET,PUT,DELETE,OPTIONS,TRACE",
                "/help/RESTful")
        return cls
            
    def head(self):
        self.content = "Headers"
        self.get()
    
    def get(self):
        self.writefile(self.executable.binpath)
        self.status = http.client.OK
        self.flush()
        
    def put(self):
        ctype, pdict = cgi.parse_header(self.req.headers['Content-Type'])
        if ctype != self.executable.mediatype[0]:
            self.error(http.client.UNSUPPORTED_MEDIA_TYPE)
        self.executable.writeimage(self.rfile_safe())
        self.status = http.client.OK
        self.flush()

    def delete(self):
        self.executable.delete()
        self.status = http.client.OK
        self.flush()
        

