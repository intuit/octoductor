import os
import boto3
import json
import logging
from string import Template
from botocore.config import Config

print('Setting up function')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

database_name = os.getenv('DB_NAME')
db_cluster_arn = os.getenv('DB_CLUSTER_ARN')
db_credentials_admin_arn = os.getenv('DB_ADMIN_CREDENTIALS_ARN')
db_credentials_read_arn = os.getenv('DB_READ_CREDENTIALS_ARN')
db_credentials_write_arn = os.getenv('DB_WRITE_CREDENTIALS_ARN')

logger.info(f"DB {database_name}, cluster {db_cluster_arn}, credentials {db_credentials_admin_arn}")

class SqlTemplate(Template):
    delimiter = '@'

def ddl_statement(ddl: str, params: dict = {}):
    rds = boto3.client('rds-data')

    logger.info(f'Running DDL statement: {ddl}')

    sql_template = SqlTemplate(ddl)
    sql = sql_template.substitute(**params)

    try:
        response = rds.execute_statement(
            secretArn=db_credentials_admin_arn,
            database=database_name,
            resourceArn=db_cluster_arn,
            sql=sql,
            continueAfterTimeout=True
        )
    except rds.exceptions.StatementTimeoutException as e:
        logger.warn("Query timed out: " + e.response)
        response = e.response
    return response

def await_connection(event, context):
    config = Config(
       retries = {
          'max_attempts': 10,
          'mode': 'standard'
       }
    )
    rds = boto3.client('rds-data', config=config)

    logging.info("Trying to establish a connection")
    rds.execute_statement(
            secretArn=db_credentials_admin_arn,
            database=database_name,
            resourceArn=db_cluster_arn,
            sql="SELECT 1;")
    logging.info("Connected successfully to serverless cluster")

def users(event, context):
    secretsmanager = boto3.client('secretsmanager')

    logging.info(f'Retrieving read secret from {db_credentials_read_arn}')
    read_secret = secretsmanager.get_secret_value(SecretId=db_credentials_read_arn)
    read_secret = json.loads(read_secret['SecretString'])
    
    logging.info(f'Retrieving write secret from {db_credentials_write_arn}')
    write_secret = secretsmanager.get_secret_value(SecretId=db_credentials_write_arn)
    write_secret = json.loads(write_secret['SecretString'])

    with open('create_user.sql', 'r') as ddl_script:
        ddl_script_content = ddl_script.read()

        logging.info(f'Creating user {read_secret["username"]}')
        params = {"user": read_secret["username"], "password": read_secret["password"]}
        response = ddl_statement(ddl_script_content, params)
        logging.info(response)

        logging.info(f'Creating user {write_secret["username"]}')
        params = {"user": write_secret["username"], "password": write_secret["password"]}
        response = ddl_statement(ddl_script_content, params)
        logging.info(response)

    with open('list_users.sql', 'r') as ddl_script:
        ddl_script_content=ddl_script.read()
        response = ddl_statement(ddl_script_content)
        return {"status": "success", "message": json.dumps(response)}

    return {"status": "fail", "message": "Unable to execute users DDL statements. Please check logs for more details."}

def tables(event, context):    
    with open('create_tables.sql', 'r') as ddl_script:
        ddl_script_content=ddl_script.read()
        response = ddl_statement(ddl_script_content)
        logging.info(response)

    with open('list_tables.sql', 'r') as ddl_script:
        ddl_script_content=ddl_script.read()
        response = ddl_statement(ddl_script_content)
        return {"status": "success", "message": json.dumps(response)}

    return {"status": "fail", "message": "Unable to execute tables DDL statements. Please check logs for more details."}

def access(event, context):
    secretsmanager = boto3.client('secretsmanager')

    with open('read_access.sql', 'r') as ddl_script:
        ddl_script_content=ddl_script.read()

        logging.info(f'Retrieving read secret from {db_credentials_read_arn}')
        read_secret = secretsmanager.get_secret_value(SecretId=db_credentials_read_arn)
        read_secret = json.loads(read_secret['SecretString'])

        logging.info(f'Granting read-only access to {read_secret["username"]}')
        response = ddl_statement(ddl_script_content, {"user": read_secret["username"]})
        logging.info(response)

    with open('write_access.sql', 'r') as ddl_script:
        ddl_script_content=ddl_script.read()

        logging.info(f'Retrieving write secret from {db_credentials_write_arn}')
        write_secret = secretsmanager.get_secret_value(SecretId=db_credentials_write_arn)
        write_secret = json.loads(write_secret['SecretString'])

        logging.info(f'Granting read/write access to {write_secret["username"]}')
        response = ddl_statement(ddl_script_content, {"user": write_secret["username"]})
        logging.info(response)

    with open('list_users.sql', 'r') as ddl_script:
        ddl_script_content=ddl_script.read()
        response = ddl_statement(ddl_script_content)
        return {"status": "success", "message": json.dumps(response)}

    return {"status": "fail", "message": "Unable to execute access DDL statements. Please check logs for more details."}
