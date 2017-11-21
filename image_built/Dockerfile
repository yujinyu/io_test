FROM fedora:26
MAINTAINER yujinyu

RUN dnf install -y libaio-devel fio
RUN dnf install -y sysbench
RUN dnf install -y wget make gcc
RUN wget http://www.iozone.org/src/current/iozone3_471.tar && tar -xvf iozone3_471.tar
RUN cd iozone3_471/src/current && make linux-AMD64 && cp iozone /usr/bin/
RUN rm iozone3_471* -rf && dnf clean all
COPY run /test/
RUN chmod +x /test/run
RUN mkdir -p /test && touch /test/file

