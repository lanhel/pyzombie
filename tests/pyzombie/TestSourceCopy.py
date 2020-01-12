#!/usr/bin/env /usr/local/bin/python3.1
# -*- coding: UTF-8 -*-
"""Source to be uploaded to a server that will copy what is on stdin
to stdout, and will produce associated diagnostic information on stderr."""
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
