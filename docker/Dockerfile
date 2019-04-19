FROM python:2-alpine

ARG HTTP_PROXY=${HTTP_PROXY}
ARG HTTPS_PROXY=${HTTPS_PROXY}
ENV http_proxy $HTTP_PROXY
ENV https_proxy $HTTPS_PROXY
ADD . /service
WORKDIR /service

RUN sh /service/docker-env-conf.sh

EXPOSE 8806
USER onap
WORKDIR /service

ENTRYPOINT modeling/toscaparsers/genericparser/docker/docker-entrypoint.sh
