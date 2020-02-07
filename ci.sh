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

python setup.py sdist --formats=zip
python -m pip install dist/*.zip

# Actual tests
python -m pip install -r test-requirements.txt

mkdir empty
cd empty

INSTALLDIR=$(python -c "import os, trio; print(os.path.dirname(trio.__file__))")
cp ../setup.cfg $INSTALLDIR
if pytest -W error -r a --junitxml=../test-results.xml --run-slow ${INSTALLDIR} --cov="$INSTALLDIR" --cov-config=../.coveragerc --verbose; then
    PASSED=true
else
    PASSED=false
fi

# Remove the LSP again; again we want to do this ASAP to avoid
# accidentally breaking other stuff.
if [ "$LSP" != "" ]; then
    netsh winsock reset
fi

$PASSED
