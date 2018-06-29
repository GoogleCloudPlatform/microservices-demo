FROM python:3

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
ENTRYPOINT locust --host="http://${FRONTEND_ADDR}" --no-web -c=10
