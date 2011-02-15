#!/usr/bin/env /usr/local/bin/python3.1
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""Source to be uploaded to a server that will copy what is on stdin to stdout,
and will produce associated diagnostic information on stderr."""
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
import os
import io

def validateResults(utest, name, returncode, stdout, stderr):
    pass

if __name__ == "__main__":
    count = 0
    line = sys.stdin.readline()
    while line:
        count = count + 1
        sys.stdout.write(line)
        sys.stderr.write("{0}: {1}\n".format(count, line[:10]))
        line = sys.stdin.readline()

