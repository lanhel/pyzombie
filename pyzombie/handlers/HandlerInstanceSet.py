#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""pyzombie HTTP RESTful server handler returning the set of available
executables."""
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

__all__ = ['HandlerInstanceSet']


import sys
import os
import re
import string
import json
from datetime import datetime
import logging
import cgi
import http.client
import http.server
from ..Handler import Handler
from ..Instance import Instance

INDEX_HTML = """<!DOCTYPE html>
<html lang='en'>
<head>
    <title>pyzombie {0} Instances</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <link rel="Contents" href="/"/>
</head>
<body>
  <h1>pyzombie</h1>
  <h2>{0} Instances</h2>
  <ol>
{1}
  </ol>
</body>
</html>
"""

INDEX_ROW = """    <li><a href="{0}">{0}</a></li>"""


class HandlerInstanceSet(Handler):    
    @classmethod
    def dispatch(cls):
        cls.initdispatch(r"""^/(?P<execname>\w+)/instances/$""",
                "GET,POST,OPTIONS,TRACE",
                "/help/RESTful")
        return cls
            
    def head(self):
        self.content = "Headers"
        self.get()
    
    def get(self):
        mtime = datetime.utcfromtimestamp(os.path.getmtime(self.executable.dirpath))
        dirs = [INDEX_ROW.format(d)
                for d in os.listdir(self.executable.dirpath)
                if os.path.isdir(os.path.join(self.executable.dirpath, d))]
        body = os.linesep.join(dirs)
        html = INDEX_HTML.format(self.executable.name, body)
        
        self.status = http.client.OK
        self["Cache-Control"] = "public max-age=3600"
        self["Last-Modified"] = mtime.strftime("%a, %d %b %Y %H:%M:%S GMT")
        self["Content-Type"] = "text/html;UTF-8"
        self.writelines(html)
        self.flush()
        
    def post(self):
        ctype, pdict = cgi.parse_header(self.req.headers['Content-Type'])
        if ctype == 'application/yaml':
            self.error(http.client.UNSUPPORTED_MEDIA_TYPE)
            return
        elif ctype == 'application/json':
            body = json.load(self.rfile_safe())
        else:
            self.error(http.client.UNSUPPORTED_MEDIA_TYPE)
            return
        
        if 'environment' in body:
            environ = body['environment']
        else:
            environ = {}
        
        if 'arguments' in body:
            argv = body['arguments']
        else:
            argv = []
        
        self.inst = Instance(self.executable, Instance.createname(), environ=environ,
            arguments=argv)
        self.nocache = True
        self.status = http.client.CREATED
        self["Location"] = self.serverurl(self.inst.restname)
        self.flush()

