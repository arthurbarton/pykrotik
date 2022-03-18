FROM python:3.9-alpine
LABEL maintainer="Arthur Barton <Arthurb@igniferous.net>"
ENV LANG=C.UTF-8

WORKDIR /app
COPY app /app/
COPY crontab /etc/crontabs/root

RUN apk update && apk add tzdata gcc musl-dev libffi-dev && \ 
    cp /usr/share/zoneinfo/Australia/Sydney /etc/localtime && \
    echo "Australia/Sydney" > /etc/timezone && \
    apk del tzdata && rm -rf /var/cache/apk/* && \
    pip install --user -r requirements.txt

ENTRYPOINT [ "/usr/sbin/crond", "-f" ]