FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8089

ENTRYPOINT ["python", "-m", "locust", "-f", "locustfile.py", "--headless", "-u", "10", "-r", "1", "--host=http://frontend:8080"]