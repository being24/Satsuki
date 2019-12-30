FROM ubuntu:18.04

WORKDIR /opt/

RUN set -x && \
    apt-get update && \
    apt-get install -y --no-install-recommends python3.7 python3-pip nano git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    git clone https://github.com/being24/Tachibana.git && \
    pip3 install -r ./Tachibana/docker_setting/requirements.txt

CMD [ "export LC_CTYPE='C.UTF-8'" ]


# docker run -it ubuntu:latest /bin/bash
