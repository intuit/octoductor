import os
import json
import time
import logging
from common import CollectorResponse, Badge, generate_badge, write_text_to_s3
from common.utils import write_client_evaluations_to_s3

log_level = os.getenv('LOG_LEVEL', 'INFO')
logger = logging.getLogger()
logger.setLevel(log_level)
logger.debug('Loading function')

bucket = os.getenv('BUCKET')

def handler(event, context):

    logger.info('Received the following event: {}'.format(json.dumps(event)))
    # transform event to entity
    scored_clients = CollectorResponse.from_dict(event)

    left_badge_color = "#454545"
    left_text = "octoductor"
    # generate svg badges
    for client in scored_clients.client_evaluations:
        client_badge = client.global_badge
        client_score = client.global_score
        if client_badge == Badge.GOLD:
            badge = generate_badge(left_text, "GOLD", left_badge_color, "gold")
            score_badge = generate_badge(left_text, "{}%".format(client_score), left_badge_color, "gold")
        elif client_badge == Badge.SILVER:
            badge = generate_badge(left_text, "SILVER", left_badge_color, "silver")
            score_badge = generate_badge(left_text, "{}%".format(client_score), left_badge_color, "silver")
        elif client_badge == Badge.BRONZE:
            badge = generate_badge(left_text, "BRONZE", left_badge_color, "#9e6605")
            score_badge = generate_badge(left_text, "{}%".format(client_score), left_badge_color, "#9e6605")
        else:
            badge = generate_badge(left_text, "NONE", left_badge_color, "gray")
            score_badge = generate_badge(left_text, "{}%".format(client_score), left_badge_color, "gray")
        client.set_rendered_badge(badge)
        client.set_rendered_score_badge(score_badge)

    write_badges_to_s3(scored_clients, bucket, "badges")
    write_client_evaluations_to_s3(scored_clients.client_evaluations, bucket, "badge_generator")
    return json.loads(scored_clients.to_json())

def write_badges_to_s3(client_collection: CollectorResponse, bucket: str, folder_name: str) -> None:
    for client in client_collection.client_evaluations:
        score_badge = client.score_badge_rendered
        badge = client.badge_badge_rendered
        client_identifier = client.client_identifier
        client_characteristics = client_identifier.split("/")
        org = client_characteristics[0]
        repo = client_characteristics[1]
        reference = client_characteristics[2]
        badge_types = {"rating": badge, "score": score_badge}
        for ty, bdg in badge_types.items():
            for fn in ["latest", reference]:
                key = "{}/{}/{}/{}_{}_badge.svg".format(folder_name, org, repo, fn, ty)
                write_text_to_s3(bucket, key, bdg)
    return "success"
