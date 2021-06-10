import jwt
import os
from common import logger, EvaluationRequest, EvaluationResponse
import requests
import json, yaml
import boto3
import base64
from datetime import datetime
from common import github, exceptions

from common import EvaluationRequest, Evaluation, EvaluationResponse, EvaluationStatus, Badge, Repository, RequirementGroup, Trigger

BUCKET = os.getenv('S3_BUCKET')
REQUIREMENT= os.getenv('REQUIREMENT')

def doublewrite(org_repo, file, contents):
    boto3.client("s3") \
        .put_object(
            Body=contents,
            Bucket=BUCKET,
            Key=f"u/{org_repo}/{file}"
        )

    boto3.client("s3") \
        .put_object(
            Body=json.dumps(yaml.safe_load(contents)),
            Bucket=BUCKET,
            Key=f"u/{org_repo}/{file.replace('.yaml', '.json')}"
        )

def do_that_yaml_thing(repos_by_org, trigger, file, default_status = EvaluationStatus.NA):
    bearer = github.bearer_token()
    token_urls = github.access_token_urls(bearer)
    evaluations = []

    for org, repos_references in repos_by_org.items():
        token = github.convert_bearer_to_access(bearer, token_urls[org])
        for repo_reference in repos_references:
            org_repo = f"{org}/{repo_reference['repo']}"
            try:
                content_of_file = github.download_file(token, org_repo, file, repo_reference['reference'])
            except exceptions.Error:
                evaluations.append(Evaluation(
                    repository=Repository(org, repo_reference['repo'], False, reference=repo_reference['reference']),
                    score=.0,
                    requirement_group=RequirementGroup.ENGINEERING,
                    requirement=REQUIREMENT,
                    status=default_status, badge=Badge.NONE, gh_check=True, blob=""))
            else:
                if trigger == Trigger.GH_RELEASE:
                    doublewrite(org_repo, file, content_of_file)

                evaluations.append(Evaluation(
                    repository=Repository(org, repo_reference['repo'], False, reference=repo_reference['reference']),
                    score=100.0,
                    requirement_group=RequirementGroup.ENGINEERING,
                    requirement=REQUIREMENT,
                    status=EvaluationStatus.PASS, badge=Badge.GOLD, gh_check=True, blob=""))
            finally:
                logger.info(f"Ran eval for {org_repo}")

        return evaluations
