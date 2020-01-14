FROM quay.io/jeremiahsavage/cdis_base

MAINTAINER Shenglai Li <sli6@uchicago.edu>

USER root
RUN apt-get update && apt-get install -y --force-yes \
    openjdk-8-jre-headless \
    wget

USER ubuntu
ENV HOME /home/ubuntu
WORKDIR ${HOME}

ENV varscan2-tool v2.3

RUN wget http://downloads.sourceforge.net/project/varscan/VarScan.v2.3.9.jar
