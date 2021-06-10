import jwt
import os
from common import logger, EvaluationRequest, EvaluationResponse
import requests
import json
import boto3
import base64
from datetime import datetime
from common import exceptions

PEM = os.getenv('GITHUB_SECRET')
BUCKET = os.getenv('S3_BUCKET')
GITHUB_DOMAIN = os.getenv('GITHUB_DOMAIN')
APPLICATION_ID = os.getenv('APPLICATION_ID')

def bearer_token():
    secretsmanager = boto3.client('secretsmanager')
    read_secret = secretsmanager.get_secret_value(SecretId=PEM)
    read_secret = json.loads(read_secret['SecretString'])
    pem = read_secret["key"]

    logger.info('Read certificate')
    payload = {
        'iat': int(datetime.now().timestamp()),
        'exp': int(datetime.now().timestamp())+600,
        'iss': APPLICATION_ID
    }
    logger.info('Encoding certificate')
    encoded = jwt.encode(payload, base64.b64decode(pem), algorithm="RS256")
    logger.info(f"Encode JWT:\n {encoded}")
    return encoded

def convert_bearer_to_access(bearer, access_tokens_url):
    headers = {
        "Accept": 'application/vnd.github.machine-man-preview+json, application/vnd.github.v3+json',
        'Authorization': f"Bearer {bearer}",
    }
    logger.info("Convert Bearer token to access token")
    response = requests.post(access_tokens_url, headers=headers)
    if response.status_code != 200:
        logger.error("Convert Bearer token to access token request failed!")
        raise exceptions.RequestFailed("Convert Bearer token to access token request failed with the following exception: {}".format(response))
    return response.json()["token"]


def access_token_urls(bearer):
    result = {}
    page_num = 1
    headers = {
        'Authorization': f"Bearer {bearer}",
        'Accept': 'application/vnd.github.machine-man-preview+json, application/vnd.github.v3+json',
    }
    URL = f"{GITHUB_DOMAIN}/app/installations"
    logger.info(f"Requesting Installations: {URL}")

    while True:
        response = requests.get(f"{URL}?page={page_num}", headers=headers)
        if response.status_code != 200:
            logger.error("Access token request failed!")
            raise exceptions.RequestFailed("Access token request failed with exception: {}".format(response))

        for installation in response.json():
            org = installation['account']['login']
            result[org] = installation['access_tokens_url']
        page_num += 1

        if 'next' not in response.links:
            break

    logger.info(f"Number of installations found {len(result)}")
    return result

def download_file(a_token, org_repo, file, reference = 'master'):
    headers = {
        "Accept": 'application/vnd.github.v3+json',
        'Authorization': f"Bearer {a_token}"
    }
    logger.info(f"Request asset.yaml from {org_repo}")
    response = requests.get(
        f"{GITHUB_DOMAIN}/repos/{org_repo}/contents/{file}",
        params={'ref': reference},
        headers=headers)
    if response.status_code != 200:
        raise exceptions.FileNotFoundError("File does not exist")
    path = response.json()["download_url"]
    return requests.get(path).content
