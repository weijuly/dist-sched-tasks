import os
import socket

TASK_REQUEST_URL = 'http://10.239.63.42:8000/v1/tasks/dequeue'
TASK_UPDATE_URL = 'http://10.239.63.42:8000/v1/tasks/update'
APP_NAME = 'processor'
CONTROL_FILE = 'control/app.control'
PROCESSOR = {
    'host': socket.gethostname(),
    'pid': os.getpid(),
    'name': 'Issac Newton'
}
HEADERS = {
    'Content-Type': 'application/json'
}
