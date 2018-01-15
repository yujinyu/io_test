FROM 192.168.3.51:5000/admin/ubuntu:16.04
MAINTAINER yujinyu

WORKDIR /usr/src/kernels/
RUN apt install -y wget make gcc xz
RUN wget https://www.kernel.org/pub/linux/kernel/v4.x/linux-4.0.tar.xz
RUN xz -d linux-4.0.tar.xz &&tar -xvf linux-4.0.tar && rm -f linux-4.0.tar
WORKDIR /usr/src/kernels/linux-4.0/




