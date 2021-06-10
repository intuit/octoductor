import json
from common import logger
import os
import boto3
import requests
from common import BoardingRequest, get_gateway

logger.info('Setting up function')
survey_link = os.getenv('SURVEYLINK')

servicediscovery = boto3.client('servicediscovery')

def handler(event, context):
    logger.debug("Received event: " + json.dumps(event))
    payload = BoardingRequest(**event)
    logger.info(f'Repository {payload.org}/{payload.repo} onboarded')
    logger.info(f'Payload: {payload}')

    base_url, request_headers = get_gateway()

    resource = "data"
    data_url = f"{base_url}/{resource}/client/"
    print(f"Post to data api on {data_url}")
    data_response = requests.post(data_url, data = payload.to_json() , headers=request_headers)
    print(data_response.status_code)
    print(data_response.text)
    print(data_response.json())
        
    return { "statusCode":200, "body": "success" }
