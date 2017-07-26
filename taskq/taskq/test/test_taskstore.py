import logging
import unittest
from logging import config

from apps.taskstore import TaskStore
from conf.dbconfig import TEST_DATABASE
from conf.logconfig import APP_LOGGING_CFG
from test.utils import valid_task_as_dict
from utils.common import TaskQueueInputError, TaskQueueEmptyError

logging.config.dictConfig(APP_LOGGING_CFG)



class TestTaskStore(unittest.TestCase):
    def setUp(self):
        self.taskstore = TaskStore(TEST_DATABASE, setup=True)

    def tearDown(self):
        self.taskstore.destroy()

    def test_empty_queue(self):
        self.assertRaises(TaskQueueEmptyError, self.taskstore.get, ['cook'])

    def test_invalid_capabilities(self):
        self.assertRaises(TaskQueueInputError, self.taskstore.get, [])
        self.assertRaises(TaskQueueInputError, self.taskstore.get, 'wa')
        self.assertRaises(TaskQueueInputError, self.taskstore.get, [0])
        self.assertRaises(TaskQueueInputError, self.taskstore.get, ['ba', 1])

    def test_create_invalid_task(self):
        self.assertRaises(TaskQueueInputError, self.taskstore.put, '--junk--')
        self.assertRaises(TaskQueueInputError, self.taskstore.put, {})

    def test_create_task(self):
        uuid = self.taskstore.put(valid_task_as_dict())
        self.assertEqual('calculate-prime-number', uuid.split('|')[0],
                         'put UUID Should contain task name as first part')

    def test_get_non_existent_task(self):
        self.taskstore.put(valid_task_as_dict())
        self.assertRaises(TaskQueueEmptyError, self.taskstore.get, ['cook'])

    def test_get_task_after_create_task(self):
        uuid = self.taskstore.put(valid_task_as_dict())
        task = self.taskstore.get(['calculate-prime-number'])
        self.assertIsInstance(task, dict, 'get should return a task dict')
        self.assertEqual(task['name'], 'calculate-prime-number', 'name should be calculate-prime-number')
        self.assertEqual(task['schedule'], 1499938282, 'scheduled time should be 1499938282')

    def test_get_after_cleanup(self):
        uuid = self.taskstore.put(valid_task_as_dict())
        self.taskstore.cleanup()
        self.assertRaises(TaskQueueEmptyError, self.taskstore.get, ['calculate-prime-number'])

    def test_check_get_order(self):
        task = valid_task_as_dict()
        task['schedule'] = 1499938582
        self.assertIsNotNone(self.taskstore.put(task))
        self.assertIsNotNone(self.taskstore.put(valid_task_as_dict()))
        task = self.taskstore.get(['calculate-prime-number'])
        self.assertEqual(task['schedule'], 1499938282, 'scheduled time should be 1499938282')

    def test_mark_in_progress_invalid_task(self):
        self.assertRaises(TaskQueueInputError, self.taskstore.mark_in_progress, 'calculate-prime-number|1499938282|1')
        self.assertRaises(TaskQueueInputError, self.taskstore.mark_in_progress, '--junk--')

    def test_mark_in_progress(self):
        uuid = self.taskstore.put(valid_task_as_dict())
        self.taskstore.mark_in_progress(uuid)
        self.assertRaises(TaskQueueEmptyError, self.taskstore.get, ['calculate-prime-number'])

    def test_mark_complete_with_invalid_data(self):
        uuid = self.taskstore.put(valid_task_as_dict())
        self.assertRaises(TaskQueueInputError, self.taskstore.mark_complete, uuid, 'Jack Sparrow', 'Elizabeth Swann')

    def test_mark_complete(self):
        uuid = self.taskstore.put(valid_task_as_dict())
        self.taskstore.mark_complete(uuid, {'result': 'success'}, {'processor': 'intel-core-i7'})
