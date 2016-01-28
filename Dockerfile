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

RUN apt-get build-dep -y --force-yes python-psycopg2

RUN adduser --disabled-password --gecos '' ubuntu && adduser ubuntu sudo && echo "ubuntu    ALL=(ALL)   NOPASSWD:ALL" >> /etc/sudoers.d/ubuntu
ENV HOME /home/ubuntu

USER ubuntu
RUN mkdir ${HOME}/bin
WORKDIR ${HOME}/bin
ADD varscan-tool ${HOME}/bin/varscan-tool/
ADD setup.* ${HOME}/bin/varscan-tool/
ADD requirements.txt ${HOME}/bin/varscan-tool/

USER root
RUN chown -R ubuntu:ubuntu ${HOME}/bin/varscan-tool/
USER ubuntu

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

ENV varscan 0.1

RUN pip install --user virtualenvwrapper \
    && /bin/bash -c "source ${HOME}/.local/bin/virtualenvwrapper.sh \
    && mkvirtualenv --python=/usr/bin/python3 p3 \
    && echo source ${HOME}/.local/bin/virtualenvwrapper.sh >> ${HOME}/.bashrc \
    && echo source ${HOME}/.virtualenvs/p3/bin/activate >> ${HOME}/.bashrc \
    && source ~/.virtualenvs/p3/bin/activate \
    && cd ~/bin/varscan-tool \
    && pip install -r ./requirements.txt" 

USER ubuntu
WORKDIR ${HOME}

