
import unittest

from common.dto import *

class TestDTOs(unittest.TestCase):
    
    def test_repository(self):
        assert Repository("foo", "bar", True).to_json() == '{"org": "foo", "repo": "bar", "private": true, "reference": null, "pull_request_number": null, "default_branch": null, "language": null}'

    def test_evaluation(self):
        evaluation = Evaluation(Repository("foo", "bar", False), 0.5, RequirementGroup.STAKEHOLDER, "asset", EvaluationStatus.PASS, Badge.SILVER, True)
        self.assertEqual(evaluation, evaluation.from_json(evaluation.to_json()))
