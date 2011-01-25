#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""pyzombie HTTP RESTful handler test cases."""
__author__ = ('Lance Finn Helsten',)
__version__ = '1.0'
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
import re
import json
import unittest
from time import sleep
import http.client
from pyzombie.Executable import Executable
from pyzombie.Instance import Instance, DELTA_T
from pyzombie.handlers import HandlerInstance
from MockRequest import MockRequest
from HTTPResponse import HTTPResponse
import TestSourceCLI



class HandlerInstanceGetJsonTest(unittest.TestCase):
    def setUp(self):
        self.ex = Executable.getcached(__name__, mediatype="text/x-python")
        self.ex.writeimage(open(TestSourceCLI.__file__, "r"))
        self.inst = Instance(self.ex, self.__class__.__name__,
        	environ=TestSourceCLI.ENVIRON, arguments=TestSourceCLI.ARGV)
        self.inst.stdin.write(TestSourceCLI.STDIN.encode("UTF-8"))

    def tearDown(self):
        self.ex.delete()
    
    def makeRequest(self):
        req = MockRequest()
        req.headers["Accept"] = "spam/eggs; q=1.0, application/json; q=0.5, text/html;q=0.1, text/plain"

        hndlr = HandlerInstance(req, {'execname':__name__, 'instname':self.__class__.__name__})
        self.assertEqual(hndlr.executable, self.ex)        
        urlself = hndlr.serverurl(path=__name__ + '/instances/' + self.__class__.__name__)
        hndlr.get()

        resp = HTTPResponse(req.wfile.getvalue())
        self.assertEqual(resp.protocol, "HTTP/1.1")
        self.assertEqual(resp.code, str(http.client.OK))
        self.assertEqual(resp.header["Content-Type"], "application/json")
        self.assertEqual(resp.md5, resp.header["ETag"])
        self.assertEqual(int(resp.header["Content-Length"]), len(resp.body))

        state = json.load(io.StringIO(str(resp.body, "UTF-8")))
        self.assertEqual(state['version'], __version__)
        self.assertEqual(state['self'], urlself)
        self.assertEqual(state['stdin'], urlself + "/stdin")
        self.assertEqual(state['stdout'], urlself + "/stdout")
        self.assertEqual(state['stderr'], urlself + "/stderr")
        self.assertEquals(state['returncode'], self.inst.returncode)
        self.assertEquals(state['start'], self.inst.start.strftime('%Y-%m-%dT%H:%M:%SZ'))
        self.assertEquals(state['remove'], self.inst.remove.strftime('%Y-%m-%dT%H:%M:%SZ'))
        
        return req, hndlr, state
    
    def runTest(self):        
        ###
        ### Check while process is running
        ###
        req, hndlr, state = self.makeRequest()
        self.assertIsNone(state['end'])
        environ = state['environ']
        argv = state['arguments']
        
        ###
        ### Let the process stop
        ###        
        self.inst.stdin.close()
        while self.inst.returncode is None:
            sleep(DELTA_T)
        self.inst.stdout.close()
        self.inst.stderr.close()
        
        ###
        ### Recheck the response for a completed process
        ###
        req, hndlr, state = self.makeRequest()
        self.assertEquals(state['end'], self.inst.end.strftime('%Y-%m-%dT%H:%M:%SZ'))
        TestSourceCLI.validateResults(self, self.inst.name, state['returncode'],
                self.inst.stdout, self.inst.stderr)
        self.assertEquals(state['environ'], environ)
        self.assertEquals(state['arguments'], argv)


class HandlerInstanceDeleteTest(unittest.TestCase):
    LOC_RE = r"""http://MockServer:8008/(zombie_\d{7}T\d{6}Z)"""
    
    def setUp(self):
        self.ex = Executable.getcached(__name__, mediatype="text/x-python")
        self.ex.writeimage(open(TestSourceCLI.__file__, "r"))
        self.inst = Instance(self.ex, self.__class__.__name__,
        	environ=TestSourceCLI.ENVIRON, arguments=TestSourceCLI.ARGV)
        self.inst.stdin.write(TestSourceCLI.STDIN.encode("UTF-8"))

    def runTest(self):
        req = MockRequest()
        hndlr = HandlerInstance(req, {'execname':__name__, 'instname':self.__class__.__name__})
        hndlr.delete()
        
        resp = HTTPResponse(req.wfile.getvalue())        
        self.assertEqual(resp.protocol, "HTTP/1.1")
        self.assertEqual(resp.code, str(http.client.OK))
        self.assertFalse(os.path.isdir(self.inst.datadir))

