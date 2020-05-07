#!/bin/bash

if [ -z "$1" ]; then
    VENV_FOLDER="$(cd ../venv && pwd)"
    printf "Venv folder not specified, using %s\n" "$VENV_FOLDER"
else
    VENV_FOLDER="$1"
fi

PYTHON=$(which python3)

source "${VENV_FOLDER}/bin/activate"
export PYTHONPATH="$(cd .. && pwd)"

$PYTHON -m pytest

