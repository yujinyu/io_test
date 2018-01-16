#!/usr/bin/env bash
cd /usr/src/linux-4.0/
/usr/bin/time -f "time: %E" --output=/mnt/$2.log make -j$1 > /dev/null 2>&1
