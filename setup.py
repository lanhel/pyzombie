#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#$Id: setup.py 902 2009-10-16 16:38:28Z lance $
#-------------------------------------------------------------------------------
"""pyzombie project setup."""
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

import sys
if sys.version_info < (3, 0):
    raise Exception("pyzombie requires Python 3.0 or higher.")
import os
import shutil
import logging
import subprocess
import re
import unittest
from distutils.core import setup
from distutils.core import Command
from distutils.command.build import build as _build

class build(_build):
    """This will overload the normal build command to allow automatic build
    of the documentation from reStructured files.
    """
    
    def run(self):
        super().run()
        for dirpath, dirnames, filenames in os.walk("pyzombie"):
            files = [os.path.splitext(f) for f in filenames]
            files = [f[0] for f in files if f[1] == ".rst"]
            for f in files:
                src = os.path.join(dirpath, f + ".rst")                
                dst = os.path.join(self.build_lib, dirpath, f + ".html")
                
                if (self.force
                or not os.path.isfile(dst)
                or os.path.getmtime(src) > os.path.getmtime(dst)):
                    print("translating", src)
                    args = ["rst2html.py", os.path.abspath(src), os.path.abspath(dst)]
                    subprocess.call(args)
    
        

class test(Command):
    description = "Run all unit and integration tests on the system."
    user_options = [
        ("suite=", "s", "Run specific test suite [default: all tests]."),
    ]
    
    def initialize_options(self):
        self.suite = []
        self.test_src = os.path.abspath("./test")
        self.test_dst = os.path.abspath("./build/test")
        if not os.path.isdir(self.test_dst):
            os.makedirs(self.test_dst)
        sys.path[0] = os.path.abspath(self.test_dst)
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
            level=logging.NOTSET,
            filename=os.path.abspath("./build/test/logfile.txt"))
    
    def finalize_options(self):
        if os.path.isdir(self.test_dst):
            shutil.rmtree(self.test_dst)
        shutil.copytree(self.test_src, self.test_dst)
        for dirpath, dirnames, filenames in os.walk(self.test_dst):            
            tests = [os.path.join(dirpath, f) for f in filenames
                    if f.endswith('Test.py') or f.endswith('TestCase.py')]
            tests = [os.path.abspath(f) for f in tests]
            tests = [f for f in tests if os.path.exists(f) and os.path.isfile(f)]
            tests = [os.path.split(f)[1] for f in tests]
            tests = [os.path.splitext(f)[0] for f in tests]
            self.suite.extend(tests)
            for d in [d for d in dirnames if d.startswith('.')]:
                dirnames.remove(d)
            sys.path.extend([os.path.join(dirpath, d) for d in dirnames])
        self.suite = unittest.TestLoader().loadTestsFromNames(self.suite)        
    
    def run(self):
        var = os.path.abspath('./build/var')
        if os.path.isdir(var):
            shutil.rmtree(var)
        tr = unittest.TextTestRunner()
        tr.run(self.suite)


class acceptance(Command):
    description = "Run acceptance tests against a server."
    user_options = [
            ("suite=", "s", "Run specific acceptance suite [default: all tests]."),
            ("host=", "h", "Server host IP address to test [default: localhost]."),
            ("port=", "p", "Server host IP Port to test [default: 8008].")
        ]
    test_src = './acceptance/pyzombie'
    
    def initialize_options(self):
        self.suite = []
        self.host = "localhost"
        self.port = "8008"
        self.src = os.path.abspath("./acceptance")
        self.dst = os.path.abspath("./build/acceptance")
    
    def finalize_options(self):
        pass
    
    def run(self):
        pass


class changeversion(Command):
    description = "Change first __version__ string in all python files where the version is in xx.yy.zz form."
    user_options = [
        ("newversion=", None, "New version for all package.")
    ]
    
    def initialize_options(self):
        self.oldversion = tuple(__version__.split('.'))
        self.newversion = None
        
    def finalize_options(self):
        self.newversion = tuple(self.newversion.split('.'))
        if len(self.newversion) < 2 or 3 < len(self.newversion):
            print("New version must be a xx.yy or xx.yy.zz format.")
            sys.exit(errno.EINVAL)
        if self.newversion < self.oldversion:
            print("New version must be greater than {{0}.{1}.{2}}.".format(self.oldversion))
            sys.exit(errno.EINVAL)

    def run(self):
        srcpat = re.compile(r"""__version__\s*=\s*['"](\d{1,2}\.\d{1,2}(\.\d{1,2})?)['"]\s*""", re.MULTILINE)
        if len(self.newversion) == 2:
            repl = """__version__ = '{0}.{1}'\n""".format(*self.newversion)
        else:
            repl = """__version__ = '{0}.{1}.{2}'\n""".format(*self.newversion)
        
        for dirpath, dirnames, filenames in os.walk(os.getcwd()):
            filenames = [f for f in filenames if os.path.splitext(f)[1] == '.py']
            for f in filenames:
                path = os.path.join(dirpath, f)
                file = open(path, mode='r')
                contents = file.read()
                file.close()
                match = srcpat.search(contents)
                if match and tuple(match.groups()[0].split('.')) == self.oldversion:
                    contents = srcpat.sub(repl, contents)
                    file = open(path, mode='w')
                    file.write(contents)
                    file.close()
                elif match:
                    print("Invalid version {0} in {1}.".format(match.groups()[0], path), file=sys.stderr)


class deploy(Command):
    description = "Place the distribution archive onto the distribution server."
    user_options = []

    def initialize_options(self):
        self.host = None
        self.path = None
        self.user = None
        
    def finalize_options(self):
        import getpass
        print("Transfer files to {0}:{1}".format(self.host, self.path))
        if self.user is None:
            self.user = getpass.getuser()
            user = input("Username ({}): ".format(self.user))
            if user:
                self.user = user

    def run(self):
        distdir = os.path.join(os.getcwd(), 'dist')
        args = ['/usr/bin/rsync', '-v']
        args.extend([os.path.abspath(os.path.join(distdir, f)) for f in os.listdir(distdir)])
        args.append('{0}@{1}:{2}'.format(self.user, self.host, self.path))
        pid = subprocess.Popen(args)
        pid.wait()

setup(
    name='pyzombie',
    version=__version__,
    author='Lance Finn Helsten',
    author_email='lanhel@me.com',
    url='http://www.flyingtitans.com/products/pyzombie',
    description='Remote code execution server.',
    #long_description=""" """,
    #download_url='',
    #classifiers=[],
    #platforms=[],
    license="GNU Public License",    
    scripts=['pyzombied.py'],
    packages=['pyzombie', 'pyzombie/handlers'],
    #package_dir={'' : 'src'},
    package_data = {'pyzombie': ['httpfiles/*', 'httphelp/*.css']},
    #data_files=[],
    requires=[],
    cmdclass={
            "build":build,
            "test":test,
            "deploy":deploy,
            "changeversion":changeversion
        },
    classifiers = [
        ]
)


