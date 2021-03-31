FROM python:3.8.5-buster

WORKDIR /opt/

ENV LC_CTYPE='C.UTF-8'
ENV TZ='Asia/Tokyo'
ENV DEBIAN_FRONTEND=noninteractive

RUN set -x && \
    apt-get update && \
    apt-get install -y --no-install-recommends python3-pip nano git tzdata&& \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    cp /usr/share/zoneinfo/Asia/Tokyo /etc/localtime && \
    pip3 install -U setuptools && \
    git clone https://github.com/being24/Satsuki.git && \
    pip3 install -r ./Satsuki/docker_setting/requirements.txt && \
    python -m pip install -U git+https://github.com/Rapptz/discord-ext-menus && \
    chmod 0755 ./Satsuki/*.sh && \
    chmod 0700 ./Satsuki/bot.py && \
    sh ./Satsuki/ayame.sh && \
    echo "Hello, Satsuki ready! @2020/07/27"

CMD ["/opt/Satsuki/bot.sh"]