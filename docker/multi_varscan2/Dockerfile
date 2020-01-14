FROM ubuntu:16.04
LABEL maintainer="sli6@uchicago.edu"
LABEL version="2.3.9"
LABEL description="Python wrapper of multithreading `VarScan.v2.3.9`"

RUN apt-get update -y \
    && apt-get install -y \
    openjdk-8-jre-headless \
    python-dev \
    wget \
    && apt-get clean

RUN cd /opt/ \
    && wget http://downloads.sourceforge.net/project/varscan/VarScan.v2.3.9.jar

ADD multi_varscan2.py /opt/
