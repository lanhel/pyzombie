# :Author: Lance Finn Helsten
# :Copyright: 2009 Lance Finn Helsten <lanhel@flyingtitans.com>
# :License:
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#
# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
VERSION       = $(shell cd .. && python -m setup --version)
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
AWSS3         ?= aws --profile=pyzombie-docs s3
SOURCEDIR     = source
BUILDDIR      = ../build/share/pyzombieclient
PUBLISHURL    = s3://pyzombie-docs/pyzombieclient/$(VERSION)

# Put it first so that "make" without argument is like "make help".
.PHONY: help
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)


.PHONY: publish
publish: docs
	$(AWSS3) sync "$(BUILDDIR)/html" $(PUBLISHURL)
ifeq ($(findstring +,$(VERSION)),)
	$(AWSS3) sync $(PUBLISHURL) s3://pyzombie-docs/pyzombieclient/latest
endif


.PHONY: docs
docs: apidoc
	@$(SPHINXBUILD) -M html $(SPHINXOPTS) "$(SOURCEDIR)" "$(BUILDDIR)"
	#@$(SPHINXBUILD) -M singlehtml $(SPHINXOPTS) "$(SOURCEDIR)" "$(BUILDDIR)"
	#@$(SPHINXBUILD) -M epub $(SPHINXOPTS) "$(SOURCEDIR)" "$(BUILDDIR)"
	#@$(SPHINXBUILD) -M latex $(SPHINXOPTS) "$(SOURCEDIR)" "$(BUILDDIR)"
	#@$(SPHINXBUILD) -M latexpdf $(SPHINXOPTS) "$(SOURCEDIR)" "$(BUILDDIR)"
	#@$(SPHINXBUILD) -M doctest $(SPHINXOPTS) "$(SOURCEDIR)" "$(BUILDDIR)"


.PHONY: apidoc
apidoc:
	sphinx-apidoc -o $(SOURCEDIR)/ ../src/pyzombie


.PHONY: man
man:
	@echo Update man pages
	@mkdir -p source/man/man1
	@python -c 'import pyzombie; print(pyzombie.__doc__)' | \
		sed '1,3d' | \
		rst2man.py > source/man/man1/pyzombie.1


# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
.PHONY: Makefile
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
