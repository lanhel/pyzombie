#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Executable object."""
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
__all__ = ["Executable"]

import os
import io
import stat
import shutil
from datetime import datetime
import mimetypes
from .ZombieConfig import config, datadir


class Executable:
    """This represents a single executable within the system."""

    @classmethod
    def createname(cls):
        """Create a unique RESTful name for a new executable."""
        name = config.get("pyzombie_filesystem", "execbase")
        name = "{0}_{1}".format(name, datetime.utcnow().strftime("%Y%jT%H%M%SZ"))
        if os.path.isdir(Executable.execdirpath(name)):
            # Need to handle the rare case of duplicate resource names---this
            # will happen all the time in testing, but rarely in production.
            index = 0
            altname = "{0}_{1:03}".format(name, index)
            while os.path.isdir(Executable.execdirpath(altname)):
                index = index + 1
                altname = "{0}_{1:03}".format(name, index)
            name = altname
        return name

    @classmethod
    def execdirpath(cls, name):
        """Path to directories that holds all executables."""
        return os.path.normpath(os.path.join(datadir(), name))

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
        self.__edir = Executable.execdirpath(name)
        self.__bin = os.path.normpath(os.path.join(self.__edir, self.binaryname))
        if os.path.isdir(self.__edir):
            fnames = [
                f for f in os.listdir(self.__edir) if f.startswith(self.binaryname)
            ]
            if fnames:
                self.__bin = self.__bin + os.path.splitext(fnames[0])[1]
        else:
            os.makedirs(self.__edir)
            if not mediatype:
                mediatype = "application/octet-stream"
            self.__bin = self.__bin + mimetypes.guess_extension(mediatype)
        self.__mediatype = mimetypes.guess_type(self.__bin)
        self.instances = {}

    def __str__(self):
        return "<pyzombie.Executable {0}>".format(self.name)

    def readimage(self, fp):
        """Read te image from the persistant store into the file object."""
        execfile = open(self.binpath, "rb")
        databuf = execfile.read(4096)
        while databuf:
            if isinstance(fp, io.TextIOBase):
                databuf = str(databuf, encoding="utf-8")
            fp.write(databuf)
            databuf = fp.read(4096)
        fp.flush()
        execfile.close()

    def writeimage(self, fp):
        """Write the image from the file object to the persistant store."""
        execfile = open(self.binpath, "wb")
        databuf = fp.read(4096)
        while databuf:
            if isinstance(databuf, str):
                databuf = bytes(databuf, encoding="utf-8")
            execfile.write(databuf)
            databuf = fp.read(4096)
        execfile.flush()
        execfile.close()
        os.chmod(self.binpath, stat.S_IRWXU)

    def delete(self):
        """Terminate all instances then remove the executable."""
        for i in set(self.instances.values()):
            i.delete()
        shutil.rmtree(self.dirpath, True)

    @property
    def datadir(self):
        """data directory that holds executables persistent information."""
        return datadir()

    @property
    def execbase(self):
        """Base name for all executable directories."""
        return config.get("pyzombie_filesystem", "execbase")

    @property
    def binaryname(self):
        """Base name for executable's binary image."""
        return config.get("pyzombie_filesystem", "binary")

    @property
    def name(self):
        """RESTful name of the executable."""
        return self.__name

    @property
    def dirpath(self):
        """Path to the executable directory."""
        return self.__edir

    @property
    def binpath(self):
        """Path to the executable file."""
        return self.__bin

    @property
    def mediatype(self):
        """Internet media type of the executable."""
        return self.__mediatype
