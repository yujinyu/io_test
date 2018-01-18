FROM 192.168.3.51:5000/admin/fedora:26
MAINTAINER yujinyu

RUN dnf install -y libaio-devel fio && dnf clean all
COPY run.sh /
RUN chmod +x /run.sh
RUN mkdir -p /test && touch /test/file





