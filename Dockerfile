FROM python:3.10-alpine

ARG BOT_NAME="satsuki"

WORKDIR /opt/

ENV LC_CTYPE='C.UTF-8'
ENV TZ='Asia/Tokyo'
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./ ${BOT_NAME}

RUN set -x && \
    apk add --no-cache build-base nano git tzdata ncdu libstdc++ && \
    cp /usr/share/zoneinfo/Asia/Tokyo /etc/localtime && \ls
    python3 -m pip install -U setuptools && \
    python3 -m pip install -r ./${BOT_NAME}/requirements.txt && \
    chmod 0700 ./${BOT_NAME}/bot.py && \
    apk del build-base  && \
    rm -rf /var/cache/apk/*  && \
    echo "Hello, ${BOT_NAME} ready!"

CMD ["/opt/Satsuki/bot.py"]