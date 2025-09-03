# syntax=docker/dockerfile:1
FROM python:3.12.11-alpine3.22

RUN apk add --update --no-cache bash git openssh && \
    apk add --update --virtual .deps --no-cache gnupg
