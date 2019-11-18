FROM pytorch/pytorch:1.1.0-cuda10.0-cudnn7.5-runtime

LABEL maintainer="colethienes@gmail.com"

RUN pip install pytorch-transformers --no-cache-dir --compile
RUN pip install git+https://github.com/koursaros-ai/nboost.git[torch] --no-cache-dir --compile


