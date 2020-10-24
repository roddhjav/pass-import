DESTDIR ?= /

all:
	@python3 setup.py build
	@echo
	@echo "pass-import was built successfully. You can now install it wit \"make install\""
	@echo

install:
	@python3 setup.py install --root="$(DESTDIR)" --optimize=1 --skip-build
	@echo
	@echo "pass-import is installed succesfully"
	@echo

local:
	@python3 setup.py install --user --optimize=1
	@echo
	@echo "pass-import is localy installed succesfully."
	@echo "Remember to set PASSWORD_STORE_ENABLE_EXTENSIONS to 'true' for the extension to be enabled."

tests:
	@python3 -m green -vvv --run-coverage --termcolor --processes $(shell nproc)
	@coverage html

lint:
	@prospector --profile .prospector.yaml --strictness veryhigh \
		-t dodgy -t mccabe -t pep257 -t pep8 -t pylint \
		-t profile-validator -t pyflakes -t pyroma \
		pass_import/
	@prospector --profile .prospector.yaml --strictness veryhigh \
		-t dodgy -t mccabe -t pep257 -t pep8 -t pylint \
		-t profile-validator -t pyflakes -t pyroma \
		docs/updatedoc.py setup.py
	@prospector --profile tests/assets/prospector.yaml --strictness veryhigh \
		-t dodgy -t mccabe -t mypy -t pep257 -t pep8 -t pylint \
		-t profile-validator -t pyflakes -t pyroma \
		tests/

security:
	@bandit --ini .bandit -r pass_import tests setup.py docs/updatedoc.py

export PYTHONPATH = ./
docs:
	@python3 docs/updatedoc.py

clean:
	@rm -rf .coverage .mypy_cache .pybuild .ropeproject build config.json \
		debian/.debhelper debian/debhelper* debian/pass-extension-import* \
		dist *.egg-info htmlcov pass_import/**/__pycache__/ */__pycache__/ \
		__pycache__ session.baseline.sqlite session.sqlite \
		tests/assets/gnupg/random_seed tests/assets/test-results/ \
		tests/**/__pycache__/

.PHONY: install uninstall local tests lint security docs clean
