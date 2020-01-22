#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""pyzombie HTTP RESTful resource handler."""
__author__ = ("Lance Finn Helsten",)
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
__all__ = ["Handler"]

import sys
import os
import mimetypes
import hashlib
import re
import cgi
import http.client
from .ZombieConfig import datadir
from .Executable import Executable

# cgitb.enable()


###
### TODO
###

### Pay attention to If-Modified-Since to allow return of 304 Not Modified
### Pay attention to If-None-Match to allow return of 304 Not Modified
### Pay attention to If-Unmodified-Since
### Pay attention to If-Modified-Since


CHUNK_SIZE = 256
FLUSHED = "Flushed"


class Handler:
    """Holds all the information necessary to handle a single resource dispatch.

    :param executable: The Executable object for this handler. In rare
        cases no executable can be determined so this will return None.
    """

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-public-methods

    @classmethod
    def initdispatch(cls, regex, allow, helppath):
        """Initialize dispatch table."""
        cls.regex = re.compile(regex)
        cls.allow = allow
        cls.help = helppath
        return cls

    @classmethod
    def match(cls, path):
        """Check to see if the path is recognized by the dispatch handler,
        if so then return a dictionary of recognized parts, otherwise
        return None."""
        ret = None
        mo = cls.regex.match(path)
        if mo is not None:
            ret = mo.groupdict()
        return ret

    def __init__(self, req, urlargs):
        self.req = req
        self.urlargs = urlargs
        self.content = "Single"
        self.nocache = False
        self.__status = None
        self.headers = {}
        self.lines = []
        self.__acceptset = None
        self.__acceptlangset = None
        self.__acceptencset = None
        self.__etag = None
        self.__executable = None

    @property
    def status(self):
        """Current response status of this request."""
        return self.__status

    @status.setter
    def status(self, value):
        self.__status = value

    @property
    def startstamp(self):
        """Return timestamp of the request."""
        return self.req.server.stamp

    @property
    def startstamprfc850(self):
        """Return timestamp as RFC850 string."""
        return self.req.date_time_string()

    @property
    def datadir(self):
        """Return path to data directory used by this request."""
        return datadir()

    @property
    def executable(self):
        """Return the Executable object for this request."""
        if self.__executable is None:
            self.initexecutable()
        return self.__executable

    @property
    def accept(self):
        """Return an ordered set of media types that will be accepted."""
        if not self.__acceptset:
            astr = self.req.headers["Accept"]
            if astr is None:
                astr = "text/html"
            self.__acceptset = self.__parseq(astr)
            self.__acceptset.append(None)
        return self.__acceptset

    @property
    def acceptlanguage(self):
        """Return an ordered set of languages that will be accepted."""
        if not self.__acceptlangset:
            astr = self.req.headers["Accept-Language"]
            if astr is None:
                astr = "en"
            self.__acceptlangset = self.__parseq(astr)
            self.__acceptlangset.append(None)
        return self.__acceptlangset

    @property
    def acceptencoding(self):
        """Return an ordered set of langauges that will be accepted."""
        if not self.__acceptencset:
            astr = self.req.headers["Accept-Encoding"]
            if astr is None:
                astr = ""
            self.__acceptencset = self.__parseq(astr)
            self.__acceptencset.append(None)
        return self.__acceptencset

    def __parseq(self, astr):
        # pylint: disable=no-self-use
        # pylint: disable=invalid-name

        qre = re.compile(r"([a-zA-Z*]+/[a-zA-Z*]+)(\s*;\s*q=(\d+(\.\d+))?)?")
        astr = astr.split(",")
        aset = ["DUMMY"]
        weight = [0.0]
        for a in astr:
            q = 1.0
            m = qre.match(a.strip())
            if m:
                a = m.group(1)
                if m.group(3):
                    q = float(m.group(3))
            for i, w in enumerate(weight):
                if q > w:
                    aset.insert(i, a)
                    weight.insert(i, q)
                    break
        return aset[:-1]

    def initexecutable(self, mediatype=None):
        """This will initialize the executable property with a given media
        type. Generally using the executable property directly will give
        correct results. This is really only used when POST of a new exectuable
        occurs."""
        if self.__executable is not None:
            raise AttributeError("Executable property is already initialized.")
        if "execname" in self.urlargs:
            name = self.urlargs["execname"]
        else:
            name = Executable.createname()
        self.__executable = Executable.getcached(name, mediatype)
        assert self.__executable is not None

    def serverurl(self, path):
        """Given a path to a resource create a full URL to that resource.

        :param path: The relative path on the server to the resource.

        :return: The URL that can be given to this server to find the
            given resource.
        """
        return "http://{0}:{1}/{2}".format(
            self.req.server.server_name, self.req.server.server_port, path
        )

    def rfile_safe(self):
        """Return a safe filepointer."""
        return self.req.rfile

    def multipart(self):
        """Return field storage from request."""
        ctype, _ = cgi.parse_header(self.req.headers["Content-Type"])
        if ctype != "multipart/form-data":
            self.error(http.client.UNSUPPORTED_MEDIA_TYPE)
            return None
        fp = self.rfile_safe()
        ret = cgi.FieldStorage(
            fp=fp,
            headers=self.req.headers,
            environ={"REQUEST_METHOD": "POST"},
            strict_parsing=True,
        )
        return ret

    def readline(self):
        """Read a single line from the input stream in decoded format."""

    def writeline(self, line):
        """Write a single line of text to the output stream."""
        self.lines.append(line)

    def writelines(self, lines):
        """Write a string one line at a time to the output stream."""
        for line in lines.splitlines():
            self.writeline(line)

    def writefile(self, path):
        """Read and then write the file from the given path to the output
        stream. This will write all the headers before the file. If there is
        an error reading the file then the appropriate HTTP error code will
        be sent.

        This is meant for static files. Dynamic files should use writeline
        or writelines to operate.

        :param path: The normalized path to the file.
        """
        if os.path.isfile(path):
            mediatype, enc = mimetypes.guess_type(path)
            self.writefp(open(path, "rb"), mediatype=mediatype, enc=enc)
        else:
            self.error(http.client.NOT_FOUND)

    def writefp(self, fp, mediatype="text/plain", enc=None, chunked=None):
        """Read from the given file object and write the data to the output
        stream. If this is chunked then this will not return until the input
        file object is closed.

        :param fp: The file type object to read from.
        :param chunked: If not ``None`` then the data should be sent in
            a chunked manner, and the value should be a function that
            returns a boolean value to indicate all data has been sent.
            The default is no chunked.
        """
        self.req.send_response(http.client.OK)
        self.req.send_header(
            "Cache-Control", "public max-age={0}".format(self.req.server.maxagestatic)
        )
        self.req.send_header("Last-Modified", self.req.date_time_string())
        if mediatype is None:
            self.req.send_header("Content-Type", "application/octet-stream")
        else:
            if mediatype in ["text/plain", "text/html"]:
                mediatype = "{0};UTF-8".format(mediatype)
            self.req.send_header("Content-Type", mediatype)
        if enc is not None:
            self.req.send_header("Content-Encoding", enc)

        if chunked is not None:
            self.__etag_init()
            self.content = "Chunked"
            self.req.send_header("Transfer-Encoding", "chunked")
            self.req.end_headers()
            length = 0
            done = False
            while not done:
                data = fp.read(CHUNK_SIZE)
                while not data and not done:
                    data = fp.read(CHUNK_SIZE)
                    done = chunked()
                if data:
                    datalen = len(data)
                    length = length + datalen
                    self.__etag_feed(data)
                    self.req.wfile.write("{0:x}".format(datalen).encode("UTF-8"))
                    self.req.wfile.write(os.linesep.encode("UTF-8"))
                    if isinstance(data, str):
                        self.req.wfile.write(data.encode("UTF-8"))
                    elif isinstance(data, bytes):
                        self.req.wfile.write(data)
                    self.req.wfile.write(os.linesep.encode("UTF-8"))
            self.req.wfile.write(b"0")
            self.req.wfile.write(os.linesep.encode("UTF-8"))
            self.req.send_header(
                "Cache-Control",
                "public max-age={0}".format(self.req.server.maxagedynamic),
            )
            self.req.send_header("ETag", self.__etag_value())
            self.req.wfile.write(os.linesep.encode("UTF-8"))
            self.content = FLUSHED
        else:
            data = fp.read()
            self.req.send_header("ETag", self.etag(data))
            self.req.send_header("Content-Length", len(data))
            self.req.end_headers()
            self.req.wfile.write(data)
            self.content = FLUSHED

    def error(self, code, message=None):
        """Respond with HTTP status code for error."""
        self.req.send_error(code, message=message)
        self.content = FLUSHED

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
                self.headers["Cache-Control"] = "public max-age={0}".format(
                    self.req.server.maxagedynamic
                )

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
        """Build an ETag representation for the data associated with
        the given name."""
        self.__etag_init()
        self.__etag_feed(data)
        return self.__etag_value()

    def __etag_init(self):
        self.__etag = hashlib.md5()

    def __etag_feed(self, data):
        if isinstance(data, str):
            self.__etag.update(data.encode("UTF-8"))
        elif isinstance(data, bytes):
            self.__etag.update(data)
        else:
            self.__etag.update(str(data).encode("UTF-8"))

    def __etag_value(self):
        return self.__etag.hexdigest()

    def __getitem__(self, key):
        return self.headers[key]

    def __setitem__(self, key, value):
        self.headers[key] = value
