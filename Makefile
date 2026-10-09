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

PLUGINNAME = dimensions_selector

# QGIS version of the docker image, can be overriden by calling
# QGIS_VERSION=4.2 make <target> or in local.mk
QGIS_VERSION ?= 3.44

QGISDIR ?= .local/share/QGIS/QGIS3/profiles/default

export DOCKER_BUILDKIT=1

# Used by docker-compose.yaml to select the image tag
export QGIS_VERSION

DOCKER_RUN_CMD = docker compose run --rm --user `id -u` tester

-include local.mk

default: help

.PHONY: help
help: ## Display this help message
	@echo "Usage: make <target>"
	@echo
	@echo "Possible targets:"
	@grep -E -h '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "    %-20s%s\n", $$1, $$2}'

.PHONY: clean
clean: ## Delete generated files
	git clean -dfX

.PHONY: qgis
qgis: ## Run QGIS desktop
	docker compose run --rm --user `id -u`:`id -g` qgis

.PHONY: check
check: ## Run linters
	$(DOCKER_RUN_CMD) make -f docker.mk check

.PHONY: black
black: ## Run black formatter
	$(DOCKER_RUN_CMD) make -f docker.mk black

.PHONY: test
test: ## Run the automated tests suite
	$(DOCKER_RUN_CMD) make -f docker.mk pytest

.PHONY: bash
bash: ## Run bash in tests container
	$(DOCKER_RUN_CMD) bash

.PHONY: build
build: ## Build documentation and translations
build: docker-build
	$(DOCKER_RUN_CMD) make -f docker.mk build

.PHONY: docker-build
docker-build: ## Build docker images (QGIS_VERSION=<version> to select the QGIS version)
	docker build \
		--build-arg QGIS_VERSION=$(QGIS_VERSION) \
		--tag camptocamp/qgis-dimensions-selector:$(QGIS_VERSION) \
		./docker

.PHONY: transup
transup: ## Update translation catalogs
	$(DOCKER_RUN_CMD) make -f docker.mk transup

.PHONY: package
package: ## Create plugin archive
package: build
	mkdir -p dist
	rm -f dist/$(PLUGINNAME).zip
	zip dist/$(PLUGINNAME).zip -r $(PLUGINNAME) -x '*/__pycache__/*'
	echo "Created package: dist/$(PLUGINNAME).zip"

.PHONY: deploy
deploy: ## Deploy plugin to your QGIS plugin directory (to test zip archive)
deploy: package derase
	unzip dist/$(PLUGINNAME).zip -d $(HOME)/$(QGISDIR)/python/plugins/

.PHONY: derase
derase: ## Remove deployed plugin from your QGIS plugin directory
	rm -Rf $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)

.PHONY: link
link: ## Create symbolic link to this folder in your QGIS plugins folder (for development)
link: derase
	ln -s $(shell pwd)/$(PLUGINNAME) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
