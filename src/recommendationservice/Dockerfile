FROM grpc/python:1.0

# show python logs as they occur
ENV PYTHONUNBUFFERED=0

# get packages
WORKDIR /recommendationservice
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# add files into working directory
COPY . .

# set listen port
ENV PORT "8080"
EXPOSE 8080

ENTRYPOINT ["python", "/home/recommendation_server.py"]
