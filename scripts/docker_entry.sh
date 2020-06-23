#!/usr/bin/env bash

# Send SIGTERM to all running processes on exit
trap "/bin/kill -s TERM -1" SIGTERM SIGQUIT

case "$1" in
    '' | 'exmpl')
        cd exmpl && ./start.sh
    ;;
    'tests')
        cd tests && ./start.sh
    ;;
    *) exec "${@}" ;;
esac

