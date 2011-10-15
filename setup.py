#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#----------------------------------------------------------------------------
"""pyzombie project setup."""
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
    license="Apache License, Version 2.0",    
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: Apache Software License',
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


