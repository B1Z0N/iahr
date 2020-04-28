#!/bin/bash

if [ -z "$1" ]; then
    printf "Create venv and pass it's folder as the first arg\n"
    exit 1
fi

VENV_FOLDER="$(pwd)/${1}"
PYTHON=$(which python3)

source "${VENV_FOLDER}/bin/activate"
export PYTHONPATH="$(cd ../ && pwd)"
$PYTHON  main.py

