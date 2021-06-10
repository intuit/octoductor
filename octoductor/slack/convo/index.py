import os
import json
import boto3
import logging
import urllib.request
from urllib.error import URLError, HTTPError

slack_bot_token_arn = os.getenv('SLACK_BOT_TOKEN_ARN')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_secret():
    secretsmanager = boto3.client('secretsmanager')
    logger.info('Retrieving Slack secrets from {}'.format(slack_bot_token_arn))
    secret_response = secretsmanager.get_secret_value(SecretId=slack_bot_token_arn)
    secret_value = json.loads(secret_response['SecretString'])
    return secret_value['slackToken']


"""
add_request_headers adds HTTP headers to request object.
"""
def add_request_headers(request, bot_token):
    request.add_header("Content-Type", "application/json")
    request.add_header("Accept-Charset", "utf-8")
    request.add_header("Authorization", "Bearer " + bot_token)


"""
Build request
@:param channel_id
@:param slack_text
"""
def build_request(channel_id, slack_text):
    slack_url = "https://slack.com/api/chat.postMessage"
    payload = {'channel': channel_id, 'text': slack_text}
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(slack_url, data=data, method="POST")
    return request


"""
Compose slack post message. 
Channel id for channel begins with #. Channel id for user begins with @. 
@:returns http response
"""


def slack_post_message(bot_token, channel_id, slack_text):
    # Build request object.
    request = build_request(channel_id, slack_text)
    # Add request headers.
    add_request_headers(request, bot_token)

    # Fire off the request!
    response = urllib.request.urlopen(request).read()
    logger.info(response)
    return response


slack_bot_token = get_secret()

def handler(event, context):

    logger.info(f"Received event:\n{json.dumps(event)}\nWith context:\n{context}")

    body = event.get('body', None)

    if body is None:
        raise ValueError('event body must be present and must be of type string. Please check your input event.')

    if isinstance(body, list):
        parsed_events = body
    else:
        parsed_events = json.loads(body)

    if not(isinstance(parsed_events, list)):
        err_mssg = 'event body must contain a list of objects ({channel: <>, slacktext: <>}). Please check your input event.'
        logger.error(err_mssg)
        return {"body": json.dumps(err_mssg), "statusCode": 400}

    errors = False
    error_payloads = []
    for payload in parsed_events:
        target = payload.get("channel", None)
        slack_text = payload.get("slacktext", None)

        if target is None:
            raise ValueError('event target must be present and must be of type string. Please check your input event.')
        if slack_text is None:
            raise ValueError('event slack_text must be present and must be of type string. Please check your input event.')

        # invoke slack post message
        try:
            response = slack_post_message(slack_bot_token, target, slack_text)
        except HTTPError as e:
            errors = True
            error_message_http = "Request failed: {} {}".format(e.code, e.reason)
            logger.error(error_message_http)
            error_payloads.append(error_message_http)
        except URLError as e:
            errors = True
            error_message_url = "Server connection failed: {}".format(e.reason)
            logger.error(error_message_url)
            error_payloads.append(error_message_url)

    body = {"body": json.dumps(error_payloads)}
    if errors:
        body["statusCode"] = 500
    else:
        body["statusCode"] = 200


    return body
