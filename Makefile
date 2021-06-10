VERSION?=0.0.0

.PHONY: clean python ui cdk
all: python ui cdk

clean:
	find . -name "node_modules" -type d -prune -print | xargs rm -rf;
	find . -name "package-lock.json" -prune -print | xargs rm;
	find . -name "cdk.out" -type d -prune -print | xargs rm -rf;
	find . -name "yarn.lock" -type d -prune -print | xargs rm -rf;
	find . -type d \( -path ./docs -o -path ./octoductor/ui  \) -prune -false  -o \( -name "*.js" -o -name "*.d.ts" \) -and ! -name "*.config.js" | xargs rm -rf;
	rm -rf .coverage;
	rm -rf .parcel-cache;
	rm -rf octoductor/ui/build;

setup:
	python3 -m venv .env;
	source ./.env/bin/activate

python:
	cd octoductor; \
	pip install ".[test]"; \
	py.test --cov=. --cov-report term-missing --cov-branch --cov-report=xml -rP;

ui:
	cd octoductor/ui; \
	npm install; \
	npx react-scripts build;

cdk:
	npm install
	npx cdk synth > template.yaml;

package:
	npm install
	npm run build
	npm version --no-git-tag-version --allow-same-version $(VERSION)
	npm pack
	pip install --upgrade twine setuptools wheel
	cd octoductor; \
	python setup.py sdist bdist_wheel 
