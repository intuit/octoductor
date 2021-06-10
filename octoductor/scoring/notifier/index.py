import os
import json
import requests
import logging
from common import CollectorResponse, get_gateway

log_level = os.getenv('LOG_LEVEL', 'INFO')
logger = logging.getLogger()
logger.setLevel(log_level)
logger.debug('Loading function')

def handler(event, context):
    logger.info("Received event for relay: " + json.dumps(event))
    scored_clients = CollectorResponse.from_dict(event)

    base_url, request_headers = get_gateway()

    request_headers['charset'] = 'utf-8'

    resource = "slackconvo"
    slack_url = f"{base_url}/{resource}"

    slack_results_to_clients(scored_clients, slack_url, request_headers)

    return json.loads(scored_clients.to_json())

def slack_results_to_clients(request: CollectorResponse, slack_url: str, headers) -> None:
    messages = []
    for client in request.client_evaluations:
        sender = client.sender
        score = client.global_score
        badge = client.global_badge.name
        message = format_message(sender, score, badge)
        messages.append(message)

    slack_response = requests.post(slack_url,
                                   data=json.dumps(messages),
                                   headers=headers)
    if str(slack_response.status_code) != "200":
        raise ValueError('slack post request failed with error: {}'.format(slack_response.text))


def format_message(sender: str, score: str, badge: str) -> dict:
    slack_message = {
        "slacktext": "Congratulations! Your awesome octoductor score is *{}*, and you have earned a *{}* badge!".format(score, badge),
        "channel": "@{}".format(sender),
    }
    return slack_message
