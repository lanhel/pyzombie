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
__all__ = ['Deploy']

import sys
if sys.version_info < (3, 0):
    raise Exception("pytrader requires Python 3.0 or higher.")
import os
from distutils.core import Command
from distutils.errors import DistutilsOptionError
from distutils.util import get_platform

class Deploy(Command):
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
        args.append(os.path.abspath(os.path.join(os.getcwd(), 'HEADER.html')))
        args.append(os.path.abspath(os.path.join(os.getcwd(), 'FOOTER.html')))
        args.extend([os.path.abspath(os.path.join(distdir, f)) for f in os.listdir(distdir)])
        args.append('{0}@{1}:{2}'.format(self.user, self.host, self.path))
        pid = subprocess.Popen(args)
        pid.wait()


