FROM ubuntu:16.04
LABEL maintainer="sli6@uchicago.edu"
LABEL version="1.5"
LABEL description="Python wrapper of multithreading `VarScan.v2.3.9`"

RUN apt update -y \
    && apt install -y \
    openjdk-8-jre-headless \
    software-properties-common \
    wget

RUN add-apt-repository ppa:deadsnakes/ppa \
    && apt update -y \
    && apt install python3.7 -y \
    && apt-get clean

RUN cd /opt/ \
    && wget http://downloads.sourceforge.net/project/varscan/VarScan.v2.3.9.jar

ADD multi_varscan2_p3.py /opt/
