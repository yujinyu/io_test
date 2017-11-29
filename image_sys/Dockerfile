FROM iotest:allinone
MAINTAINER yujinyu
WORKDIR /test/
RUN sysbench --test=fileio --file-test-mode=seqrd --file-io-mode=sync --file-extra-flags=direct --file-block-size=4k --file-total-size=2G prepare