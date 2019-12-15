FROM pytorch/pytorch:1.1.0-cuda10.0-cudnn7.5-runtime

LABEL maintainer="colethienes@gmail.com"

RUN pip install --upgrade pip
RUN pip install nboost[pt]

ENTRYPOINT ["nboost"]