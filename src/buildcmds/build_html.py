#!/usr/bin/env python # -*- coding: UTF-8 -*-
"""Setuptools build HTML documents command."""
__author__ = ("Lance Finn Helsten",)
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
__all__ = ["has_html_source", "BuildHtml"]

import sys
import os
import errno
import itertools
import glob
import subprocess
import setuptools


def has_html_source(self):
    """Check if source docs for build_html present."""
    dist = self.distribution
    src_root = os.path.abspath(dist.package_dir.get("", "."))
    paths = doc_paths(src_root, dist.package_data)
    try:
        next(paths)
        return True
    except StopIteration:
        return False


def doc_paths(src_root, package_data):
    """Return an iterator of relative paths over ``package_data``
        in ``src_root`` that are reStructuredText.
    """
    globpat = [
        [os.path.join(pk, g) for g in pv if g.endswith(".rst")]
        for pk, pv in package_data.items()
    ]
    globpat = itertools.chain(*globpat)
    globpat = (os.path.join(src_root, d) for d in globpat)
    files = (glob.iglob(d, recursive=True) for d in globpat)
    for file in itertools.chain(*files):
        file = os.path.relpath(file, src_root)
        yield file


class BuildHtml(setuptools.Command):
    """Setuptools command to build HTML documents.

    Source documents must be reStructuredText.
    """

    # pylint: disable=attribute-defined-outside-init

    description = "Build HTML documentation."
    user_options = [
        ("build-base=", "b", "base directory for build library"),
        ("build-lib=", None, "build directory for all distribution"),
        ("force", "f", "Build documentation ignoring timestamps."),
    ]

    def initialize_options(self):
        """Default values for user options."""
        self.build_base = "build"
        self.build_lib = None
        self.force = False

    def finalize_options(self):
        """Set final values of user options."""
        if self.build_lib is None:
            self.build_lib = os.path.join(self.build_base, "lib")

    def run(self):
        """Build HTML documents from supported source files."""
        args = [
            "rst2html.py",
            "--stylesheet",
            "help.css",
            "--link-stylesheet",
            "--traceback",
            "SRC_PATH_ARG_2",
            "DST_PATH_ARG_3",
        ]

        # Process the reStructuredText files.
        try:
            src_root = os.path.abspath(self.distribution.package_dir.get("", "."))

            for fname in doc_paths(src_root, self.distribution.package_data):
                src = os.path.join(src_root, fname)
                dst = os.path.abspath(
                    os.path.join(self.build_lib, os.path.splitext(fname)[0] + ".html")
                )
                if not os.path.isdir(os.path.dirname(dst)):
                    os.makedirs(os.path.dirname(dst))
                if (
                    self.force
                    or not os.path.isfile(dst)
                    or os.path.getmtime(src) > os.path.getmtime(dst)
                ):
                    print("Docutils", fname)
                    args[-2] = os.path.abspath(src)
                    args[-1] = os.path.abspath(dst)
                    ret = subprocess.call(args)
        except OSError as err:
            if err.errno == errno.ENOENT:
                print("error: Docutils missing.", file=sys.stderr)
            raise err
