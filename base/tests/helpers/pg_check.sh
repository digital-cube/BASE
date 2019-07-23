#!/usr/bin/env bash

if [ `PGPASSWORD=$1 psql -U$2 -t -c "select count(*) from pg_stat_activity where datname = '$3'"` != 0 ]
then
    echo 1 > /tmp/pgstat
else
    echo 0 > /tmp/pgstat
fi

