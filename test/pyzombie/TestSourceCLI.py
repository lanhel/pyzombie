#!/usr/bin/env /usr/local/bin/python3.1
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""Source to be uploaded to a server that will test arguments, envionment,
stdin, stdout, and stderr for proper behavior."""
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
import json

NAME = "TestSourceCLI"
ENVIRON = {'env0':'abc', 'env1':'123'}
ARGV = ['-a', '-b', '--xyz']
STDIN = """My line1\nMyline2\n"""
STDERR = """Standard Error Test\n"""

def validateResults(utest, name, returncode, stdout, stderr):
    """Validate the results of executing this file.
    
    utest
        The unit test case that will handle asserts.
    stdout
        The file that contains the stdout produced by executing this file.
    stderr
        The file that contains the stderr produced by executing this file.
    """
    actualout = json.load(stdout)    
    utest.assertEquals(actualout['name'], NAME)
    for e in ENVIRON.keys():
        utest.assertEquals(actualout['environ'][e], ENVIRON[e])
    #utest.assertTrue(name in actualout['argv'][0])
    utest.assertEquals(actualout['argv'][1:], ARGV)
    utest.assertEquals("".join(actualout['stdin']), STDIN)
    
    utest.assertEquals(STDERR, stderr.read())
    
    
def dumpstdout(fp, env, argv, stdin):
    out = {}
    out['name'] = NAME
    out['environ'] = dict(env)
    out['argv'] = argv
    out['stdin'] = stdin.readlines()
    json.dump(out, fp)


def restful_yaml():
    pass

def restful_json():
    """Return a byte string that can be sent directly to a pyzombie server when
    executing this test program."""
    out = {}
    out['environment'] = ENVIRON
    out['arguments'] = ARGV
    return json.dumps(out).encode("UTF-8")


if __name__ == "__main__":
    dumpstdout(sys.stdout, os.environ, sys.argv, sys.stdin)
    print(STDERR, end="", file=sys.stderr)

