import unittest
import json
import boto3
from scoring import repo_crawler
from unittest.mock import patch, Mock
from unittest import mock
from moto import mock_secretsmanager
import responses
import requests

from pathlib import Path
p = Path(__file__)


# class TestRepoCrawler(unittest.TestCase):


#     # @responses.activate
#     # @patch('scoring.repo_crawler.index.GITHUB_DOMAIN', 'https://github.awesome-corp.com')
#     # def test_access_token_urls(self):
#     #     with open(p.with_name('installations_1.json'), 'r') as f:
#     #         installations_1 = f.read()
#     #     with open(p.with_name('installations_2.json'), 'r') as f:
#     #         installations_2 = f.read()
#     #     responses.add(
#     #         responses.GET,
#     #         'https://github.awesome-corp.com/app/installations',
#     #         json=json.loads(installations_1),
#     #         headers={ 'Link': '<https://github.awesome-corp.com/app/installations?page=2>; rel="next", <https://github.awesome-corp.com/app/installations?page=2>; rel="last"'},
#     #         status=200
#     #     )
#     #     responses.add(
#     #         responses.GET,
#     #         'https://github.awesome-corp.com/app/installations?page=1',
#     #         json=json.loads(installations_1),
#     #         headers={ 'Link': '<https://github.awesome-corp.com/app/installations?page=2>; rel="next", <https://github.awesome-corp.com/app/installations?page=2>; rel="last"'},
#     #         status=200
#     #     )
#     #     responses.add(
#     #         responses.GET,
#     #         'https://github.awesome-corp.com/app/installations',
#     #         json=json.loads(installations_2),
#     #         headers={ 'Link': '<https://github.awesome-corp.com/app/installations?page=1>; rel="first", <https://github.awesome-corp.com/app/installations?page=1>; rel="prev", <https://github.awesome-corp.com/app/installations?page=2>; rel="last"'},
#     #         status=200
#     #     )

#     #     response = repo_crawler.access_token_urls('bearer')
#     #     expected = {
#     #         'foo-bar': 'https://github.com/api/v3/app/installations/431/access_tokens',
#     #         'barz': 'https://github.com/api/v3/app/installations/424/access_tokens',
#     #         'awesome-repo': 'https://github.com/api/v3/app/installations/423/access_tokens',
#     #         'captain-america': 'https://github.com/api/v3/app/installations/431/access_tokens',
#     #         'ironman': 'https://github.com/api/v3/app/installations/424/access_tokens'
#     #     }
#     #     self.assertEquals(response, expected)
