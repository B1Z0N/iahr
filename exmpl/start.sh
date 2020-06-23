#!/bin/bash

DIRECTORY=$(cd `dirname $0` && pwd)

export PYTHONPATH="$(cd $DIRECTORY && cd .. && pwd)"

python3 "$DIRECTORY"/main.py

