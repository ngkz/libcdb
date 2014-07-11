#!/bin/bash
#Usage: libc-search.sh <address of __libc_start_main (hex)> <symbol to search>
#./libc-search.sh f75fa8a0 system
find "$(dirname $0)/libs" -type f | while read path; do
    LIBC_START_MAIN="$(nm -D "$path" | grep "${1:(-3)}" | grep __libc_start_main)"
    [ -z "$LIBC_START_MAIN" ] && continue
    echo "$path:"
    echo "$LIBC_START_MAIN"
    nm -D "$path" | grep "$2"
done
