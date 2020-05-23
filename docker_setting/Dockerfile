FROM ubuntu:18.04

WORKDIR /opt/

ENV LC_CTYPE='C.UTF-8'
ENV TZ='Asia/Tokyo'
ENV DEBIAN_FRONTEND=noninteractive

COPY token /opt

RUN set -x && \
    apt-get update && \
    apt-get install -y --no-install-recommends python3.7 python3-pip tzdata nano git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    cp /usr/share/zoneinfo/Asia/Tokyo /etc/localtime && \
    pip3 install -U setuptools && \
    git clone https://github.com/being24/Tachibana.git && \
    pip3 install -r ./Tachibana/docker_setting/requirements.txt && \
    chmod 0755 ./Tachibana/*.sh && \
    chmod 0700 ./Tachibana/bot.py && \
    sh ./Tachibana/ayame.sh && \
    mv /opt/token /opt/Tachibana && \
    echo "Hello, Tachibana ready!"

CMD ["/opt/Tachibana/bot.sh"]