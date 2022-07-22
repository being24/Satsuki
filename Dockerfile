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
    python -m pip install -U git+https://github.com/Rapptz/discord-ext-menus && \
    python -m pip install -U git+https://github.com/Rapptz/discord.py && \
    chmod 0700 ./Satsuki/*.sh && \
    chmod 0700 ./Satsuki/bot.py && \
    apk del build-base  && \
    rm -rf /var/cache/apk/*  && \
    echo "Hello, satsuki ready!"

CMD ["/opt/Satsuki/bot.sh"]