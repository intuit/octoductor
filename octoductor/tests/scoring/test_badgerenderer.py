import unittest
import json
from unittest.mock import patch, call, Mock
from scoring.badge_generator import index
from common.dto import *
from common import generate_badge, write_text_to_s3

evaluation = Evaluation(Repository("foo", "bar", False),
                0.5, RequirementGroup.STAKEHOLDER, "asset",
                EvaluationStatus.PASS, Badge.SILVER, True
                )

class TestBadgeGenerator(unittest.TestCase):
    def write_badges_to_s3(client_collection: CollectorResponse, bucket: str, folder_name: str) -> None:
        pass

    def write_client_evaluations_to_s3(collection: ClientEvaluation, bucket: str, folder_name: str):
        pass

    @patch('scoring.badge_generator.index.write_badges_to_s3', write_badges_to_s3)
    @patch('scoring.badge_generator.index.write_client_evaluations_to_s3', write_client_evaluations_to_s3)
    def test_gold(self):
        event = CollectorResponse([
            ClientEvaluation('foo/bar/ref', 'sender', Trigger.GH_RELEASE,
            [evaluation],
            'correlation_id', 'ts', 0.75, Badge.GOLD)
        ])

        result = index.handler(event.to_dict(), None)

        badge = result['client_evaluations'][0]['badge_badge_rendered']
        self.assertTrue(badge.startswith('<svg'))
        self.assertTrue(badge.endswith('svg>'))
        self.assertTrue(badge.find('GOLD') > 0)

        score_badge = result['client_evaluations'][0]['score_badge_rendered']
        self.assertTrue(score_badge.startswith('<svg'))
        self.assertTrue(score_badge.endswith('svg>'))
        self.assertTrue(score_badge.find('75%') > 0)

    @patch('scoring.badge_generator.index.write_badges_to_s3', write_badges_to_s3)
    @patch('scoring.badge_generator.index.write_client_evaluations_to_s3', write_client_evaluations_to_s3)
    def test_silver(self):
        event = CollectorResponse([
            ClientEvaluation('foo/bar/ref', 'sender', Trigger.GH_RELEASE,
            [evaluation],
            'correlation_id', 'ts', 0.75, Badge.SILVER)
        ])

        result = index.handler(event.to_dict(), None)

        badge = result['client_evaluations'][0]['badge_badge_rendered']
        self.assertTrue(badge.startswith('<svg'))
        self.assertTrue(badge.endswith('svg>'))
        self.assertTrue(badge.find('SILVER') > 0)
    
    @patch('scoring.badge_generator.index.write_badges_to_s3', write_badges_to_s3)
    @patch('scoring.badge_generator.index.write_client_evaluations_to_s3', write_client_evaluations_to_s3)
    def test_bronze(self):
        event = CollectorResponse([
            ClientEvaluation('foo/bar/ref', 'sender', Trigger.GH_RELEASE,
            [evaluation],
            'correlation_id', 'ts', 0.75, Badge.BRONZE)
        ])

        result = index.handler(event.to_dict(), None)

        badge = result['client_evaluations'][0]['badge_badge_rendered']
        self.assertTrue(badge.startswith('<svg'))
        self.assertTrue(badge.endswith('svg>'))
        self.assertTrue(badge.find('BRONZE') > 0)

    @patch('scoring.badge_generator.index.write_badges_to_s3', write_badges_to_s3)
    @patch('scoring.badge_generator.index.write_client_evaluations_to_s3', write_client_evaluations_to_s3)
    def test_none(self):
        event = CollectorResponse([
            ClientEvaluation('foo/bar/ref', 'sender', Trigger.GH_RELEASE,
            [evaluation],
            'correlation_id', 'ts', 0.75, Badge.NONE)
        ])

        result = index.handler(event.to_dict(), None)

        badge = result['client_evaluations'][0]['badge_badge_rendered']
        self.assertTrue(badge.startswith('<svg'))
        self.assertTrue(badge.endswith('svg>'))
        self.assertTrue(badge.find('NONE') > 0)

    @patch('scoring.badge_generator.index.write_text_to_s3')
    def test_write_badges_to_s3(self, write_text_to_s3):
        response = CollectorResponse([
            ClientEvaluation('foo/bar/ref', 'sender', Trigger.GH_RELEASE,
            [evaluation],
            'correlation_id', 'ts', 0.75, Badge.NONE)
        ])

        result = index.write_badges_to_s3(response, 'super-bucket', 'badge-folder')

        write_text_to_s3.assert_has_calls([
            call('super-bucket', 'badge-folder/foo/bar/latest_rating_badge.svg', ''),
            call('super-bucket', 'badge-folder/foo/bar/ref_rating_badge.svg', ''),
            call('super-bucket', 'badge-folder/foo/bar/latest_score_badge.svg', ''),
            call('super-bucket', 'badge-folder/foo/bar/ref_score_badge.svg', '')
        ])
