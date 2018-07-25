# Use the grpc.io provided Python image as the base image
FROM grpc/python:1.0

# show python logs as they occur
ENV PYTHONUNBUFFERED=0

# install pip for python3
RUN apt-get -qqy update && \
        apt-get -qqy install python3-pip

# get packages
WORKDIR /email_server
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Add the application
COPY . .

EXPOSE 8080
ENTRYPOINT [ "python3", "email_server.py" ]
