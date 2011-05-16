#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#----------------------------------------------------------------------------
"""pyzombie project setup."""
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

import sys
if sys.version_info < (3, 0):
    raise Exception("fettler requires Python 3.0 or higher.")
sys.path.append("./setup/lib")
import locale
from distutils.core import setup
from distutils.command.build import build
from distutils_local import *

locale.setlocale(locale.LC_ALL, '')

build.sub_commands.append(('build_docutils', build_docutils.has_docs))

setup(
    name='pyzombie',
    version=__version__,
    author='Lance Finn Helsten',
    author_email='lanhel@me.com',
	#maintainer='',
    #maintainer_email='',
    url='http://code.google.com/p/pyzombie/',
    #url='http://www.flyingtitans.com/products/pyzombie',
    description='Remote code execution server.',
    long_description=open('README.txt').read(),
    platforms=['OS Independent'],
    download_url='http://code.google.com/p/pyzombie/downloads/list',
    license="GNU Affero General Public License",    
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: GNU Affero General Public License v3',
		'Operating System :: OS Independent',
		'Topic :: Software Development :: Quality Assurance',
		'Topic :: Software Development :: Testing',
		'Topic :: Software Development :: Testing :: Traffic Generation',
		'Topic :: Utilities'
    ],
    scripts=['pyzombied.py'],
    packages=['pyzombie', 'pyzombie/handlers'],
    #package_dir={'' : 'src'},
    package_data = {'pyzombie': ['httpfiles/*', 'httphelp/*.css']},
    #data_files=[],
    requires=[],
    cmdclass={
        "build_docutils":build_docutils,
        "test":test_unit,
        "accept":test_accept,
        "deploy":deploy
    }
)


