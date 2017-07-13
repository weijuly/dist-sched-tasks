from apps.taskstore import TaskStore, TaskStoreError
import unittest
import logging
from logging import config

from conf.dbconfig import TEST_DATABASE
from conf.logconfig import LOGGING_CFG

logging.config.dictConfig(LOGGING_CFG)


def generate_task():
    return {
        'name': 'calculate-prime-number',
        'schedule': 1499938282,
        'config': {
            'algorithm': 'Sieve of Eratosthenes',
            'start': 100,
            'stop': 10000
        }
    }


class TestTaskStore(unittest.TestCase):
    def setUp(self):
        self.taskstore = TaskStore(TEST_DATABASE, setup=True)

    def tearDown(self):
        self.taskstore.destroy()

    def test_empty_queue(self):
        self.assertRaises(TaskStoreError, self.taskstore.get, ['cook'])

    def test_invalid_capabilities(self):
        self.assertRaises(TaskStoreError, self.taskstore.get, [])
        self.assertRaises(TaskStoreError, self.taskstore.get, 'wa')
        self.assertRaises(TaskStoreError, self.taskstore.get, [0])
        self.assertRaises(TaskStoreError, self.taskstore.get, ['ba', 1])

    def test_create_invalid_task(self):
        self.assertRaises(TaskStoreError, self.taskstore.put, '--junk--')
        self.assertRaises(TaskStoreError, self.taskstore.put, {})

    def test_create_task(self):
        uuid = self.taskstore.put(generate_task())
        self.assertEqual('calculate-prime-number', uuid.split('|')[0],
                         'put UUID Should contain task name as first part')

    def test_get_non_existent_task(self):
        self.taskstore.put(generate_task())
        self.assertRaises(TaskStoreError, self.taskstore.get, ['cook'])

    def test_get_task_after_create_task(self):
        uuid = self.taskstore.put(generate_task())
        task = self.taskstore.get(['calculate-prime-number'])
        self.assertIsInstance(task, dict, 'get should return a task dict')
        self.assertEqual(task['name'], 'calculate-prime-number', 'name should be calculate-prime-number')
        self.assertEqual(task['schedule'], 1499938282, 'scheduled time should be 1499938282')

    def test_get_after_cleanup(self):
        uuid = self.taskstore.put(generate_task())
        self.taskstore.cleanup()
        self.assertRaises(TaskStoreError, self.taskstore.get, ['calculate-prime-number'])

    def test_check_get_order(self):
        task = generate_task()
        task['schedule'] = 1499938582
        self.assertIsNotNone(self.taskstore.put(task))
        self.assertIsNotNone(self.taskstore.put(generate_task()))
        task = self.taskstore.get(['calculate-prime-number'])
        self.assertEqual(task['schedule'], 1499938282, 'scheduled time should be 1499938282')

    def test_mark_in_progress_invalid_task(self):
        self.assertRaises(TaskStoreError, self.taskstore.mark_in_progress, 'calculate-prime-number|1499938282|1')
        self.assertRaises(TaskStoreError, self.taskstore.mark_in_progress, '--junk--')

    def test_mark_in_progress(self):
        uuid = self.taskstore.put(generate_task())
        self.taskstore.mark_in_progress(uuid)
        self.assertRaises(TaskStoreError, self.taskstore.get, ['calculate-prime-number'])

    def test_mark_complete_with_invalid_data(self):
        uuid = self.taskstore.put(generate_task())
        self.assertRaises(TaskStoreError, self.taskstore.mark_complete, uuid, 'Jack Sparrow', 'Elizabeth Swann')

    def test_mark_complete(self):
        uuid = self.taskstore.put(generate_task())
        self.taskstore.mark_complete(uuid, {'result': 'success'}, {'processor': 'intel-core-i7'})
