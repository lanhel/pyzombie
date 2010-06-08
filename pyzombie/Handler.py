#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#$Id: setup.py 902 2009-10-16 16:38:28Z lance $
#-------------------------------------------------------------------------------
"""pyzombie HTTP RESTful resource handler."""
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

__all__ = ['Handler']

import sys
import os
import mimetypes
import hashlib
import re
import http.client

###
### TODO
###

### Pay attention to If-Modified-Since to allow return of 304 Not Modified
### Pay attention to If-None-Match to allow return of 304 Not Modified
### Pay attention to If-Unmodified-Since
### Pay attention to If-Modified-Since


FLUSHED = "Flushed"


class Handler:
    """Holds all the information necessary to handle a single resource dispatch.    
    """
        
    @classmethod
    def initdispatch(cls, regex, allow, help):
        cls.regex = re.compile(regex)
        cls.allow = allow
        cls.help = help
        return cls

    @classmethod
    def match(cls, path):
        """Check to see if the path is recognized by the dispatch handler,
        if so then return a dictionary of recognized parts, otherwise
        return None."""
        ret = None
        mo = cls.regex.match(path)
        if mo != None:
            ret = mo.groupdict()
        return ret
    
    def __init__(self, req, urlargs):
        self.req = req
        self.config = req.config
        self.urlargs = urlargs
        self.content = "Single"
        self.nocache = False
        self.__status = None
        self.headers = {}
        self.lines = []
    
    @property
    def status(self):
        return self.__status
    
    @status.setter
    def status(self, value):
        self.__status = value

    @property
    def startstamp(self):
        return self.req.server.stamp
    
    @property
    def startstamprfc850(self):
        return self.req.server.stamprcf850
    
    @property
    def datadir(self):
        return self.config.get("pyzombie_filesystem", "data")
    
    @property
    def execbase(self):
        return self.config.get("pyzombie_filesystem", "execbase")
    
    @property
    def binaryname(self):
        return self.config.get("pyzombie_filesystem", "binary")
    
    def serverurl(self, path):
        """Given a path to a resource create a full URL to that resource.
        
        Parameters
        ----------
        path
            The relative path on the server to the resource.
        
        Return
        ------
        The URL that can be given to this server to find the given resource.
        """
        return "http://{0}:{1}/{2}".format(
                self.req.server.server_name,
                self.req.server.server_port,
                path)
    
    def binarypaths(self, name):
        """Given a name for a binary file create the path to the directory to
        hold the binary, and a path to the binary itself.
        
        Parameters
        ----------
        name
            Name of the binary.
        
        Return
        ------
        A tuple that gives the path to the containing directory, and the path
        to the binary.
        """
        edir = os.path.normpath(os.path.join(self.datadir, name))
        bin = os.path.normpath(os.path.join(edir, self.binaryname))
        return (edir, bin)
        
    def accept(self):
        """Return an ordered set of media types that will be accepted."""
        if not hasattr(self, "acceptset"):
            astr = self.req.headers["Accept"]
            if astr is None:
                astr = "text/html"
            self.acceptset = self.__parseq(astr)
        return self.acceptset
    
    def acceptlanguage(self):
        """Return an ordered set of languages that will be accepted."""
        if not hasattr(self, "acceptlangset"):
            astr = self.req.headers["Accept-Language"]
            if astr is None:
                astr = "en"
            self.acceptlangset = self.__parseq(astr)
        return self.acceptlangset
    
    def acceptencoding(self):
        """Return an ordered set of langauges that will be accepted."""
        if not hasattr(self, "acceptencset"):
            astr = self.req.headers["Accept-Encoding"]
            if astr is None:
                astr = ""
            self.acceptencset = self.__parseq(astr)
        return self.acceptencset
    
    def __parseq(self, astr):
        astr = astr.split(",")
        aset = ["DUMMY"]
        weight = [0.0]
        for a in astr:
            q = 1.0
            if ";q=" in a:
                a, q = a.split(";")
                q = float(q.replace("q=", ""))
            
            for i, w in enumerate(weight):
                if q > w:
                    aset.insert(i - 1, a)
                    weight.insert(i - 1, w)
                    break
        return aset[:-1]
    
    def readline(self):
        """Read a single line from the input stream in decoded format."""
        pass
    
    def savebody(self, path):
        """Save the body of the request to the given file."""
        out = open(path, "wb")
        length = int(self.req.headers["Content-Length"])
        while length >= 4096:
            bdata = self.req.rfile.read(4096)
            out.write(bdata)
            length = length - 4096
        bdata = self.req.rfile.read(length)
        out.write(bdata)
        out.flush()
        out.close()
    
    def writeline(self, line):
        """Write a single line of text to the output stream."""
        self.lines.append(line)
    
    def writelines(self, lines):
        """Write a string one line at a time to the output stream."""
        for l in lines.splitlines():
            self.writeline(l)
    
    def writefile(self, path):
        """Read and then write the file from the given path to the output
        stream. This will write all the headers before the file. If there is
        an error reading the file then the appropriate HTTP error code will
        be sent.
        
        This is meant for static files. Dynamic files should use writeline
        or writelines to operate.
        
        Parameters:
        path
            The normalized path to the file.
        """
        if os.path.isfile(path):
            data = open(path, "rb").read()
            type, enc = mimetypes.guess_type(path, strict=True)
            self.req.send_response(http.client.OK)
            self.req.send_header("Cache-Control", "public max-age={0}".format(self.req.server.maxagestatic))
            self.req.send_header("Last-Modified", self.req.server.stamprfc850)
            self.req.send_header("ETag", self.etag(data))
            if type == None:
                self.req.send_header("Content-Type", "application/octet-stream")
            else:
                if type in ["text/plain", "text/html"]:
                    type = "{0};UTF-8".format(type)
                self.req.send_header("Content-Type", type)
            if enc != None:
                self.req.send_header("Content-Encoding", enc)
            self.req.send_header("Content-Length", len(data))
            self.req.end_headers()
            self.req.wfile.write(data)
            self.content = FLUSHED
        else:
            self.req.send_error(http.client.NOT_FOUND)
            
        
    def flush(self):
        """Flush the headers if they have not been written and all the lines
        that have been written to the http output stream."""
        
        if self.content == FLUSHED:
            return

        self.lines.append("")
        buf = os.linesep.join(self.lines).encode("UTF-8")
        self.lines = []
        
        if not self.nocache:
            if "Cache-Control" not in self.headers:
                self.headers["Cache-Control"] = "public max-age={0}".format(self.req.server.maxagedynamic)
            
            if "ETag" not in self.headers:
                self.headers["ETag"] = self.etag(buf)
                
        if self.content in ["Headers", "Single", "Chunked"]:
            self.req.send_response(self.status)
            for k in self.headers:
                self.req.send_header(k, self.headers[k])
                
        if self.content == "Headers":
            self.req.end_headers()
            self.content = FLUSHED
        elif self.content == "Single":
            self.req.send_header("Content-Length", len(buf))
            self.req.end_headers()
            self.req.wfile.write(buf)
            self.content = FLUSHED
        elif self.content == "Chunked":
            pass
    
    def etag(self, data):
        """Build an ETag representation for the data associated with the given
        name."""
        m = hashlib.md5()
        m.update(data)
        return m.hexdigest()
    
    def __getitem__(self, key):
        return self.headers[key]
    
    def __setitem__(self, key, value):
        self.headers[key] = value
    

