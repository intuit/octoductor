import re
import sys
import os

from setuptools import setup, find_namespace_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

def readme():
    with open('README.md') as f:
        return f.read()

lint_requires = [
    'pep8',
    'pyflakes'
]

tests_require = [
    'pycodestyle',
    'pydocstyle',
    'pylint',
    'pytest',
    'pytest-cov',
    'pytest-pep8',
    'boto3',
    'moto==1.3.14',
    'python-dateutil',
    'pycryptodome',
    'responses'
]

setup(
    name='intlgntsys-mlservices.octoductor.core',
    version=os.environ['VERSION'] if "VERSION" in os.environ else '0.0.0',
    author='Intuit',
    maintainer='Intuit',
    author_email='Tech-Intuit-AI-octoductor@intuit.com',
    url='https://github.com/intuit/octoductor',
    description=('Octoductor orchestrates multiple GitHub checks into a single evaluation workflow based on AWS serverless technologies.'),
    license="MIT",
    long_description=readme(),
    packages=find_namespace_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]
    ),
    install_requires=requirements,
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
        'dev': ['boto3']
    },
    include_package_data=True,
    python_requires=">=3.7",
)
