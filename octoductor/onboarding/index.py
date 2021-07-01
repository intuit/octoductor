import json
from common import logger
import os
import boto3
import requests
from common import BoardingRequest, get_gateway

logger.info('Setting up function')
survey_link = os.getenv('SURVEYLINK')

def handler(event, context):
    logger.debug("Received event: " + json.dumps(event))
    payload = BoardingRequest(**event)
    base_url, request_headers = get_gateway()
    resource = "data"
    data_url = f"{base_url}/{resource}/client/"
    data_response = requests.post(data_url, data = payload.to_json(), headers=request_headers)
    return { "statusCode":200, "body": "success" }
