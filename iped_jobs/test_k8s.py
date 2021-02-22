import unittest
import requests
from kubernetes import client

from .k8s import _addJob

class Test_AddJob(unittest.TestCase):
    def test_addJob(self):
        d  = dict(
            image='a10',
            IPEDJAR='a20',
            EVIDENCE_PATH='a30',
            OUTPUT_PATH='a40',
            IPED_PROFILE='a50',
            ADD_ARGS='a60',
            ADD_PATHS='a70')
        job = _addJob(**d)
        assert job['spec']['template']['spec']['containers'][0]['image'] == d['image']
        # for x in ['IPEDJAR', 'EVIDENCE_PATH', 'OUTPUT_PATH', 'IPED_PROFILE', 'ADD_ARGS', 'ADD_PATHS']:
        #     assert job['spec']['template']['spec']['containers'][0]['env'][x] == d[x]
        