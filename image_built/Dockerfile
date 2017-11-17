FROM fedora:26
MAINTAINER yujinyu

RUN dnf install -y  libaio-devel fio
RUN dnf install -y  sysbench
RUN dnf install -y wget make gcc
RUN wget  http://www.iozone.org/src/current/iozone3_471.tar
RUN tar -xvf iozone3_471.tar && cd iozone3_471/src/current && make linux-AMD64 && cp iozone /usr/bin/ && rm -rf iozone3_471*  && dnf clean all

