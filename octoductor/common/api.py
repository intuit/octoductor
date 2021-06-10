from common import logger, BoardingRequest, ts, EvaluationRequest, exceptions
import os
import boto3
import requests

namespace = os.getenv('NAMESPACE')
def get_gateway():
    servicediscovery = boto3.client('servicediscovery')
    response = servicediscovery.discover_instances(
        NamespaceName=namespace,
        ServiceName='private-gateway'
    )
    gateway_id = response['Instances'][0]['InstanceId']
    stage = response['Instances'][0]['Attributes']['stage']
    logger.info(f"Gateway identifier: {gateway_id}")
    logger.info(f"Stage: {stage}")

    response = servicediscovery.discover_instances(
        NamespaceName=namespace,
        ServiceName='vpc-endpoint'
    )

    endpoint_id = response['Instances'][0]['InstanceId']
    logger.info(f"VPC endpoint identifier: {endpoint_id}")

    dns = response['Instances'][0]['Attributes']['dns']
    logger.info(f"DNS : {dns}")

    return f"https://{dns}/{stage}", {'x-apigw-api-id': gateway_id, 'Content-Type': 'application/json'}

def onboard(client: BoardingRequest):
    base_url, header = get_gateway()
    resource = "onboarding-workflow"
    url = f"{base_url}/{resource}"
    response = requests.post(url, data = client.to_json(), headers=header)
    if response.status_code != 200:
        logger.error("Failed to onboard client!")
        raise exceptions.RequestFailed("Failed to onboard client with exception: {}".format(response))
    logger.info(f"Sent {client.org}/{client.repo} to onboarding flow, got response {response}")

# TODO
def offboard(client: BoardingRequest):
    base_url, header = get_gateway()
    resource = "onboarding-workflow"
    logger.warn(f"{client.org}/{client.repo} wants to offboard, not implemented yet")
    # url = f"{base_url}/{resource}"
    # response = requests.delete(url, data = client.to_json(), headers=header)
    # logger.info(f"Sent {client.org}/{client.repo} to onboarding flow, got response {response}")

def evaluate(evaluation: EvaluationRequest):
    base_url, header = get_gateway()
    resource = "evaluation"
    url = f"{base_url}/{resource}"
    response = requests.post(url, data = evaluation.to_json(), headers=header)
    if response.status_code != 200:
        logger.error("Failed to evaluate!")
        raise exceptions.RequestFailed("Failed to evaluate with exception: {}".format(response))
    logger.info(f"Sent {evaluation.repositories} for evaluation  ({response})")
