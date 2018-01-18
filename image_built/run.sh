#!/usr/bin/env bash

fio -filename=/test/file -rw=$1 -bs=$2 -size=32G -runtime=180 -thread -name=mytest > /mnt/$3