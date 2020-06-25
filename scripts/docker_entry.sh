#!/usr/bin/env bash

# Send SIGTERM to all running processes on exit
trap "/bin/kill -s TERM -1" SIGTERM SIGQUIT

case "$1" in
    '' | 'exmpl')
        (cp .env exmpl && cd exmpl && ./start.sh)
    ;;
    'tests')
        (cp .env tests && cd tests && ./start.sh)
    ;;
    *) exec "${@}" ;;
esac

