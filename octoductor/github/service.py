import os
import boto3
import serverless_wsgi
import json
import logging
import requests
import hmac

from flask import Flask, jsonify, render_template, request, abort
from markupsafe import escape
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import List
from common import logger
from .handlers import OnboardingHandler, EvaluationHandler

resource = os.getenv('RESOURCE', 'github')
secret_arn = os.getenv('GITHUB_SECRET_ARN')

app = Flask(__name__)

def get_secrets():
    secretsmanager = boto3.client('secretsmanager')
    logger.info(f'Retrieving GitHub secrets from {secret_arn}')
    secret_response = secretsmanager.get_secret_value(SecretId=secret_arn)
    secret_value = json.loads(secret_response['SecretString'])
    return secret_value['secret'], secret_value['key']

def match_webhook_secret(request):
    secret, _ = get_secrets()
    if ('X-Hub-Signature' in request.headers and
        request.headers.get('X-Hub-Signature') is not None):
        header_signature = request.headers.get('X-Hub-Signature', None)
    else:
        abort(403, 'X-Hub-Signature header missing.')
    sha_name, signature = header_signature.split('=')
    if sha_name != 'sha1':
        abort(501)

    mac = hmac.new(secret.encode(),
                    msg=request.data,
                    digestmod="sha1")

    if not hmac.compare_digest(str(mac.hexdigest()), str(signature)):
        abort(403, 'Signature mismatch')
        
    logger.debug(mac.hexdigest())
    logger.debug(request.headers.get('X-Hub-Signature'))

@app.route(f'/{resource}/hook', methods=['POST'])
@app.route(f'/{resource}/hook/', methods=['POST'])
def hook():
    logger.info(f"Request Headers:\n{request.headers}")

    match_webhook_secret(request)

    event = request.headers["X-GitHub-Event"]
    delivery = request.headers["X-GitHub-Delivery"]

    for handler in [OnboardingHandler(), EvaluationHandler()]:
        handler.handle(delivery, event, request.data)

    response = {
        "statusCode": 200
    }

    return response; 
