import os
import json
import logging
from common import CollectorResponse, ClientEvaluation, EvaluationStatus, Badge, write_client_evaluations_to_s3

log_level = os.getenv('LOG_LEVEL', 'INFO')
logger = logging.getLogger()
logger.setLevel(log_level)
logger.debug('Loading function')

bucket = os.getenv('BUCKET')

def handler(event, context):

    logger.info('Received the following event: {}'.format(json.dumps(event)))
    # transform event to entity
    collector_response = CollectorResponse.from_dict(event)
    # generate global score by client
    scored_result = score_generator(collector_response)
    # write results to S3
    write_client_evaluations_to_s3(scored_result.client_evaluations, bucket, "score-generator")

    return json.loads(scored_result.to_json())

def score_generator(collection: CollectorResponse):
    # iterate through clients
    for client in collection.client_evaluations:
        # extract raw evaluation results
        raw_results_by_req_group = extract_raw_results_by_requirement(client)
        # summarize raw evaluation results by requirement group
        final_results_by_req = summarize_results_by_requirement(raw_results_by_req_group)

        req_scores = []
        req_badges = []
        for req, res in final_results_by_req.items():
            group_score = res.get("req_group_score")
            group_badge = res.get("req_group_badge")
            if group_score is not None:
                req_scores.append(group_score)
            if group_badge is not None:
                req_badges.append(group_badge)

        client.set_global_score(round(sum(req_scores)/float(len(req_scores)),2))
        client.set_global_badge(Badge(int(sum(req_badges)/float(len(req_badges)))))
        client.set_blob(json.dumps(final_results_by_req))

    return collection

def extract_raw_results_by_requirement(client_evaluation):
    raw_results_by_req_group = {}
    # iterate through each evaluation by client
    for evaluation in client_evaluation.evaluation_responses:
        group = evaluation.requirement_group
        status = evaluation.status
        badge = evaluation.badge
        score = evaluation.score
        if raw_results_by_req_group.get(group) is None:
            if status != EvaluationStatus.NA:
                raw_results_by_req_group[group] = { "statuses": [status], "badges": [badge], "scores": [score] }
            else:
                raw_results_by_req_group[group] = { "statuses": [], "badges": [badge], "scores": [score] }
        else:
            if status != EvaluationStatus.NA:
                raw_results_by_req_group[group]["statuses"].append(status)
            raw_results_by_req_group[group]["badges"].append(badge)
            raw_results_by_req_group[group]["scores"].append(score)
    return raw_results_by_req_group

def summarize_results_by_requirement(raw_results_by_req_group):
    final_results_by_req = {}
    for req, res in raw_results_by_req_group.items():
        f_score = 0.0
        f_badge = Badge.NONE
        f_status = EvaluationStatus.NA
        for k, v in res.items():
            assert(isinstance(v, list))
            l = len(v)
            s = sum(v)
            mean = s/float(l)
            if k == "scores":
                f_score = round(mean,1)
            elif k == "badges":
                f_badge = Badge(int(mean))
            else:
                f_status = EvaluationStatus(int(mean))
        final_results_by_req[req] = { "req_group_score": f_score, "req_group_badge": f_badge, "req_group_status": f_status }
    return final_results_by_req
