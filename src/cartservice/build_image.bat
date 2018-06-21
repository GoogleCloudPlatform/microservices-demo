@echo off

echo building container image for cart service
docker build -t cartservice .

echo running the image, mapping the port
docker run -it --rm -p 5000:8080 --name
