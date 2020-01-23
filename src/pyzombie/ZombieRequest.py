#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""pyzombie HTTP RESTful server request handler."""
__author__ = ("Lance Finn Helsten",)
__copyright__ = """Copyright 2009 Flying Titans, Inc."""
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
__all__ = []

# pylint: disable=wildcard-import

import socket
import http.client
import http.server
from setuptools_scm import get_version
from .Handler import Handler
from .handlers import *


DISPATCH_TABLE = [
    Handler.initdispatch(r"""^\*$""", "OPTIONS,TRACE", "abc"),  # "Server",
    ### HandlerTeapot.dispatch()    See RFC 2324
    HandlerHelp.dispatch(),
    HandlerExecSet.dispatch(),
    HandlerExecAdd.dispatch(),
    HandlerExec.dispatch(),
    HandlerExecStart.dispatch(),
    HandlerInstanceSet.dispatch(),
    HandlerInstance.dispatch(),
    HandlerInstanceStdin.dispatch(),
    HandlerInstanceStdout.dispatch(),
    HandlerInstanceStderr.dispatch(),
    HandlerLeftovers.dispatch(),
]


class ZombieRequest(http.server.BaseHTTPRequestHandler):
    """Extension of HTTP request handler to dispatch on Zombie verbs.

    :param request: The request to process.
    :param client_address: Tuple of the form ``(host, port)`` referring to
        the client’s address.
    :param server: The RESTful HTTP server instance.
    """

    def __init__(self, request, client_address, server):
        self.protocol_version = "HTTP/1.1"
        self.server_version = "pyzombie/" + get_version()
        super().__init__(request, client_address, server)

    def resolvedispatch(self):
        """Resolve the path against resource patterns. If matched then return
        the dispatch object and the dictionary of recognized path parts."""
        for handler in DISPATCH_TABLE:
            parts = handler.match(self.path)
            if parts is not None:
                return (handler, parts)
        self.send_error(http.client.NOT_FOUND)
        self.end_headers()
        return (None, None)

    def dispatch(self, method):
        """Determine the handler for the particular resource pattern and
        dispatch to that handler.

        :param method: The HTTP method that started this call. The lower
            case string is the name of the method in the handler class
            that will be called.
        """
        handler, parts = self.resolvedispatch()
        if handler is not None:
            handler = handler(self, parts)
            if hasattr(handler, method.lower()):
                getattr(handler, method.lower())()
            else:
                self.send_error(
                    http.client.METHOD_NOT_ALLOWED,
                    "{0} not allowed on resource {1}".format(self.command, self.path),
                )
                self.end_headers()

    # pylint: disable=invalid-name

    def do_OPTIONS(self):
        """Dispatch handler for HTTP OPTIONS."""
        try:
            handler, _ = self.resolvedispatch()
            if handler is not None:
                self.send_response(http.client.OK)
                self.send_header(
                    "Server", "pyzombie/" + get_version(root=".", relative_to=__file__)
                )
                self.send_header("Allow", handler.allow)
                self.send_header("Location", handler.help)
                self.end_headers()
        except socket.error as err:
            self.log_error("Internal socket error %s.", err)

    def do_HEAD(self):
        """Dispatch handler for HTTP HEAD."""
        try:
            self.dispatch("HEAD")
        except socket.error as err:
            self.log_error("Internal socket error %s.", err)

    def do_GET(self):
        """Dispatch handler for HTTP GET."""
        try:
            self.dispatch("GET")
        except socket.error as err:
            self.log_error("Internal socket error %s.", err)

    def do_POST(self):
        """Dispatch handler for HTTP POST."""
        try:
            self.dispatch("POST")
        except socket.error as err:
            self.log_error("Internal socket error %s.", err)

    def do_PUT(self):
        """Dispatch handler for HTTP PUT."""
        try:
            self.dispatch("PUT")
        except socket.error as err:
            self.log_error("Internal socket error %s.", err)

    def do_DELETE(self):
        """Dispatch handler for HTTP DELETE."""
        try:
            self.dispatch("DELETE")
        except socket.error as err:
            self.log_error("Internal socket error %s.", err)
