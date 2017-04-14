#!/bin/bash

UID_VAL=$(stat -c '%u' /data)

if [ ! -d /data/spool ]; then
   mkdir /data/spool
fi

chown -R $UID_VAL /data/spool

exec uwsgi --ini /uwsgi.ini --uid $UID_VAL
