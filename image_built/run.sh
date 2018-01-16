#!/usr/bin/env bash
cd /usr/src/linux-4.0/
(time make -j $1 > /dev/null) > /mnt/$2.log
