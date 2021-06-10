import os
import json
import uuid
import logging
from common import CollectorRequest, EvaluationResponse, ClientEvaluation, CollectorResponse, ts, write_client_evaluations_to_s3

log_level = os.getenv('LOG_LEVEL', 'INFO')
logger = logging.getLogger()
logger.setLevel(log_level)
logger.debug('Loading function')

bucket = os.getenv('BUCKET')

def handler(event, context):
    logger.info("Received event for collection: " + json.dumps(event))
    requests = CollectorRequest.from_dict({"evaluation_responses": event})
    # group requests by asset/repo
    collection = collect_evaluations_by_client(requests)
    collector_response = CollectorResponse(client_evaluations=collection)
    # persist requests
    write_client_evaluations_to_s3(collection, bucket, "collector")
    return json.loads(collector_response.to_json())

def collect_evaluations_by_client(collection: CollectorRequest):
    evaluation_by_client_map = {}  # of type Map[String, Map[String, Any]] where any in this case is either List[Evaluation], String, or Trigger
    for crawler_output in collection.evaluation_responses:
        for evaluation in crawler_output.evaluation:
            repo = evaluation.repository.repo
            org = evaluation.repository.org
            reference = evaluation.repository.reference
            asset_path = str(org + "/" + repo)
            if reference is not None:
                asset_path = str(org + "/" + repo + "/" + reference)
            if evaluation_by_client_map.get(asset_path) is None:
                evaluation_by_client_map[asset_path] = {"sender": crawler_output.sender, "trigger": crawler_output.trigger, "evaluations": []}
                evaluation_by_client_map[asset_path]["evaluations"].append(evaluation)
            else:
                evaluation_by_client_map[asset_path]["evaluations"].append(evaluation)

    out = []
    for client, obj in evaluation_by_client_map.items():
        client_evaluation = ClientEvaluation(
            client_identifier = client,
            evaluation_responses = obj["evaluations"],
            sender = obj["sender"],
            trigger = obj["trigger"],
            correlation_id = str(uuid.uuid4()),
            ts = ts()
        )
        out.append(client_evaluation)

    return out
