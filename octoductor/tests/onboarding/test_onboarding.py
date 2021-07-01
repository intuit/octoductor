import unittest
import responses
import json
from unittest.mock import patch
from onboarding import index
from common import BoardingRequest

def gw():
    return 'https://test.com/test-environment', {'x-apigw-api-id': 'gateway_id', 'Content-Type': 'application/json'}

class TestOnboarding(unittest.TestCase):    
    @responses.activate
    @patch('onboarding.index.get_gateway', gw)
    def test_onboarding(self):
        event = BoardingRequest('foo', 'bar', 'sender', 'correlation identifier', 'ts')
        responses.add(responses.POST, 'https://test.com/test-environment/data/client/', json=json.loads(event.to_json()), status=200)
        self.assertEquals(index.handler(event.to_dict(), None), {'statusCode': 200, 'body': 'success'})
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == 'https://test.com/test-environment/data/client/'
        assert responses.calls[0].response.text == event.to_json()
