from flask import Flask
from redis import Redis
import os

app = Flask(__name__)
redis_host = os.environ['CACHE_STORE_HOST']
redis = Redis(host=redis_host, port=6379)

@app.route('/')
def main():
    return 'Welcome to Kubernetes 👋 \n Thanks for visiting {} times.'.format(redis.incr('hits'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)