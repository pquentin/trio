#!/bin/bash

set -o errexit

python -m pip install coverage==5.0.3 pytest-cov==2.8.1 pytest==5.3.5
python t.py
pytest --cov=.
