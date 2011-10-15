#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""test

Implements a Distutils 'test' command."""
__author__ = ('Lance Finn Helsten',)
__version__ = '1.0.1'
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
__all__ = ['test_unit', 'test_accept']

import sys
if sys.version_info < (3, 0):
    raise Exception("pytrader requires Python 3.0 or higher.")
import os
import shutil
import logging
import subprocess
import time
import unittest
from distutils.core import Command
from distutils.errors import DistutilsOptionError
from distutils.util import get_platform



class __TestCommand(Command):
    user_options = [
        ("suite=", "s", "Run specific test suite [default: all tests]."),
        ("debug=", "d", "Debug a specific test with preset breakpoints."),
        ("bSetup", None, "Add a breakpoint in setUp for debug."),
        ("bTeardown", None, "Add a breakpoint in tearDown for debug."),
    ]
    
    def initialize_options(self):
        self.suite = []
        self.debug = None
        self.bSetup = False
        self.bTeardown = False
    
    def finalize_options(self):
        sys.path[0] = os.path.abspath(self.test_src)
        if not os.path.isdir(self.testroot):
            os.makedirs(self.testroot)
        
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
            level=logging.NOTSET,
            filename=os.path.join(self.testroot, "logfile.txt"))
        
        for dirpath, dirnames, filenames in os.walk(self.test_src):
            if not dirpath.endswith('__pycache__'):
                sys.path.append(dirpath)
        
        if self.debug is None:
            for dirpath, dirnames, filenames in os.walk(self.test_src):
                tests = []
                for f in filenames:
                    f = os.path.splitext(f)[0]
                    for suffix in self.suffixes:
                        if f.endswith(suffix):
                            tests.append(f)
                            break
                self.suite.extend(tests)
            self.suite = unittest.TestLoader().loadTestsFromNames(self.suite)
        else:
            if re.match(r"^.+\.test[^.]+$", self.debug):
                module, self.method = self.debug.rsplit('.', 1)
            else:
                module = self.debug
                self.method = "runTest"
            module = module.replace('.', '/')
            module = os.path.join(self.test_src, module)
            module = module + '.py'
            while not os.path.isfile(module):
                module = os.path.dirname(module) + '.py'
            module = os.path.basename(module)
            module = os.path.splitext(module)[0]
            module = __import__(module)
            self.suite = unittest.TestLoader().loadTestsFromModule(module)
            self.case = self.__tests(self.suite)
            self.case = [c for c in self.case if str(c).startswith(self.method)]
            assert len(self.case) >= 1, "Debug cannot handle multiple cases."
            if not self.case:
                print("No test case chosen")
                sys.exit(1)
            self.case = self.case[0]
    
    def __tests(self, suite):
        ret = []
        for t in suite:
            if isinstance(t, unittest.TestSuite):
                ret.extend(self.__tests(t))
            else:
                ret.append(t)
        return ret
    
    def run(self):
        if self.debug is None:
            tr = unittest.TextTestRunner()
            tr.run(self.suite)
        else:
            import pdb
            db = pdb.Pdb()
            if self.bSetup:
                db.rcLines.append('b self.setUp')
            db.rcLines.append('b self.{0}'.format(self.method))
            if self.bTeardown:
                db.rcLines.append('b self.tearDown')
            db.rcLines.append('c')
            db.rcLines.append('l')
            db.runcall(self.case.debug)


class test_unit(__TestCommand):
    description = "Run all unit and integration tests on the system."
    
    def initialize_options(self):
        super().initialize_options()
        self.suffixes = ["Test", "TestCase"]
        self.test_src = os.path.abspath("./test")
        self.testroot = os.path.abspath('./build/test')
        self.config = "./test/etc/test.conf"


class test_accept(__TestCommand):
    description = "Run all acceptance tests on the system."

    def initialize_options(self):
        super().initialize_options()
        self.suffixes = ["Accept", "AcceptCase"]
        self.test_src = os.path.abspath("./test")
        self.testroot = os.path.abspath('./build/acceptance')
        self.config = "./test/etc/acceptance.conf"
    
    def run(self):
        with open(os.path.join(self.testroot, "initout.txt"), "w") as out:
            res = subprocess.check_output(
                    ['./build/scripts-3.2/fettlerctl.py', 'db_init'],
                    stderr=subprocess.STDOUT)
            res = str(res, encoding="UTF-8")
            out.write(res)
        out = open(os.path.join(self.testroot, "stdout.txt"), "w")
        err = open(os.path.join(self.testroot, "stderr.txt"), "w")
        with subprocess.Popen(['./build/scripts-3.2/fettlerd.py'], stdout=out, stderr=err) as proc:
            try:
                time.sleep(1.0)
                super().run()
                proc.terminate()
            except KeyboardInterrupt:
                print("User Termination")
                proc.kill()
            finally:
                print()


