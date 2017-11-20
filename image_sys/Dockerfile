FROM iotest:allinone
MAINTAINER yujinyu
WORKDIR /test/
RUN sysbench --test=fileio --file-test-mode=read --file-io-mode=sync --file-extra-flags=direct --file-block-size=4k --file-total-size=4G prepare