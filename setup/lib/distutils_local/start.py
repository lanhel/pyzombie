#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""test

Implements a Distutils 'test' command."""
__author__ = ('Lance Finn Helsten',)
__version__ = '1.0.1'
__copyright__ = """Copyright (C) 2011 Lance Finn Helsten"""
__license__ = """
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
__all__ = ['SystemStart']

import sys
if sys.version_info < (3, 0):
    raise Exception("pytrader requires Python 3.0 or higher.")
import os
import shutil
import logging
import subprocess
from distutils.core import Command

class SystemStart(Command):
    description = "Start the system."
    user_options = [
        ("debug", "d", "Start the system in Pdb."),
        ("port=", None, "IP Port for the system.")
    ]

    def initialize_options(self):
        self.debug = False
        self.port = None
        self.testroot = os.path.abspath('./build/start')

    def finalize_options(self):
        os.environ['FETTLERHOME'] = self.testroot
        if os.path.isdir(self.testroot):
            shutil.rmtree(self.testroot)
        os.makedirs(self.testroot, exist_ok=True)
        os.makedirs(os.path.join(self.testroot, 'etc'))
        os.makedirs(os.path.join(self.testroot, 'var'))
        os.makedirs(os.path.join(self.testroot, 'var', 'db'))
        os.makedirs(os.path.join(self.testroot, 'var', 'log'))
        os.makedirs(os.path.join(self.testroot, 'var', 'run'))
        os.makedirs(os.path.join(self.testroot, 'var', 'cache'))
        os.makedirs(os.path.join(self.testroot, 'var', 'spool'))        
        shutil.copyfile("./test/etc/start.conf", os.path.join(self.testroot, 'etc', 'fettler.conf'))

        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
            level=logging.NOTSET,
            filename=os.path.join(self.testroot, "logfile.txt"))
    
    def run(self):
        with open(os.path.join(self.testroot, "initout.txt"), "w") as out:
            res = subprocess.check_output(
                    ['./build/scripts-3.2/fettlerctl.py', 'db_init'],
                    stderr=subprocess.STDOUT)
            res = str(res, encoding="UTF-8")
            out.write(res)
        
        args = ['./build/scripts-3.2/fettlerd.py']
        if self.port is not None:
            args.append("--port")
            args.append(self.port)
        with subprocess.Popen(args, stdout=sys.stdout, stderr=sys.stderr) as proc:
            try:
                code = proc.wait()
            except KeyboardInterrupt:
                proc.terminate()
                print()
