FROM ubuntu:18.04

WORKDIR /opt/

ENV LC_CTYPE='C.UTF-8'

COPY token /opt

RUN set -x && \
    apt-get update && \
    apt-get install -y --no-install-recommends python3.7 python3-pip nano git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install -U setuptools && \
    git clone https://github.com/being24/Tachibana.git && \
    pip3 install -r ./Tachibana/docker_setting/requirements.txt && \
    sh ./Tachibana/ayame.sh && \
    chmod 0700 ./Tachibana/*.sh && \
    mv /opt/token /opt/Tachibana && \
    echo "Hello, Tachibana ready!"

CMD ["/opt/Tachibana/bot.sh"]