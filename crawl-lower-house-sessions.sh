#!/bin/bash
START_YEAR=$1
END_YEAR=${2:-2022}

years=$(seq $START_YEAR $END_YEAR)
source .venv/bin/activate
for year in $years
do
    python crawl-lower-house-sessions.py --year $year --log-level info --log-file crawl-$year.log
done
deactivate
