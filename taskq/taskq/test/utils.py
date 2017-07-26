import json

PROCESSOR = {
    'host': 'mark42.ironman.com',
    'pid': 12345,
    'name': 'Issac Newton'
}


def valid_task_as_dict():
    return {
        'name': 'calculate-prime-number',
        'schedule': 1499938282,
        'config': {
            'algorithm': 'Sieve of Eratosthenes',
            'start': 100,
            'stop': 10000
        }
    }


def valid_deq_req_as_dict():
    return {
        'processor': PROCESSOR,
        'capabilities': ['cook', 'shop', 'calculate-prime-number']
    }


def valid_task_as_json():
    return json.dumps(valid_task_as_dict())


def random_dict_as_json():
    return json.dumps({'name': 'Jack Sparrow', 'occupation': 'Captain', 'vessel': 'The Black Pearl'})


def invalid_task_as_json():
    return random_dict_as_json()


def valid_deq_req_as_json():
    return json.dumps(valid_deq_req_as_dict())


def invalid_deq_req_as_json():
    return random_dict_as_json()


def empty_deq_req_as_json():
    req = valid_deq_req_as_dict()
    req['capabilities'] = []
    return json.dumps(req)


def valid_upd_req_as_json(uuid, success=True):
    return json.dumps({
        'processor': PROCESSOR,
        'result': {
            'name': 'Kim Tae-yeon',
            'occupation': 'K Pop Singer',
            'favourite': True
        },
        'success': success,
        'uuid': uuid
    })


def invalid_upd_req_as_json():
    return random_dict_as_json()
