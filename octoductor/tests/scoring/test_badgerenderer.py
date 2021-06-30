import unittest
import json
from unittest.mock import patch, Mock
from scoring.badge_generator import index
from common.dto import *
from common import generate_badge, write_text_to_s3

class TestBadgeGenerator(unittest.TestCase):
    def write_badges_to_s3(client_collection: CollectorResponse, bucket: str, folder_name: str) -> None:
        pass

    def write_client_evaluations_to_s3(collection: ClientEvaluation, bucket: str, folder_name: str):
        pass

    @patch('scoring.badge_generator.index.write_badges_to_s3', write_badges_to_s3)
    @patch('scoring.badge_generator.index.write_client_evaluations_to_s3', write_client_evaluations_to_s3)
    def test_handler(self):
        event = CollectorResponse([
            ClientEvaluation('foo/bar/ref', 'sender', Trigger.GH_RELEASE, [Evaluation(Repository("foo", "bar", False), 0.5, RequirementGroup.STAKEHOLDER, "asset", EvaluationStatus.PASS, Badge.SILVER, True)],
            'correlation_id', 'ts', 0.75, Badge.GOLD)
        ])

        result = index.handler(event.to_dict(), None)
        badge = result['client_evaluations'][0]['badge_badge_rendered']
        self.assertTrue(badge.startswith('<svg'))
        self.assertTrue(badge.endswith('svg>'))
        self.assertTrue(badge.find('GOLD') > 0)
