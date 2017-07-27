FROM python:3
COPY ./scheduler /scheduler
RUN pip3 install schedule
WORKDIR /scheduler
CMD [ "python", "scheduler.py" ]
