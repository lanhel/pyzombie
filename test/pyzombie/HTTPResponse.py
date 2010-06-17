#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#$Id: setup.py 902 2009-10-16 16:38:28Z lance $
#-------------------------------------------------------------------------------
"""HTTP response parser."""
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

import sys
import os
import io
import hashlib

class HTTPResponse:
    def __init__(self, bytes):
        self.bio = io.BytesIO(bytes)
        #self.strrep = str(bytes, "UTF-8")
        #tio = io.StringIO(self.strrep)
        
        self.protocol, self.code, self.message = self.__readline().strip().split(" ", 2)
        self.header = {}
        line = self.__readline().strip()
        while line != "":
            key, value = line.split(":", 1)
            self.header[key] = value.strip()
            line = self.__readline().strip()
        self.body = self.bio.read()
        
    @property
    def md5(self):
        m = hashlib.md5()
        m.update(self.body)
        return m.hexdigest()
    
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
