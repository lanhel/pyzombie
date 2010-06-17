#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#$Id: setup.py 902 2009-10-16 16:38:28Z lance $
#-------------------------------------------------------------------------------
"""Executable object."""
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

__all__ = ['Executable']

import sys
import os
from datetime import datetime
import mimetypes
import weakref
from .ZombieConfig import config, datadir


class Executable:
    """This represents a single executable within the system.
    
    Factory Properties
    ------------------
    datadir
        The data directory that holds executables persistent information.
    execbase
        The base name for all executable directories.
    binaryname
        The base name for an executable's binary image.
    """
    
    @classmethod
    def createname(cls):
        """Create a unique RESTful name for a new executable."""
        name = config.get("pyzombie_filesystem", "execbase")
        name = "{0}_{1}".format(name, datetime.utcnow().strftime("%Y%jT%H%M%SZ"))
        return name
    
    __cache = {}
    
    @classmethod
    def getcached(cls, name, mediatype=None):
        """Get a cached executable by name. This will create a new executable
        if necessary."""
        if name not in cls.__cache:
            cls.__cache[name] = Executable(name, mediatype)
        return cls.__cache[name]
    
    def __init__(self, name, mediatype=None):
        """
        Parameters
        ----------
        name
            Name of the executable directory.
        mediatype
            The media type for the binary. If none given then the mediatype
            will default to application/octet-stream.
        """
        self.__name = name
        self.__edir = os.path.normpath(os.path.join(self.datadir, name))
        self.__bin = os.path.normpath(os.path.join(self.__edir, self.binaryname))
        if os.path.isdir(self.__edir):
            fnames = [f for f in os.listdir(self.__edir) if f.startswith(self.binaryname)]
            if fnames:
                self.__bin = self.__bin + os.path.splitext(fnames[0])[1]
        else:
            os.makedirs(self.__edir)
            if not mediatype:
                mediatype = "application/octet-stream"
            self.__bin = self.__bin + mimetypes.guess_extension(mediatype)
        self.__mediatype = mimetypes.guess_type(self.__bin)
    
    @property
    def datadir(cls):
        return datadir()
    
    @property
    def execbase(cls):
        return config.get("pyzombie_filesystem", "execbase")
    
    @property
    def binaryname(cls):
        return config.get("pyzombie_filesystem", "binary")

    @property
    def name(self):
        """This is the RESTful name of the executable."""
        return self.__name
    
    @property
    def dirpath(self):
        """This is the path to the executable directory."""
        return self.__edir
    
    @property
    def binpath(self):
        """This is the path to the executable file."""
        return self.__bin
    
    @property
    def mediatype(self):
        """This is the internet media type of the executable."""
        return self.__mediatype
    
    def readimage(self, fp):
        """Read te image from the persistant store into the file object."""
        pass
    
    def writeimage(self, fp):
        """Write the image from the file object to the persistant store."""
        execfile = open(self.binpath, "w")
        databuf = fp.read(4096)
        while databuf:
            execfile.write(databuf)
            databuf = fp.read(4096)
        execfile.flush()
        execfile.close()
    
    def run(self):
        """Increment the executable running count."""
        pass
        
    def isrunning(self, edir):
        return False
