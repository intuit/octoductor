import unittest, json, boto3, base64, jwt
from common import github, utils
from unittest.mock import patch, Mock
from moto import mock_secretsmanager
import unittest
import json
import boto3
from unittest.mock import patch, Mock
from unittest import mock
from moto import mock_secretsmanager
import responses
import requests

from pathlib import Path
p = Path(__file__)

from Cryptodome.PublicKey import RSA

key = RSA.generate(2048)

class TestGithub(unittest.TestCase):
    @patch('common.github.PEM', 'pem-arn')
    @patch('common.github.APPLICATION_ID', 1234)
    @mock_secretsmanager
    def test_bearer_token(self):
        boto3.client("secretsmanager", region_name="us-west-2") \
            .create_secret(
                Name="pem-arn",
                SecretString=json.dumps({"key": base64.b64encode(key.exportKey()).decode('utf-8')})
            )
        result = github.bearer_token()
        decoded = jwt.decode(result, key.publickey().exportKey(), algorithms=["RS256"])

        self.assertEqual(1234, decoded['iss'])

    @responses.activate
    def test_convert_bearer_to_access(self):
        tokens_url = 'https://github.awesome-corp.com/api/v3/app/installations/42/access_tokens'
        with open(p.with_name('access_tokens.json'), 'r') as f:
            access_tokens = f.read()
        responses.add(responses.POST, tokens_url, json=json.loads(access_tokens), status=200)
        token = github.convert_bearer_to_access('bearer', tokens_url)
        self.assertEqual('atoken', token)
    
    @responses.activate
    @patch('common.github.GITHUB_DOMAIN', 'https://github.awesome-corp.com')
    def test_access_token_urls(self):
        with open(p.with_name('installations_1.json'), 'r') as f:
            installations_1 = f.read()
        with open(p.with_name('installations_2.json'), 'r') as f:
            installations_2 = f.read()
        responses.add(
            responses.GET,
            'https://github.awesome-corp.com/app/installations',
            json=json.loads(installations_1),
            headers={ 'Link': '<https://github.awesome-corp.com/app/installations?page=2>; rel="next", <https://github.awesome-corp.com/app/installations?page=2>; rel="last"'},
            status=200
        )
        responses.add(
            responses.GET,
            'https://github.awesome-corp.com/app/installations?page=1',
            json=json.loads(installations_1),
            headers={ 'Link': '<https://github.awesome-corp.com/app/installations?page=2>; rel="next", <https://github.awesome-corp.com/app/installations?page=2>; rel="last"'},
            status=200
        )
        responses.add(
            responses.GET,
            'https://github.awesome-corp.com/app/installations',
            json=json.loads(installations_2),
            headers={ 'Link': '<https://github.awesome-corp.com/app/installations?page=1>; rel="first", <https://github.awesome-corp.com/app/installations?page=1>; rel="prev", <https://github.awesome-corp.com/app/installations?page=2>; rel="last"'},
            status=200
        )

        response = github.access_token_urls('bearer')
        expected = {
            'foo-bar': 'https://github.com/api/v3/app/installations/431/access_tokens',
            'barz': 'https://github.com/api/v3/app/installations/424/access_tokens',
            'awesome-repo': 'https://github.com/api/v3/app/installations/423/access_tokens',
            'captain-america': 'https://github.com/api/v3/app/installations/431/access_tokens',
            'ironman': 'https://github.com/api/v3/app/installations/424/access_tokens'
        }
        self.assertEquals(response, expected)

    @responses.activate
    @patch('common.github.GITHUB_DOMAIN', 'https://github.awesome-corp.com')
    def test_download_file(self):
        responses.add(
            responses.GET,
            'https://github.awesome-corp.com/repos/foo/bar/contents/file.txt?ref=v0.42.0',
            json=json.loads("""
            {
                "type": "file",
                "encoding": "base64",
                "size": 5362,
                "name": "file.txt",
                "path": "file.txt",
                "content": "encoded content ...",
                "sha": "3d21ec53a331a6f037a91c368710b99387d012c1",
                "url": "https://api.github.awesome-corp.com/repos/foo/bar/contents/file.txt",
                "git_url": "https://api.github.awesome-corp.com/repos/foo/bar/git/blobs/v0.42.0",
                "html_url": "https://github.awesome-corp.com/foo/bar/blob/master/file.txt",
                "download_url": "https://raw.github.awesome-corp.com/foo/bar/master/file.txt",
                "_links": {
                    "git": "https://api.github.awesome-corp.com/repos/foo/bar/git/blobs/v0.42.0",
                    "self": "https://api.github.awesome-corp.com/repos/foo/bar/contents/file.txt",
                    "html": "https://github.awesome-corp.com/foo/bar/blob/master/file.txt"
                }
            }
            """),
            status=200
        )
        responses.add(
            responses.GET,
            'https://raw.github.awesome-corp.com/foo/bar/master/file.txt',
            body="Hello world",
            status=200
        )

        content_of_file = github.download_file('token', 'foo/bar', 'file.txt', 'v0.42.0')
        self.assertEquals(content_of_file.decode('utf-8'), "Hello world")

    @responses.activate
    @patch('common.github.GITHUB_DOMAIN', 'https://github.awesome-corp.com')
    def test_download_file_fail(self):
        responses.add(
            responses.GET,
            'https://github.awesome-corp.com/repos/foo/bar/contents/file.txt?ref=v0.42.0',
            status=404
        )
        with self.assertRaises(Exception) as context:
            github.download_file('token', 'foo/bar', 'file.txt', 'v0.42.0')

        self.assertTrue('File does not exist' in str(context.exception))
