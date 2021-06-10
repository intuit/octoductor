import unittest
from github.handlers import *
from pathlib import Path
from common import logger

p = Path(__file__)

class CaptureHandler(Handler):
    delivery: str
    event: str
    payload = None

    def on_installation_repositories(self, delivery: str, payload: InstallationRepositories):
        self.delivery = delivery
        self.event = 'on_installation_repositories'
        self.payload = payload
    def on_installation(self, delivery: str, payload: Installation):
        self.delivery = delivery
        self.event = 'on_installation'
        self.payload = payload
    def on_release(self, delivery: str, payload: ReleaseHook):
        self.delivery = delivery
        self.event = 'on_release'
        self.payload = payload
    def on_pull_request(self, delivery: str, payload: PullRequestHook):
        self.delivery = delivery
        self.event = 'on_pull_request'
        self.payload = payload

class TestGitHubHandlers(unittest.TestCase):
    def test_installation_repositories(self):
        handler = CaptureHandler()
        with open(p.with_name('installation_repositories.json'), 'r') as f:
            handler.handle('1234', 'installation_repositories', f.read())
        
        self.assertEqual(handler.event, 'on_installation_repositories')
        self.assertEqual(handler.delivery, '1234')
        self.assertEqual(type(handler.payload).__name__, 'InstallationRepositories')

    def test_installation(self):
        handler = CaptureHandler()
        with open(p.with_name('installation.json'), 'r') as f:
            handler.handle('1', 'installation', f.read())
        
        self.assertEqual(handler.event, 'on_installation')
        self.assertEqual(handler.delivery, '1')
        self.assertEqual(type(handler.payload).__name__, 'Installation')

    def test_release(self):
        handler = CaptureHandler()
        with open(p.with_name('release.json'), 'r') as f:
            handler.handle('1234', 'release', f.read())
        
        self.assertEqual(handler.event, 'on_release')
        self.assertEqual(handler.delivery, '1234')
        self.assertEqual(type(handler.payload).__name__, 'ReleaseHook')

    def test_pull_request(self):
        handler = CaptureHandler()
        with open(p.with_name('pull_request.json'), 'r') as f:
            handler.handle('1234', 'pull_request', f.read())
        
        self.assertEqual(handler.event, 'on_pull_request')
        self.assertEqual(handler.delivery, '1234')
        self.assertEqual(type(handler.payload).__name__, 'PullRequestHook')
