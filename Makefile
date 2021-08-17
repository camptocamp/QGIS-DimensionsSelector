#/***************************************************************************
# DimensionsSelector
#
# Dimensions Selector Plugin
#							 -------------------
#		begin				: 2018-07-05
#		git sha				: $Format:%H$
#		copyright			: (C) 2018 by Camptocamp
#		email				: info@camptocamp.com
# ***************************************************************************/
#
#/***************************************************************************
# *																		 *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or	 *
# *   (at your option) any later version.								   *
# *																		 *
# ***************************************************************************/

#################################################
# Edit the following to match your sources lists
#################################################


#Add iso code for any locales you want to support here (space separated)
# default is no locales
# LOCALES = af
LOCALES = fr

# translation

PLUGINNAME = dimensions_selector

EXTRAS = metadata.txt icon.png

EXTRA_DIRS =

PYTHON_FILES = $(shell find $(PLUGINNAME) -name *.py)
COMPILED_RESOURCE_FILES = $(PLUGINNAME)/resources.py

PEP8EXCLUDE=pydev,resources.py,conf.py,third_party,ui


#################################################
# Normally you would not need to edit below here
#################################################

HELP = help/build/html

PLUGIN_UPLOAD = ./plugin_upload.py

RESOURCE_SRC=$(shell grep '^ *<file' resources.qrc | sed 's@</file>@@g;s/.*>//g' | tr '\n' ' ')

QGISDIR=.local/share/QGIS/QGIS3/profiles/default

default: compile

compile: $(COMPILED_RESOURCE_FILES) doc

%.py : %.qrc $(RESOURCES_SRC)
	pyrcc5 -o $*.py  $<

%.qm : %.ts
	$(LRELEASE) $<

link: derase
	ln -s $(shell pwd)/$(PLUGINNAME) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)

test: compile transcompile .build/requirements-dev.timestamp
	@echo
	@echo "----------------------"
	@echo "Regression Test Suite"
	@echo "----------------------"

	@# Preceding dash means that make will continue in case of errors
	
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); \
		export QGIS_DEBUG=0; \
		export QGIS_LOG_FILE=/dev/null; \
		.build/venv/bin/nosetests -v --with-id --with-coverage --cover-erase \
			--cover-package=$(PLUGINNAME) \
			./test \
			3>&1 1>&2 2>&3 3>&- || true
	@echo "----------------------"
	@echo "If you get a 'no module named qgis.core error, try sourcing"
	@echo "the helper script we have provided first then run make test."
	@echo "e.g. source run-env-linux.sh <path to qgis install>; make test"
	@echo "----------------------"

deploy: package derase
	@echo
	@echo "------------------------------------------------"
	@echo "Deploying plugin to your QGIS profile directory."
	@echo "------------------------------------------------"
	# The deploy  target only works on unix like operating system where
	# the Python plugin directory is located at:
	# $$HOME/$(QGISDIR)/python/plugins
	unzip dist/$(PLUGINNAME).zip -d $(HOME)/$(QGISDIR)/python/plugins/

derase:
	@echo
	@echo "-------------------------"
	@echo "Removing deployed plugin."
	@echo "-------------------------"
	rm -Rf $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)

package: compile
	@echo
	@echo "------------------------------------"
	@echo "Exporting plugin to zip package.	"
	@echo "------------------------------------"
	mkdir -p dist
	rm -f $(PLUGINNAME).zip
	git archive -o dist/$(PLUGINNAME).zip HEAD $(PLUGINNAME)
	zip -g dist/$(PLUGINNAME).zip $(PLUGINNAME)/resources.py
	zip -gr dist/$(PLUGINNAME).zip $(PLUGINNAME)/help
	echo "Created package: $(PLUGINNAME).zip"

transup:
	@echo
	@echo "------------------------------------------------"
	@echo "Updating translation files with any new strings."
	@echo "------------------------------------------------"
	pylupdate4 -noobsolete $(PYTHON_FILES) -ts $(PLUGINNAME)/i18n/fr.ts
	make -C help gettext

transcompile:
	@echo
	@echo "----------------------------------------"
	@echo "Compiled translation files to .qm files."
	@echo "----------------------------------------"
	lrelease $(PLUGINNAME)/i18n/fr.ts

transclean:
	@echo
	@echo "------------------------------------"
	@echo "Removing compiled translation files."
	@echo "------------------------------------"
	rm -f $(PLUGINNAME)/i18n/*.qm

clean: transclean
	@echo
	@echo "------------------------------------"
	@echo "Removing uic and rcc generated files"
	@echo "------------------------------------"
	rm $(COMPILED_RESOURCE_FILES)
	rm -rf $(PLUGINNAME)/help

cleanall: clean
	rm -rf .build

doc: .build/requirements-dev.timestamp
	@echo
	@echo "------------------------------------"
	@echo "Building documentation using sphinx."
	@echo "------------------------------------"
	make -C help html
	cp -r help/build/html/* $(PLUGINNAME)/help/

check: flake8

pylint:
	@echo
	@echo "-----------------"
	@echo "Pylint violations"
	@echo "-----------------"
	@pylint --reports=n --rcfile=pylintrc . core gui test || true
	@echo
	@echo "----------------------"
	@echo "If you get a 'no module named qgis.core' error, try sourcing"
	@echo "the helper script we have provided first then run make pylint."
	@echo "e.g. source run-env-linux.sh <path to qgis install>; make pylint"
	@echo "----------------------"


# Run pep8 style checking
#http://pypi.python.org/pypi/pep8
pep8:
	@echo
	@echo "-----------"
	@echo "PEP8 issues"
	@echo "-----------"
	@pep8 --repeat --ignore=E203,E121,E122,E123,E124,E125,E126,E127,E128 --exclude $(PEP8EXCLUDE) --max-line-length=110 . || true
	@echo "-----------"
	@echo "Ignored in PEP8 check:"
	@echo $(PEP8EXCLUDE)

flake8: .build/requirements-dev.timestamp
	.build/venv/bin/flake8

.build/venv.timestamp:
	python3 -m venv --system-site-packages .build/venv
	touch $@

.build/requirements-dev.timestamp: .build/venv.timestamp requirements-dev.txt
	.build/venv/bin/pip install -r requirements-dev.txt
	touch $@
