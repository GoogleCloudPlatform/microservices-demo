# Recommendation Service

This is the recommendation service in Python 2.7

## Local test

start a docker image and run commands to importe requirement and start the app:

```bash
docker run -ti --rm -v $(pwd):/hipstershop python:2.7-slim bash

# install tools
cd /hipstershop/src/recommendationservice
apt-get update -qqy
apt-get -qqy install wget g++ vim netcat
pip install pip-tools

# install python dependencies
pip-compile --output-file=requirements.txt requirements.in
pip install -r requirements.txt

# run the app
python recommendation_server.py
```