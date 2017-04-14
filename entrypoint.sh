#!/bin/bash

cd /app

if [ ! -d spool ]; then
   mkdir spool
fi

exec uwsgi --ini ./uwsgi.ini
