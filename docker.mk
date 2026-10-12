PLUGINNAME = dimensions_selector

SOURCES := $(shell (cd $(PLUGINNAME) && find . -name "*.py") )
FORMS = $(shell (cd $(PLUGINNAME) && find . -name "*.ui") )


default: help

.PHONY: help
help: ## Display this help message
	@echo "Usage: make <target>"
	@echo
	@echo "Possible targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "    %-20s%s\n", $$1, $$2}'

build: doc transcompile

doc: ## Generate documentation files
	make -C help html
	mkdir -p $(PLUGINNAME)/help/
	rsync -r \
		--exclude="_sources" \
		--exclude=".buildinfo" \
		--exclude=".buildinfo.bak" \
		help/build/html/ $(PLUGINNAME)/help/

.PHONY: check
check: ## Run all linters
check: black-check flake8 bandit detect-secrets

.PHONY: black
black:
	black $(PLUGINNAME) test

.PHONY: black-check
black-check:
	black --check $(PLUGINNAME) test

.PHONY: flake8
flake8:
	flake8 $(PLUGINNAME) test

.PHONY: bandit
bandit:
	bandit -r $(PLUGINNAME)

.PHONY: detect-secrets
detect-secrets:
	detect-secrets scan $(PLUGINNAME)

.PHONY: pytest
pytest:  ## Run tests using pytest
	pytest --cov --verbose --color=yes -vv ${PYTEST_ARGS}

.PHONY: coverage
coverage: ## Display coverage report
	coverage report -m

transup: ## Update translation catalogs
transup: $(PLUGINNAME)/i18n/fr.ts
	make -C help gettext

.INTERMEDIATE: $(PLUGINNAME)/$(PLUGINNAME).pro
.PHONY: $(PLUGINNAME)/$(PLUGINNAME).pro
$(PLUGINNAME)/$(PLUGINNAME).pro:
	echo "SOURCES = $(SOURCES)" > $@
	echo "FORMS = $(FORMS)" >> $@
	echo "TRANSLATIONS = i18n/fr.ts" >> $@
	echo "CODECFORTR = UTF-8" >> $@
	echo "CODECFORSRC = UTF-8" >> $@

.PHONY: $(PLUGINNAME)/i18n/fr.ts
$(PLUGINNAME)/i18n/fr.ts: $(PLUGINNAME)/$(PLUGINNAME).pro
	pylupdate5 -noobsolete $<

transcompile: ## Compile Qt .ts translation files into .qm binary format
	lrelease $(PLUGINNAME)/i18n/*.ts
