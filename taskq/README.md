
# Build Instructions

## Build docker image
```bash
docker build -t gganesan/taskq-01-stage .
```
## Run docker image
```bash
docker run -d -p 8000:80 -t gganesan/taskq-01-stage:latest
```
