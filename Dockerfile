FROM ubuntu:14.04
MAINTAINER Stuti Agrawal <stutia@uchicago.edu>
USER root
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --force-yes \
    curl \
    g++ \
    make \
    python \
    libboost-dev \
    libboost-thread-dev \
    libboost-system-dev \
    zlib1g-dev \
    ncurses-dev \
    unzip \
    gzip \
    bzip2 \
    libxml2-dev \
    libxslt-dev \
    python-pip \
    python-dev \
    python-numpy \
    python-matplotlib \
    git \
    s3cmd \
    time \
    wget \
    python-virtualenv \
    default-jre \
    default-jdk \ 
    build-essential \ 
    cmake \
    libncurses-dev

RUN adduser --disabled-password --gecos '' ubuntu && adduser ubuntu sudo && echo "ubuntu    ALL=(ALL)   NOPASSWD:ALL" >> /etc/sudoers.d/ubuntu
ENV HOME /home/ubuntu

USER ubuntu
RUN mkdir ${HOME}/bin
WORKDIR ${HOME}/bin

#download VARSCAN
RUN wget http://downloads.sourceforge.net/project/varscan/VarScan.v2.3.9.jar && mv VarScan.v2.3.9.jar VarScan.jar

#download SAMTOOLS
RUN wget http://sourceforge.net/projects/samtools/files/samtools/1.1/samtools-1.1.tar.bz2 && tar xf samtools-1.1.tar.bz2 && mv samtools-1.1 samtools
WORKDIR ${HOME}/bin/samtools/
RUN make
WORKDIR ${HOME}

ENV PATH ${PATH}:${HOME}/bin/samtools/:${HOME}/bin/

RUN pip install s3cmd --user
WORKDIR ${HOME}
ADD varscan-tool ${HOME}/bin/varscan-tool/

ENV varscan 0.1

USER ubuntu
WORKDIR ${HOME}

