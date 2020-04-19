#!/bin/sh

if [ -z "$1" ] || [ "$1" = "--help" ]; then
    printf "You should pass the filename to transform bash script to dot env file\n"
    exit
fi

sed -r '/^\s*$/d' "$1" | sed '/^#/ d' | sed -e 's/^export //'

