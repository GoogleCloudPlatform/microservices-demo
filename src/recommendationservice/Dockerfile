FROM grpc/python:1.0

# show python logs as they occur
ENV PYTHONUNBUFFERED=0

# add files into working directory
COPY . /home/
WORKDIR /home

# get packages
RUN apt-get update && apt-get install python3-pip -y
RUN pip install opencensus
RUN pip install google-python-cloud-debugger
RUN pip install google-cloud-trace

# set listen port
ENV PORT "8080"
EXPOSE 8080

ENTRYPOINT ["python", "/home/recommendation_server.py"]
