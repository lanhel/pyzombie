#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Setuptools buildcmd package."""
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


def cmdclass():
    """Return dictionary suitable for setup ``cmdclass`` parameter."""
    from distutils.command.build import build as build_orig
    from .build_html import build_html, has_rest_docs

    commands = build_orig.sub_commands
    commands.append(("build_html", has_rest_docs))

    class build(build_orig):
        sub_commands = commands

    return {"build": build, "build_html": build_html}
