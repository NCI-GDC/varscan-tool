FROM ubuntu:16.04

RUN apt-get update -y && \
    apt-get install -y \
    openjdk-8-jre-headless \
    python-pip python-dev wget

RUN cd /bin/ && wget http://downloads.sourceforge.net/project/varscan/VarScan.v2.3.9.jar
RUN wget https://github.com/broadinstitute/picard/releases/download/2.10.1/picard.jar \
    && mv picard.jar /usr/local/bin/ \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ADD multi_varscan2.py /bin/

ENV multi_varscan2 v1.4
