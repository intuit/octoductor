# Contributing

When contributing to this repository, please first discuss the change you wish to make via issue,
email, or any other method with the owners of this repository before making a change.

Please note we have a code of conduct, please follow it in all your interactions with the project.

## Pull Request Process

1. Ensure any install or build dependencies are removed before the end of the layer when doing a
   build.
2. Create or update the README.md with details of changes to the interface, this includes new environment
   variables, exposed ports, useful file locations and container parameters.
3. Increase the version numbers in any examples files and the README.md to the new version that this
   Pull Request would represent. The versioning scheme we use is [SemVer](http://semver.org/).
4. You may merge the Pull Request in once you have the sign-off from the owners of the project, or if you
   do not have permission to do that, you may request the second reviewer to merge it for you.

## Contribute Functionality

The community is encouraged to contribute "crawlers" to Octoductor in order to enable new engineering quality checks. These crawlers are effectively AWS Lambda
functions wired  in Octoductor's [evaluation flow](octoductor/lib/evaluation/evaluation-flow.ts).

Contributors should place the function inside the [octoductor](octoductor/octoductor/) folder, while the AWS lambda construct should be placed inside the [lib](octoductor/lib/) folder. 

Each function should have associated tests. Once the function is added, the crawler can be enabled by adding the new lambda construct to [PythonEvaluatorGenerator](octoductor/lib/deployment/cdk-stack.ts).

Lastly, please contact us at `Tech-Intuit-AI-octoductor@intuit.com` before proposing more radical changes to Octoductor. These changes will be evaluated and approved on a case by case basis.

## Creating a New Crawler
```
# Run yeoman to see Octoductor contribution templates.
$ yo octoductor
yo octoductor:infra-module	Bootstrap a generic infrastructure module
yo octoductor:python-lambda	Skaffold a Lambda function written in Python
yo octoductor:nodejs-lambda	Skaffold a Lambda function leveraging Node.js
```
Follow instructions in newly generated module folder to get started.
