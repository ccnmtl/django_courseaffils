PY_DIRS=courseaffils
VE ?= ./ve
REQUIREMENTS ?= test_reqs.txt
SYS_PYTHON ?= python3
PY_SENTINAL ?= $(VE)/sentinal
WHEEL_VERSION ?= 0.37.1
PIP_VERSION ?= 22.3
MAX_COMPLEXITY ?= 12
PY_DIRS ?= $(APP)
DJANGO ?= "Django==4.2.3"

FLAKE8 ?= $(VE)/bin/flake8
PIP ?= $(VE)/bin/pip
COVERAGE ?=$(VE)/bin/coverage

all: flake8 coverage

clean:
	rm -rf $(VE)
	find . -name '*.pyc' -exec rm {} \;

$(PY_SENTINAL):
	rm -rf $(VE)
	$(SYS_PYTHON) -m venv $(VE)
	$(PIP) install pip==$(PIP_VERSION)
	$(PIP) install --upgrade setuptools
	$(PIP) install wheel==$(WHEEL_VERSION)
	$(PIP) install --no-deps --requirement $(REQUIREMENTS) --no-binary cryptography
	$(PIP) install "$(DJANGO)"
	touch $@

test: $(REQUIREMENTS) $(PY_SENTINAL)
	./ve/bin/python runtests.py

flake8: $(PY_SENTINAL)
	$(FLAKE8) $(PY_DIRS) --max-complexity=$(MAX_COMPLEXITY) --exclude=*/migrations/*.py

coverage: $(PY_SENTINAL)
	$(COVERAGE) run --source=courseaffils runtests.py

.PHONY: flake8 test jshint jscs clean
