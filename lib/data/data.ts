import { Construct, Duration } from '@aws-cdk/core';
import { Function, Code, Runtime } from '@aws-cdk/aws-lambda';
import { ISecurityGroup, IVpc, SubnetType } from "@aws-cdk/aws-ec2";
import { ClusterConnection } from '../cluster-connection'
import { CommonLayerSingleton } from '../common-layer'
import { PolicyStatement } from '@aws-cdk/aws-iam';

export class Data extends Function {
  constructor(scope: Construct, id: string, connection: ClusterConnection,
    vpc?: IVpc, securityGroup?: ISecurityGroup, logLevel: string = 'INFO',
    resource: string = 'data', memorySize: number = 128, duration: Duration = Duration.seconds(5)) {
    super(scope, id, {
      code: Code.fromInline(`
import serverless_wsgi
import json
from data.api import app
from common import logger

def handler(event, context):
    logger.debug("Received event: " + json.dumps(event))
    return serverless_wsgi.handle_request(app, event, context)
      
      `),
      memorySize: memorySize,
      timeout: duration,
      vpc: vpc,
      layers: [ CommonLayerSingleton.getInstance(scope).getLayer() ],
      environment: {
        DB_CLUSTER_ARN: connection.clusterArn,
        DB_CREDENTIALS_ARN: connection.credentials.secretArn,
        DB_NAME: connection.database,
        LOG_LEVEL: logLevel,
        RESOURCE: resource
    },
      vpcSubnets: { subnetType: SubnetType.PRIVATE },
      securityGroup: securityGroup,
      runtime: Runtime.PYTHON_3_7,
      handler: 'index.handler'
    });

    connection.credentials.grantRead(this)
    this.role!.addToPrincipalPolicy(new PolicyStatement({
        actions: ['rds-data:*'],
        resources: [connection.clusterArn]
    }))
  }
}
