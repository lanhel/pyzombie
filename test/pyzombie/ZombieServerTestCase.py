#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""pyzombie HTTP RESTful server."""
__author__ = ('Lance Finn Helsten',)
__version__ = '1.0.1'
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
if sys.version_info < (3, 0):
    raise Exception("pyzombie requires Python 3.0 or higher.")
import unittest
import io
import pyzombie


class MockSocketConnection():
    class Stream(io.BytesIO):
        def close(self):
            self.value = str(self.getvalue(), "UTF-8")
            super().close()

    def __init__(self, msg):
        self.msg = msg
        self.instream = MockSocketConnection.Stream(msg.encode("iso-8859-1"))
        self.outstream = MockSocketConnection.Stream()
    
    def makefile(self, mode, bufsize):
        if mode == 'rb':
            return self.instream
        elif mode == 'wb':
            return self.outstream
        else:
            raise ValueError("Unknown mode: " + mode)


class ZobieRequestGetTest(unittest.TestCase):    
    def runTest(self):
        body = """GET /executable/1234 HTTP/1.1
        
        """
        pass
        #request = MockSocketConnection(body)
        #client = "client"
        #server = "server"
        #pyzombie.ZombieRequest.ZombieRequest(request, client, server)
        #print(request.outstream.value)



