FROM python:3.7.4-alpine

LABEL maintainer="colethienes@gmail.com"

RUN pip install --upgrade pip
RUN pip install nboost
RUN apk add --no-cache g++

ENTRYPOINT ["nboost"]