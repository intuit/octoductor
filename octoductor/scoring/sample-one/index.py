import json
import uuid
from common import EvaluationRequest, Evaluation, EvaluationResponse, EvaluationStatus, Badge, Repository, RequirementGroup
print('Loading function')

def handler(event, context):
    print("Received event for sample one: " + json.dumps(event))
    request = EvaluationRequest.from_dict(event)
    repo = request.repositories[0]
    evaluation = Evaluation(repository=repo, score=100.0, requirement_group=RequirementGroup.ENGINEERING, requirement="sample-one", status=EvaluationStatus.PASS, badge=Badge.GOLD, gh_check=False, blob="")
    eval_response = EvaluationResponse(evaluation=[evaluation], sender=request.sender, trigger=request.trigger, correlation_id=str(uuid.uuid4()), ts=request.ts)
    ## this is an ugly way to transform enums into a serializable dictionary
    out = json.loads(eval_response.to_json())
    return out
