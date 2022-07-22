FROM python:3.8-alpine

WORKDIR /opt/

ENV LC_CTYPE='C.UTF-8'
ENV TZ='Asia/Tokyo'
ENV DEBIAN_FRONTEND=noninteractive

RUN set -x && \
    apk add --no-cache build-base nano git tzdata ncdu libstdc++ && \
    cp /usr/share/zoneinfo/Asia/Tokyo /etc/localtime && \
    python3 -m pip install -U setuptools && \
    git clone https://github.com/being24/Satsuki.git && \
    python3 -m pip install -r ./Satsuki/requirements.txt && \
    python -m pip install -U git+https://github.com/Rapptz/discord-ext-menus@fbb8803779373357e274e1540b368365fd9d8074 && \
    python -m pip install -U git+https://github.com/Rapptz/discord.py@45d498c1b76deaf3b394d17ccf56112fa691d160 && \
    chmod 0700 ./Satsuki/*.sh && \
    chmod 0700 ./Satsuki/bot.py && \
    apk del build-base  && \
    rm -rf /var/cache/apk/*  && \
    echo "Hello, satsuki ready!"

CMD ["/opt/Satsuki/bot.sh"]