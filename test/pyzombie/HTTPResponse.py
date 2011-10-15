#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""HTTP response parser."""
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

import sys
import os
import io
import hashlib

class HTTPResponse:
    def __init__(self, bytes):
        self.bio = io.BytesIO(bytes)
        self.strrep = str(bytes, "UTF-8", "replace")
        #tio = io.StringIO(self.strrep)
        
        self.protocol, self.code, self.message = self.__readline().strip().split(" ", 2)
        self.header = {}
        self.__readheaders()
        
        if "Transfer-Encoding" in self.header and self.header["Transfer-Encoding"] == "chunked":
            self.body = ""
            chunksize = int(self.__readline().strip(), 16)
            while chunksize > 0:
                chunk = self.bio.read(chunksize)
                chunk = str(chunk, "UTF-8")
                self.body = self.body + chunk
                chunkend = self.__readline()
                chunksize = self.__readline().strip()
                chunksize = int(chunksize, 16)
            self.__readheaders()
        else:
            self.body = self.bio.read()
        
    @property
    def md5(self):
        m = hashlib.md5()
        if isinstance(self.body, str):
            m.update(self.body.encode("UTF-8"))
        elif isinstance(self.body, bytes):
            m.update(self.body)
        else:
            m.update(str(self.body).encode("UTF-8"))
        return m.hexdigest()
    
    def __readheaders(self):
        line = self.__readline().strip()
        while line != "":
            key, value = line.split(":", 1)
            self.header[key] = value.strip()
            line = self.__readline().strip()
    
    def __readline(self):
        ret = bytearray()
        ch = self.bio.read(1)
        while ch != b'' and ch not in [b"\n", b"\r"]:
            ret.append(ord(ch))
            ch = self.bio.read(1)
        if ch == b"\r":
            ch = self.bio.read(1)
            if ch != b"\n":
                self.bio.seek(-1, io.SEEK_CUR)
        if ch != b'':
            ret = ret + os.linesep.encode("UTF-8")
        return str(ret, "UTF-8")
    
    def __str__(self):
        return self.strrep

