FROM python:3.6.2-alpine3.6

RUN apk add --no-cache \
        bash \
        build-base \
        curl \
        gcc \
        libffi-dev \
        linux-headers \
        openssl-dev

COPY requirements.txt /ifttt/requirements.txt
RUN pip install --no-cache-dir -r /ifttt/requirements.txt

COPY ifttt /ifttt
COPY actions/* /usr/bin

ONBUILD COPY actions/* /usr/bin/
ONBUILD RUN chmod a+x /usr/bin/*
ONBUILD COPY ifttt.yaml /ifttt/watches/config.yaml

ENV GOOGLE_APPLICATION_CREDENTIALS /run/service-asr.json
ONBUILD ARG GOOGLE_SERVICE_ASR
ONBUILD RUN echo ${GOOGLE_SERVICE_ASR} | base64 -d > ${GOOGLE_APPLICATION_CREDENTIALS}

CMD ["python", "-m", "ifttt"]
