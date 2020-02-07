#!/bin/bash

set -o errexit

python -c 'import platform; print(platform.mac_ver())'
python -m pip install coverage==5.0.3 pytest-cov==2.8.1 pytest==5.3.5
pytest --cov=.
