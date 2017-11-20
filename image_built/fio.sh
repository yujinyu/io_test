#!/usr/bin/env bash
# $1: -rw, [-buffered=1 -ioengine=]  or ]-direct=1 -ioengine= ]
# $2: -bs block-size
# $3: the file redirect the output to
touch /test/file
fio -filename=/test/file -rw=$1 -bs=$2 -size=32G -runtime=180 -thread -name=mytest > $3