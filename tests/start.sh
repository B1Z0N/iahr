#!/bin/bash

DIRECTORY=$(cd `dirname $0` && pwd)

export PYTHONPATH="$(cd $DIRECTORY && cd .. && pwd):$PYTHONPATH"

python3 -m pytest "$DIRECTORY" $@
