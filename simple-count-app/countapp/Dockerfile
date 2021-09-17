FROM python:alpine
LABEL MAINTAINER="Madhu Akula"

COPY code /app
WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 3000

CMD ["python", "app.py"]