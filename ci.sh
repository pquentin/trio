#!/bin/bash

set -ex -o pipefail

# Log some general info about the environment
env | sort

################################################################
# We have a Python environment!
################################################################

python -c "import sys, struct, ssl, sqlite3; print('#' * 70); print('python:', sys.version); print('version_info:', sys.version_info); print('bits:', struct.calcsize('P') * 8); print('openssl:', ssl.OPENSSL_VERSION, ssl.OPENSSL_VERSION_INFO); print('sqlite:', sqlite3.version, sqlite3.sqlite_version); print('#' * 70)"

python -m pip install -U pip setuptools wheel
python -m pip --version

# python setup.py sdist --formats=zip
# python -m pip install dist/*.zip

# Actual tests
python -m pip install coverage==5.0.3 pytest-cov==2.8.1 pytest==5.3.5

pytest -W error -r a repro --cov=repro --cov-config=.coveragerc --verbose
