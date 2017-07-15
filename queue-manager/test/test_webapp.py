import json
import unittest

from apps import webapp
from conf.appconfig import ENQ_REQ_KEYS, TASK_ENQUEUE_URI, TASK_DEQUEUE_URI, TASK_UPDATE_URI
from test.utils import valid_task_as_json, invalid_task_as_json, valid_deq_req_as_json, invalid_deq_req_as_json, \
    empty_deq_req_as_json, valid_upd_req_as_json, invalid_upd_req_as_json


# https://gist.github.com/ivanlmj/dbf29670761cbaed4c5c787d9c9c006b

class WebAppTestCase(unittest.TestCase):
    def setUp(self):
        webapp.app.testing = True
        self.app = webapp.app.test_client()
        webapp.taskStore.cleanup()

    def tearDown(self):
        pass

    def post(self, uri, data):
        return self.app.post(uri, data=data, content_type='application/json')

    def test_server_info(self):
        res = self.app.get('/v1/about')
        self.assertEqual(200, res.status_code)

    def test_server_info_post(self):
        res = self.post('/v1/about', valid_task_as_json())
        self.assertEqual(405, res.status_code)

    def test_enq_invalid_task(self):
        res = self.post(TASK_ENQUEUE_URI, 'invalid-json')
        self.assertEqual(400, res.status_code)
        res = self.post(TASK_ENQUEUE_URI, invalid_task_as_json())
        self.assertEqual(400, res.status_code)

    def test_enq_valid_task(self):
        res = self.post(TASK_ENQUEUE_URI, valid_task_as_json())
        self.assertEqual(201, res.status_code)
        task = json.loads(res.data.decode('utf-8'))
        self.assertTrue(ENQ_REQ_KEYS.issubset(set(task.keys())))
        self.assertTrue('uuid' in task)

    def test_deq_invalid_req(self):
        res = self.post(TASK_DEQUEUE_URI, invalid_deq_req_as_json())
        self.assertEqual(400, res.status_code)

    def test_deq_empty_capabilities_req(self):
        res = self.post(TASK_DEQUEUE_URI, empty_deq_req_as_json())
        self.assertEqual(400, res.status_code)

    def test_deq_on_empty_queue(self):
        res = self.post(TASK_DEQUEUE_URI, valid_deq_req_as_json())
        self.assertEqual(404, res.status_code)

    def test_enq_and_deq(self):
        """
        1. Create a task should return 201 and an UUID
        2. Dequeue request with task name in capabilities should return 200 same task UUID
        3. Next dequeue request with task name in capabilities should return 404
        """
        res = self.post(TASK_ENQUEUE_URI, valid_task_as_json())
        self.assertEqual(201, res.status_code)
        uuid_enq = json.loads(res.data.decode('utf-8'))['uuid']
        res = self.post(TASK_DEQUEUE_URI, valid_deq_req_as_json())
        self.assertEqual(200, res.status_code)
        uuid_deq = json.loads(res.data.decode('utf-8'))['uuid']
        self.assertEqual(uuid_deq, uuid_enq)
        res = self.post(TASK_DEQUEUE_URI, valid_deq_req_as_json())
        self.assertEqual(404, res.status_code)

    def test_enq_deq_complete(self):
        """
        1. Create a task should return 201 and an UUID
        2. Dequeue request with task name in capabilities should return 200 same task UUID
        3. Mark that task as complete should return 200
        4. Next dequeue request with task name in capabilities should return 404
        """
        res = self.post(TASK_ENQUEUE_URI, valid_task_as_json())
        self.assertEqual(201, res.status_code)
        uuid = json.loads(res.data.decode('utf-8'))['uuid']
        res = self.post(TASK_DEQUEUE_URI, valid_deq_req_as_json())
        self.assertEqual(200, res.status_code)
        res = self.post(TASK_UPDATE_URI, valid_upd_req_as_json(uuid))
        self.assertEqual(200, res.status_code)
        res = self.post(TASK_DEQUEUE_URI, valid_deq_req_as_json())
        self.assertEqual(404, res.status_code)

    def test_enq_deq_failed(self):
        """
        1. Create a task should return 201 and an UUID
        2. Dequeue request with task name in capabilities should return 200 same task UUID
        3. Mark that task as failed should return 200
        4. Next dequeue request with task name in capabilities should return 200 same task UUID
        """
        res = self.post(TASK_ENQUEUE_URI, valid_task_as_json())
        self.assertEqual(201, res.status_code)
        uuid_enq = json.loads(res.data.decode('utf-8'))['uuid']
        res = self.post(TASK_DEQUEUE_URI, valid_deq_req_as_json())
        self.assertEqual(200, res.status_code)
        res = self.post(TASK_UPDATE_URI, valid_upd_req_as_json(uuid_enq, False))
        self.assertEqual(200, res.status_code)
        res = self.post(TASK_DEQUEUE_URI, valid_deq_req_as_json())
        self.assertEqual(200, res.status_code)
        uuid_deq = json.loads(res.data.decode('utf-8'))['uuid']
        self.assertEqual(uuid_deq, uuid_enq)

    def test_upd_invalid(self):
        """
        1. Update with invalid request should return 400
        2. Update with invalid UUID as success should return 400
        2. Update with invalid UUID as failure should return 400
        """
        res = self.post(TASK_UPDATE_URI, invalid_upd_req_as_json())
        self.assertEqual(400, res.status_code)
        res = self.post(TASK_UPDATE_URI, valid_upd_req_as_json('calculate-prime-number|1499938282|1'))
        self.assertEqual(400, res.status_code)
        res = self.post(TASK_UPDATE_URI, valid_upd_req_as_json('calculate-prime-number|1499938282|1', False))
        self.assertEqual(400, res.status_code)
