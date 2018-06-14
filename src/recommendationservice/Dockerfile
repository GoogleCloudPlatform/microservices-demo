FROM python:3.5-jessie

RUN pip --no-cache-dir install \
        grpcio

# show python logs as they occur
ENV PYTHONUNBUFFERED=0

# add files into working directory
ADD recommendation.py /home
WORKDIR /home

ENTRYPOINT /usr/bin/python /home/recommendation.py
