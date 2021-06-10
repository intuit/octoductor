from pydantic.dataclasses import dataclass
from dataclasses import field
from dataclasses_json import dataclass_json
from typing import List

@dataclass_json
@dataclass
class Sender:
    login: str
    avatar_url: str
    url: str
    html_url: str
    followers_url: str
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: str
    organizations_url: str
    repos_url: str
    events_url: str
    received_events_url: str
    type: str

@dataclass_json
@dataclass
class Webhook:
    """
    https://docs.github.com/en/free-pro-team@latest/developers/webhooks-and-events/webhook-events-and-payloads#webhook-payload-object-common-properties
    """
    action: str = ''
    sender: Sender = None
    event: str = ''
    delivery: str = ''

@dataclass_json
@dataclass
class Repository:
    name: str
    full_name: str
    private: bool
    default_branch: str = None
    language: str = None

@dataclass_json
@dataclass
class Installation(Webhook):
    """
    https://docs.github.com/en/free-pro-team@latest/developers/webhooks-and-events/webhook-events-and-payloads#installation
    """
    repositories: List[Repository] = field(default_factory=list)
    event: str = 'installation'

@dataclass_json
@dataclass
class InstallationRepositories(Webhook):
    """
    https://docs.github.com/en/free-pro-team@latest/developers/webhooks-and-events/webhook-events-and-payloads#installation_repositories
    """
    repositories_added: List[Repository] = field(default_factory=list)
    repositories_removed: List[Repository] = field(default_factory=list)
    event: str = 'installation_repositories'

@dataclass_json
@dataclass
class Release:
    tag_name: str
    zipball_url: str
    created_at: str
    published_at: str
    prerelease: bool

@dataclass_json
@dataclass
class ReleaseHook(Webhook):
    repository: Repository = None
    release: Release = None

@dataclass_json
@dataclass
class Reference:
    sha: str
    ref: str
    repo: Repository

@dataclass_json
@dataclass
class PullRequest:
    title: str
    state: str
    head: Reference
    base: Reference
    closed_at: str = None
    updated_at: str = None
    merged_at: str = None

@dataclass_json
@dataclass
class PullRequestHook(Webhook):
    number: int = None
    repository: Repository = None
    pull_request: PullRequest = None
