import os
import logging
import boto3
from flask import Flask, jsonify, render_template, request, abort
from datetime import datetime
from common import Client, BoardingRequest

db_name = os.getenv('DB_NAME')
db_cluster_arn = os.getenv('DB_CLUSTER_ARN')
db_credentials = os.getenv('DB_CREDENTIALS_ARN')
log_level = os.getenv('LOG_LEVEL', 'INFO')
resource = os.getenv('RESOURCE', 'data')

logger = logging.getLogger()
logger.setLevel(log_level)

rds = boto3.client('rds-data')

logger.info('Loading function')

app = Flask(__name__)

def execute_statement(sql, params: list = []):
    logger.debug(f'Running SQL statement: {sql}')
    return rds.execute_statement(
            secretArn=db_credentials,
            database=db_name,
            resourceArn=db_cluster_arn,
            sql=sql,
            parameters=params
        )

@app.route(f'/{resource}/client', methods=['POST'])
@app.route(f'/{resource}/client/', methods=['POST'])
def onboard_client():
    try:
        payload = BoardingRequest.from_json(request.data)
    except KeyError:
        abort(400, 'Invalid payload.')
    try:
        parsedTs = datetime.fromisoformat(payload.ts)
    except ValueError:
        abort(400, 'Timestamp needs to be in ISO 8601 format.')
    if not payload.org:
        abort(400, 'Organization needs to be defined.')
    if not payload.repo:
        abort(400, 'Repository needs to be defined.')
    if not payload.sender:
        abort(400, 'Sender needs to be defined.')
    if not payload.correlation_id:
        abort(400, 'correlation_id needs to be defined.')
    if not payload.ts:
        abort(400, 'ts needs to be defined.')

    sql = """
            INSERT INTO clients (org, repo, onboarded_by, correlation_id, ts)
            VALUES (:org, :repo, :onboarded_by, :correlation_id, TO_TIMESTAMP(:ts, 'YYYY-MM-DD HH24:MI:SS'))
            ON CONFLICT (org, repo) DO UPDATE
            SET onboarded_by = :onboarded_by, correlation_id = :correlation_id, ts = TO_TIMESTAMP(:ts, 'YYYY-MM-DD HH24:MI:SS')
          """
    sql_parameters = [
        {'name':'org', 'value':{'stringValue': payload.org}},
        {'name':'repo', 'value':{'stringValue': payload.repo}},
        {'name':'onboarded_by', 'value':{'stringValue': payload.sender}},
        {'name':'correlation_id', 'value':{'stringValue': payload.correlation_id}},
        {'name':'ts', 'value':{'stringValue': parsedTs.strftime("%Y-%m-%d %H:%M:%S")}}
    ]
    response = execute_statement(sql, sql_parameters)
    logger.debug(f"{response['numberOfRecordsUpdated']} records updated.")

    sql = """
            INSERT INTO clients_audit (actn, org, repo, onboarded_by, correlation_id, ts)
            VALUES (:action, :org, :repo, :onboarded_by, :correlation_id, TO_TIMESTAMP(:ts, 'YYYY-MM-DD HH24:MI:SS'))
            ON CONFLICT (correlation_id, org, repo) DO UPDATE
            SET onboarded_by = :onboarded_by, actn='POST', ts = TO_TIMESTAMP(:ts, 'YYYY-MM-DD HH24:MI:SS')
          """
    sql_parameters = [
        {'name':'action', 'value':{'stringValue': 'POST'}},
        {'name':'org', 'value':{'stringValue': payload.org}},
        {'name':'repo', 'value':{'stringValue': payload.repo}},
        {'name':'onboarded_by', 'value':{'stringValue': payload.sender}},
        {'name':'correlation_id', 'value':{'stringValue': payload.correlation_id}},
        {'name':'ts', 'value':{'stringValue': parsedTs.strftime("%Y-%m-%d %H:%M:%S")}}
    ]
    response = execute_statement(sql, sql_parameters)
    logger.debug(f"{response['numberOfRecordsUpdated']} records updated.")

    logger.info(f'Repository {payload.org}/{payload.repo} onboarded')
    return { "statusCode": 200 }

@app.route(f'/{resource}/client/<org>/<repo>', methods=['DELETE'])
def remove_client(org: str, repo: str):
    logger.info(f"DELETE {request.data}")
    abort(501)
    return { "statusCode": 200 }

def readRecord(record):
    """
    Records are expected to look like the following:
    [{'stringValue': 'foo'}, {'stringValue': 'bar'}, {'stringValue': '2020-11-28 04:27:02'}]
    """
    return Client(org=record[0]['stringValue'], repo=record[1]['stringValue'], ts=record[2]['stringValue'])

@app.route(f'/{resource}/client/<org>/<repo>')
def retrieve_client(org: str, repo: str):
    sql = 'SELECT org, repo, ts FROM clients WHERE org=:org AND repo=:repo'
    sql_parameters = [{'name':'org', 'value':{'stringValue': org}},
                      {'name':'repo', 'value':{'stringValue': repo}}]
    response = execute_statement(sql, sql_parameters)
    records = response['records']
    if not records:
        abort(404)

    # Found records. Due to primary key lookup, result size is 1
    return readRecord(records[0]).to_json()

@app.route(f'/{resource}/client/<org>')
def retrieve_client_by_org(org: str):
    sql = 'SELECT org, repo, ts FROM clients WHERE org=:org'
    sql_parameters = [{'name':'org', 'value':{'stringValue': org}}]
    response = execute_statement(sql, sql_parameters)
    records = response['records']
    if not records:
        return "[ ]"

    # Found records.
    clients = [readRecord(record) for record in records]
    return f"[ {', '.join(list(map(lambda x: x.to_json(), clients)))} ]"

@app.route(f'/{resource}/client/')
def retrieve_all_clients():
    sql = 'SELECT org, repo, ts FROM clients'
    response = execute_statement(sql)
    records = response['records']
    if not records:
        return "[ ]"

    # Found records.
    clients = [readRecord(record) for record in records]
    return f"[ {', '.join(list(map(lambda x: x.to_json(), clients)))} ]"

@app.route(f'/{resource}/score/<org>/<repo>', methods=['POST'])
def score(org: str, repo: str):
    print(f'Results for score: {org}/{repo}')
    abort(501)
    return request.data
