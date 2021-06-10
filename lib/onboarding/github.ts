import { Function, Code, Runtime } from '@aws-cdk/aws-lambda'
import { Construct, Duration } from '@aws-cdk/core';
import {ISecurityGroup, IVpc, SubnetType} from "@aws-cdk/aws-ec2";
import { INamespace } from "@aws-cdk/aws-servicediscovery";
import { PolicyStatement } from '@aws-cdk/aws-iam';
import { ISecret } from '@aws-cdk/aws-secretsmanager';
import { CommonLayerSingleton } from '../common-layer'

export class GitHub extends Function {
  constructor(scope: Construct, id: string, namespace: INamespace, secret: ISecret,
    vpc?: IVpc, securityGroup?: ISecurityGroup,
    memorySize: number = 128, duration: Duration = Duration.seconds(5)) {
    super(scope, id, {
      code: Code.fromInline(`
import serverless_wsgi
import json
from github import app
from common import logger

def handler(event, context):
    logger.warn("Received event: " + json.dumps(event))
    return serverless_wsgi.handle_request(app, event, context)
      
      `),
      memorySize: memorySize,
      timeout: duration,
      vpc: vpc,
      environment: {
        GITHUB_SECRET_ARN: secret.secretArn,
        NAMESPACE: namespace.namespaceName
      },
      runtime: Runtime.PYTHON_3_7,
      handler: 'index.handler',
      layers: [ CommonLayerSingleton.getInstance(scope).getLayer() ],
      vpcSubnets: { subnetType: SubnetType.PRIVATE },
      securityGroup: securityGroup
    });
    secret.grantRead(this.role!)
    this.role!.addToPrincipalPolicy(new PolicyStatement({
      actions: ['servicediscovery:DiscoverInstances'],
      resources: ['*']
    }));
  }
}
