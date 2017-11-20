#!/usr/bin/env bash
mkdir -p  /test && cd /test
sysbench --test=fileio --file-test-mode=$1 --file-block-size=$2 --file-total-size=32G  prepare
sysbench --test=fileio --file-test-mode=$1 --file-block-size=$2 --file-total-size=32G run > $3
sysbench --test=fileio --file-test-mode=$1 --file-block-size=$2 --file-total-size=32G clean
exit 0
