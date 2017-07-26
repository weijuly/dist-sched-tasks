JOB_SERVER = 'tcp://*:55555'
APP_NAME = 'task_server'
WEB = 'web'
CONTROL_FILE = 'control/app.control'

ENQ_REQ_KEYS = {'name', 'schedule', 'config'}
DEQ_REQ_KEYS = {'processor', 'capabilities'}
UPD_REQ_KEYS = {'processor', 'result', 'success', 'uuid'}

TASK_ENQUEUE_URI = '/v1/tasks/enqueue'
TASK_DEQUEUE_URI = '/v1/tasks/dequeue'
TASK_UPDATE_URI = '/v1/tasks/update'
