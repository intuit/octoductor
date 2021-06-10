
import unittest
from github.events import *
from pathlib import Path

p = Path(__file__)

class TestGitHubEvents(unittest.TestCase):
    
    def test_installation(self):
        '''https://docs.github.com/en/developers/webhooks-and-events/webhook-events-and-payloads#webhook-payload-example-13'''
        with open(p.with_name('installation.json'), 'r') as f:
            installation = Installation.from_json(f.read())

        self.assertEqual(installation.repositories, [Repository('Hello-World', 'octocat/Hello-World', False)])
        self.assertEqual(installation.action, 'deleted')

    def test_installation_repositories(self):
        '''https://docs.github.com/en/developers/webhooks-and-events/webhook-events-and-payloads#webhook-payload-example-14'''
        with open(p.with_name('installation_repositories.json'), 'r') as f:
            installation = InstallationRepositories.from_json(f.read())

        self.assertEqual(installation.repositories_added, [Repository('Space', 'Codertocat/Space', False)])
        self.assertEqual(installation.repositories_removed, [])

    def test_release(self):
        '''https://docs.github.com/en/developers/webhooks-and-events/webhook-events-and-payloads#webhook-payload-example-34'''
        with open(p.with_name('release.json'), 'r') as f:
            release = ReleaseHook.from_json(f.read())

        self.assertEqual(release.repository,
         Repository('Hello-World', 'Codertocat/Hello-World', False, 'master', 'Ruby'))
        self.assertEqual(release.release.tag_name, '0.0.1')

    def test_pull_reequest(self):
        '''https://docs.github.com/en/developers/webhooks-and-events/webhook-events-and-payloads#webhook-payload-example-30'''
        with open(p.with_name('pull_request.json'), 'r') as f:
            request = PullRequestHook.from_json(f.read())

        self.assertEqual(request.repository, Repository('Hello-World', 'Codertocat/Hello-World', False, 'master'))
        self.assertEqual(request.number, 2)
        self.assertEqual(request.pull_request.state, 'open')
        self.assertEqual(request.pull_request.head.sha, 'ec26c3e57ca3a959ca5aad62de7213c562f8c821')
        self.assertEqual(request.pull_request.base.sha, 'f95f852bd8fca8fcc58a9a2d6c842781e32a215e')
