from common import logger, ts
from .events import Installation, InstallationRepositories, Repository, PullRequestHook, ReleaseHook
import os
import boto3
import requests
from common import dto
from common import api

class Handler:
    def on_installation_repositories(self, delivery: str, payload: InstallationRepositories):
        pass
    def on_installation(self, delivery: str, payload: Installation):
        pass
    def on_ping(self, delivery: str, payload: str):
        pass
    def on_release(self, delivery: str, payload: ReleaseHook):
        pass
    def on_pull_request(self, delivery: str, payload: PullRequestHook):
        pass
    def on_deprecated(self, delivery: str, event: str, payload: str):
        logger.info(f"Ignored deprecated event '{event}'")
    def handle(self, delivery: str, event: str, payload: str):
        deprecated = [
            "integration_installation",
            "integration_installation_repositories"]
        dispatch = {
            "installation_repositories": lambda delivery, payload: self.on_installation_repositories(delivery, InstallationRepositories.from_json(payload)),
            "installation": lambda delivery, payload: self.on_installation(delivery, Installation.from_json(payload)),
            "pull_request": lambda delivery, payload: self.on_pull_request(delivery, PullRequestHook.from_json(payload)),
            "release": lambda delivery, payload: self.on_release(delivery, ReleaseHook.from_json(payload)),
            "ping": self.on_ping
        }
        if event in dispatch:
            dispatch[event](delivery, payload)
        elif event in deprecated:
            self.on_deprecated(delivery, event, payload)
        else:
            logger.info(f"Ignored unsupported event of type {event}")

class OnboardingHandler(Handler):
    def on_installation_repositories(self, delivery: str, installation: InstallationRepositories):
        for repository in installation.repositories_added:
            api.onboard(dto.BoardingRequest(
                repository.full_name.split('/')[0],
                repository.name,
                installation.sender.login,
                delivery,
                ts()))
        for repository in installation.repositories_removed:
            api.offboard(dto.BoardingRequest(
                repository.full_name.split('/')[0],
                repository.name,
                installation.sender.login,
                delivery,
                ts()))

    def on_installation(self, delivery: str, payload: Installation):
        for repository in payload.repositories:
            api.onboard(dto.BoardingRequest(
                repository.full_name.split('/')[0],
                repository.name,
                payload.sender.login,
                delivery,
                ts()))

class EvaluationHandler(Handler):
    def on_release(self, delivery: str, payload: ReleaseHook):
        logger.debug(f"on_release payload '{payload}'")
        api.evaluate(
            dto.EvaluationRequest(
                [dto.Repository(
                    payload.repository.full_name.split('/')[0],
                    payload.repository.name,
                    payload.repository.private,
                    payload.release.tag_name,
                    None,
                    payload.repository.default_branch,
                    payload.repository.language
                )],
                payload.sender.login,
                payload.delivery,
                ts(),
                dto.Trigger.GH_RELEASE
            )
        )
    def on_pull_request(self, delivery: str, payload: PullRequestHook):
        logger.debug(f"on_pull_request payload '{payload}'")
        api.evaluate(
            dto.EvaluationRequest(
                [dto.Repository(
                    payload.repository.full_name.split('/')[0],
                    payload.repository.name,
                    payload.repository.private,
                    payload.pull_request.head.sha,
                    payload.number,
                    payload.repository.default_branch,
                    payload.repository.language
                )],
                payload.sender.login,
                payload.delivery,
                ts(),
                dto.Trigger.GH_PULL_REQUEST
            )
        )
