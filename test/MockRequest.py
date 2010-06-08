#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#$Id: setup.py 902 2009-10-16 16:38:28Z lance $
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
import configparser
import http.client
import unittest
from MockServer import MockServer

class MockRequest():
    
    def __init__(self):
        self.server = MockServer()
        self.protocol_version = "HTTP/1.1"
        self.server_version = "MockRequest/" + __version__
        self.error_content_type = "text/plain"
        self.error_message_format = """Code: %(code)d\nMessage: %(message)s\nExplain: %(explain)s"""
        self.config = self.server.config
        self.buffer = io.BytesIO()
    
    def __writeline(self, line):
        self.buffer.write(line.encode("UTF-8"))
        self.buffer.write(os.linesep.encode("UTF-8"))
    
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
    
    @property
    def wfile(self):
        return self.buffer



