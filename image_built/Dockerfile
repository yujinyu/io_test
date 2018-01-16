#FROM 192.168.3.51:5000/admin/ubuntu:16.04
FROM 192.168.3.51:5000/admin/test:cpu-bound
MAINTAINER yujinyu


#RUN apt-get update
#RUN apt-get install -y time
#WORKDIR /usr/src/
#RUN wget https://www.kernel.org/pub/linux/kernel/v4.x/linux-4.0.tar.xz
#RUN tar -xvf linux-4.0.tar.xz && rm -f linux-4.0.tar.xz

# WORKDIR /usr/src/linux-4.0/
COPY run.sh /
RUN chmod +x /run.sh





