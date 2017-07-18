
# Build Instructions
docker build -t gganesan/taskq-01-stage .
docker run -p 8000:80 -t gganesan/taskq-01-stage:latest
