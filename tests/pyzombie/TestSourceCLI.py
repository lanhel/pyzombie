#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Source to be uploaded to a server that will test arguments, envionment,
stdin, stdout, and stderr for proper behavior."""
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

import sys
import os
import io
import json

NAME = "TestSourceCLI"
ENVIRON = {"env0": "abc", "env1": "123"}
ARGV = ["-a", "-b", "--xyz"]
STDIN = """My line1\nMyline2\n"""
STDERR = """Standard Error Test\n"""


def validateResults(utest, name, returncode, stdout, stderr):
    """Validate the results of executing this file.

    :param utest: The unit test case that will handle asserts.
    :param returncode: The return code produced by this file.
    :param stdout: The file that contains the stdout produced by executing this file.
    :param stderr: The file that contains the stderr produced by executing this file.
    """
    try:
        actualout = json.load(stdout)
    except json.decoder.JSONDecodeError as err:
        print(stderr.read())
        raise err
    utest.assertEqual(actualout["name"], NAME)
    for e in ENVIRON.keys():
        utest.assertEqual(actualout["environ"][e], ENVIRON[e])
    # utest.assertTrue(name in actualout['argv'][0])
    utest.assertEqual(actualout["argv"][1:], ARGV)
    utest.assertEqual("".join(actualout["stdin"]), STDIN)

    utest.assertEqual(STDERR, stderr.read())


def dumpstdout(fp, env, argv, stdin):
    out = {}
    out["name"] = NAME
    out["environ"] = dict(env)
    out["argv"] = argv
    out["stdin"] = stdin.readlines()
    json.dump(out, fp)


def restful_yaml():
    pass


def restful_json():
    """Return a byte string that can be sent directly to a pyzombie server when
    executing this test program."""
    out = {}
    out["environment"] = ENVIRON
    out["arguments"] = ARGV
    return json.dumps(out).encode("UTF-8")


if __name__ == "__main__":
    dumpstdout(sys.stdout, os.environ, sys.argv, sys.stdin)
    print(STDERR, end="", file=sys.stderr)
