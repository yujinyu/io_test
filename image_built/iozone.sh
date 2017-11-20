#!/usr/bin/env bash
# $1: -i  x  -I  or  blank
    #  0=write/rewrite, 1=read/re-read, 2=random-read/write,  3=Read-backwards
    #  4=Re-write-record, 5=stride-read,  6=fwrite/re-fwrite,  7=fread/Re-fread
    #  8=random mix, 9=pwrite/Re-pwrite, 10=pread/Re-pread
    # 11=pwritev/Re-pwritev, 12=preadv/Re-preadv
# $2: -r,    blocksize
# $3: the file redirect the output to
iozone -a -i $1 -r $2  -s 32g -Rab $3.xls