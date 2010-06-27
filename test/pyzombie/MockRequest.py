#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""pyzombie mock request."""
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
import time 
import configparser
import http.client
import unittest
from MockServer import MockServer

class MockHeaders():
    """Handles the case insensitive nature of HTTP headers."""
    def __init__(self):
        self.headers = {}
    
    def __getitem__(self, key):
        return self.headers[key.lower()]
    
    def __setitem__(self, key, value):
        self.headers[key.lower()] = value
    
    def __delitem__(self, key):
        del self.headers[key.lower()]
    
    def __contains__(self, key):
        return key.lower() in self.headers
    
    def __str__(self):
        ret = ["{0}: {1}".format(k, self.headers[k]) for k in self.headers.keys()]
        return os.linesep.join(ret)


class MockRequest():
    """Mocks up an HTTP request for unit testing."""
    
    def __init__(self):
        self.server = MockServer()
        self.protocol_version = "HTTP/1.1"
        self.server_version = "MockRequest/" + __version__
        self.error_content_type = "text/plain"
        self.error_message_format = """Code: %(code)d\nMessage: %(message)s\nExplain: %(explain)s"""
        self.config = self.server.config
    
    def __writeline(self, line):
        self.wfile.write(line.encode("UTF-8"))
        self.wfile.write(os.linesep.encode("UTF-8"))
    
    def send_response(self, code, message=None):
        if message is None:
            message = http.client.responses[code]
        out = "{0} {1} {2}".format(self.protocol_version, code, message)
        self.__writeline(out)
        self.send_header("Server", self.server_version)
    
    def send_error(self, code, message=None):
        self.send_response(code, message)
        self.send_header("Content-Type", self.error_content_type)
        body = (self.error_message_format %
            {'code': code, 'message': message, 'explain': "<no long message>"})
        body = body.encode("UTF-8")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)
    
    def send_header(self, keyword, value):
        out = "{0}: {1}".format(keyword, value)
        self.__writeline(out)
    
    def end_headers(self):
        self.__writeline("")
    
    def date_time_string(timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        return time.strftime(timestamp, "%a, %d %b %Y %H:%M:%S GMT")
    
    @property
    def headers(self):
        if not hasattr(self, '_MockRequest__headers'):
            self.__headers = MockHeaders()
        return self.__headers
        
    @property
    def wfile(self):
        if not hasattr(self, 'writebuf'):
            self.writebuf = io.BytesIO()
        return self.writebuf
    
    @property
    def rfile(self):
        if not hasattr(self, 'readbuf'):
            self.readbuf = io.BytesIO(b"")
        return self.readbuf
    



