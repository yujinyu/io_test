#!/usr/bin/env bash

fio -filename=/test/file -rw=$1 -direct=1 -bs=$2 -size=32G -runtime=60 -thread -name=mytest > /mnt/$3