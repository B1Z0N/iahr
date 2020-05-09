#!/bin/bash

PYTHON=$(which python3)

source "../venv/bin/activate"
export PYTHONPATH="$(cd .. && pwd)"

$PYTHON -m pytest $@

