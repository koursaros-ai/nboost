# ## ### ###### hello ## there
FROM tensorflow/tensorflow:1.15.0-gpu-py3

LABEL maintainer="colethienes@gmail.com"

RUN apt-get update && apt-get install -y git
RUN pip install --upgrade pip
RUN echo 5
RUN pip install git+https://github.com/koursaros-ai/nboost.git#egg=project[tf] --no-cache-dir --compile


