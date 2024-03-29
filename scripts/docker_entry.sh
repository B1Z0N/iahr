#!/usr/bin/env bash

# Send SIGTERM to all running processes on exit
trap "/bin/kill -s TERM -1" SIGTERM SIGQUIT

case "$1" in
    '' | 'exmpl')
        (cp .env exmpl && cd exmpl && python3 main.py)
    ;;
    'tests')
        (cp .env tests && python3 -m pytest ./tests)
    ;;
    *) exec "${@}" ;;
esac

