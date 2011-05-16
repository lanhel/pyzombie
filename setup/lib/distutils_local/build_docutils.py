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
__all__ = ['build_docutils']

import sys
if sys.version_info < (3, 0):
    raise Exception("pytrader requires Python 3.0 or higher.")
import os
import itertools
import subprocess
from distutils.core import Command

def doc_paths(packages):
    """Given a list of package names find all the reStructured text files
    with a '.rst' extension."""
    dirs = [p.replace('.', os.sep) for p in packages]
    dirs = [os.path.abspath(p) for p in dirs]
    files = [[os.path.join(p, f) for f in os.listdir(p)] for p in dirs]
    files = [f for f in itertools.chain(*files) if os.path.splitext(f)[1] == '.rst']
    files = [os.path.relpath(f) for f in files]
    return files

class build_docutils(Command):
    description = "Build documentation with Docutils."
    user_options = [
        ('build-base=', 'b', "base directory for build library"),
        ('build-lib=', None, "build directory for all distribution"),
        ('force', 'f', 'Build documentation ignoring timestamps.')
    ]
        
    def has_docs(self):
        return len(doc_paths(self.distribution.packages)) > 0

    def initialize_options(self):
        self.build_base = 'build'
        self.build_lib = None
        self.force = False

    def finalize_options(self):
        if self.build_lib is None:
            self.build_lib = os.path.join(self.build_base, 'lib')
    
    def run(self):
        env = dict(os.environ)
        env["PATH"] = os.path.abspath("setup/bin") + os.pathsep \
                + env["PATH"]
        env["PYTHONPATH"] = os.path.abspath("setup/lib/python") \
                + os.pathsep + env["PYTHONPATH"]
        args = [sys.executable,
                os.path.abspath("setup/bin/rst2html.py"),
                "SRC_PATH_ARG_2",
                "DST_PATH_ARG_3",
                "--stylesheet", "help.css",
                "--link-stylesheet",
                "--traceback"]

        for f in doc_paths(self.distribution.packages):
            src = os.path.abspath(f)
            dst = os.path.abspath(
                os.path.join(self.build_lib, os.path.splitext(f)[0] + ".html"))
            if self.force or os.path.getmtime(src) > os.path.getmtime(dst):
                print("Docutils", f)
                args[2] = os.path.abspath(src)
                args[3] = os.path.abspath(dst)
                subprocess.call(args, env=env)



