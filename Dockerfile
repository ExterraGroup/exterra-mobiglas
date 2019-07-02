FROM python:3.6

# python envs
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# build rocksdb python
RUN apt-get update -y --fix-missing \
  && apt-get install -y \
    build-essential \
    curl \
    libgflags-dev \
    libsnappy-dev \
    zlib1g-dev \
    libbz2-dev \
    liblz4-dev

ENV LD_LIBRARY_PATH=/usr/local/lib \
  PORTABLE=1

RUN cd /tmp \
  && curl -sL rocksdb.tar.gz https://github.com/facebook/rocksdb/archive/v5.15.10.tar.gz > rocksdb.tar.gz \
  && tar fvxz rocksdb.tar.gz \
  && cd rocksdb-5.15.10 \
  && make shared_lib \
  && make install-shared

RUN apt-get remove -y \
  build-essential \
  curl \
  && rm -rf /tmp

# python dependencies
COPY requirements.txt /
RUN pip install -r ./requirements.txt --upgrade

# todo: fix
#RUN mkdir /opt/mobiglas /opt/mobiglas/rocksdb /opt/mobiglas/logs
#ENV ROCKSDB_PATH=/opt/mobiglas/rocksdb/mobiglas.db \
    PATH="$PATH:$ROCKSDB_PATH"

#CMD export PATH=$PATH


COPY . /mobiglas
COPY config-dev.json /mobiglas/config.json
WORKDIR /mobiglas

CMD ["python", "-m", "mobiglas"]