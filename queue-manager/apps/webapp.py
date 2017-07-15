import datetime
import json
import logging.config
import socket

from flask import Flask, request, jsonify

from apps.taskstore import TaskStore
from conf.appconfig import APP_NAME, WEB, ENQ_REQ_KEYS, DEQ_REQ_KEYS, TASK_ENQUEUE_URI, \
    TASK_DEQUEUE_URI, TASK_UPDATE_URI, UPD_REQ_KEYS
from conf.dbconfig import DATABASE
from conf.logconfig import APP_LOGGING_CFG
from utils.common import TaskQueueInputError, TaskQueueSystemError, TaskQueueEmptyError

logging.config.dictConfig(APP_LOGGING_CFG)

app = Flask(__name__)
appLogger = logging.getLogger(APP_NAME)
webLogger = logging.getLogger(WEB)

taskStore = TaskStore(DATABASE, setup=True)


def validate_enq_req(req):
    appLogger.debug('Received enqueue request: %s', json.dumps(req))
    if not ENQ_REQ_KEYS.issubset(set(req.keys())):
        raise TaskQueueInputError('Required keys missing in enqueue request')
    return req


def validate_deq_req(req):
    appLogger.debug('Received dequeue request: %s', json.dumps(req))
    if not DEQ_REQ_KEYS.issubset(set(req.keys())):
        raise TaskQueueInputError('Required keys missing in dequeue request')
    capabilities = req['capabilities']
    if len(capabilities) == 0:
        raise TaskQueueInputError('Capabilities should not be empty')
    return req


def validate_upd_req(req):
    appLogger.debug('Received update request: %s', json.dumps(req))
    if not UPD_REQ_KEYS.issubset(set(req.keys())):
        raise TaskQueueInputError('Required keys missing in update request')
    if type(req['success']) is not bool:
        raise TaskQueueInputError('Update request success should be boolean')
    return req


def no_tasks(error):
    return app.response_class(
        response=json.dumps({'error': error}),
        status=404,
        mimetype='application/json')


def bad_request(error):
    appLogger.error('User Error: %s', error)
    return app.response_class(
        response=json.dumps({'error': error}),
        status=400,
        mimetype='application/json')


def system_error(error):
    appLogger.error('System Error: %s', error)
    return app.response_class(
        response=json.dumps({'error': error}),
        status=500,
        mimetype='application/json')


def success(task, status=200):
    return app.response_class(
        response=json.dumps(task),
        status=status,
        mimetype='application/json')


@app.route('/')
def index():
    return 'Hallo'


@app.route('/v1/about', methods=['GET'])
def about():
    return jsonify({
        'node': socket.gethostname(),
        'version': '1.0',
        'time': datetime.datetime.now().isoformat()
    })


@app.route(TASK_ENQUEUE_URI, methods=['POST'])
def enqueue():
    try:
        task = validate_enq_req(request.get_json())
        uuid = taskStore.put(task)
        appLogger.info('Created task: %s', uuid)
        task['uuid'] = uuid
        return success(task, status=201)
    except TaskQueueInputError as e:
        return bad_request(str(e))
    except TaskQueueSystemError as e:
        return system_error(str(e))


@app.route(TASK_DEQUEUE_URI, methods=['POST'])
def dequeue():
    try:
        req = validate_deq_req(request.get_json())
        task = taskStore.get(req['capabilities'])
        uuid = task['uuid']
        taskStore.mark_in_progress(uuid)
        return success(task, status=200)
    except TaskQueueInputError as e:
        return bad_request(str(e))
    except TaskQueueEmptyError as e:
        return no_tasks(str(e))


@app.route(TASK_UPDATE_URI, methods=['POST'])
def update():
    try:
        req = validate_upd_req(request.get_json())
        uuid, result, processor = req['uuid'], req['result'], req['processor']
        if req['success']:
            taskStore.mark_complete(uuid, result, processor)
        else:
            taskStore.mark_failed(uuid)
        return success(req, status=200)
    except TaskQueueInputError as e:
        return bad_request(str(e))
    except TaskQueueEmptyError as e:
        return no_tasks(str(e))


@app.after_request
def after(response):
    webLogger.info('%s %s %s %s' % (request.remote_addr, request.method, request.full_path, response.status))
    return response
