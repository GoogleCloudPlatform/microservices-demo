FROM grpc/python:1.0

# show python logs as they occur
ENV PYTHONUNBUFFERED=0

# get packages
WORKDIR /recommendationservice
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install opencensus
RUN pip install google-cloud-trace
RUN pip install google-python-cloud-debugger

# add files into working directory
COPY . .

# set listen port
ENV PORT "8080"
EXPOSE 8080

ENTRYPOINT ["python", "/recommendationservice/recommendation_server.py"]
