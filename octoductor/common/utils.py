import os
import boto3
import logging
from pybadges import badge
from .dto import ClientEvaluation

log_level = os.getenv('LOG_LEVEL', 'INFO')
logger = logging.getLogger()
logger.setLevel(log_level)
logger.debug('Logger initialized')


def ts() -> str:
    import datetime
    return datetime.datetime.utcnow() \
        .replace(tzinfo=datetime.timezone.utc) \
        .replace(microsecond=0) \
        .isoformat()

def write_text_to_s3(bucket, key, body):
    client = boto3.client('s3')
    response = client.put_object(Body=bytearray(body,"utf-8"), Bucket=bucket, Key=key)
    if response.get("ResponseMetadata").get("HTTPStatusCode") != 200:
        raise ValueError('failed to write to S3. S3 response: {}'.format(response))
    return 'success'

def write_client_evaluations_to_s3(collection: ClientEvaluation, bucket: str, folder_name: str):
    for client in collection:
        client_identifier = client.client_identifier
        client_characteristics = client_identifier.split("/")
        org = client_characteristics[0]
        repo = client_characteristics[1]
        reference = client_characteristics[2]
        file_name_output_keys = ["latest", reference]
        for fn in file_name_output_keys:
            key = "{}/{}/{}/{}.json".format(folder_name, org, repo, fn)
            write_text_to_s3(bucket, key, client.to_json())

def generate_badge(l_txt: str, r_txt: str, l_color: str, r_color: str) -> str:
    # documentation can be found here
    # https://github.com/google/pybadges/blob/1f4de8796e7e0c19723054bccd41c6665e10e0a2/pybadges/__init__.py#L115
    return badge(left_text=l_txt, right_text=r_txt, left_color=l_color, right_color=r_color)
